from core.database import db
from core.models.Review import Review
from core.models.ReviewAudit import ReviewAudit
from core.models.User import User
from core.models.Site import Site
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any


from sqlalchemy import func, desc, asc


class ReviewService:
    """
    Servicio para gestionar las operaciones de moderación de reseñas.
    """

    @staticmethod
    def get_review_by_id(review_id: int) -> Optional[Review]:
        """Busca una reseña por su ID primario."""
        return db.session.get(Review, review_id)


    @staticmethod
    def get_reviews_paginated(
        page: int = 1, 
        per_page: int = 25,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = 'created_at',
        sorted_by: str = 'desc'
    ) -> dict:
        """
        Recupera reseñas paginadas con filtros y ordenamiento.
        """

        filters = filters or {}
        
        # 1. Construir la consulta base (Unir con Site)
        # Añado el filtro de borrado lógico al Site
        query = db.session.query(Review).join(Site).filter(Site.deleted == False)
        # 2. Aplicar Filtros (Combinables)
        
        # Estado (Pendiente/Aprobada/Rechazada)
        status = filters.get('status')
        if status and status in ['Pendiente', 'Aprobada', 'Rechazada']:
            query = query.filter(Review.status == status)
        
        # Sitio (site_id)
        site_id = filters.get('site_id')
        if site_id is not None:
            query = query.filter(Review.site_id == site_id)
            
        # Calificación (Rango 1-5)
        min_rating = filters.get('min_rating')
        max_rating = filters.get('max_rating')
        if min_rating is not None and 1 <= min_rating <= 5:
            query = query.filter(Review.rating >= min_rating)
        if max_rating is not None and 1 <= max_rating <= 5:
            query = query.filter(Review.rating <= max_rating)
        
        # Fecha (Rango desde/hasta)
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')
        if date_from:
            query = query.filter(Review.created_at >= date_from)
        if date_to:
            # Incluir hasta el final del día
            query = query.filter(Review.created_at < date_to + timedelta(days=1)) 

        # Usuario (email - Búsqueda parcial)
        user_email = filters.get('user_email')
        if user_email:
            query = query.filter(func.lower(Review.user_email).like(f'%{user_email.lower()}%'))
        # 3. Aplicar Ordenamiento
        order_column = None
        if order_by == 'created_at':
            order_column = Review.created_at
        elif order_by == 'rating':
            order_column = Review.rating
        elif order_by == 'site_name': 
            order_column = Site.site_name
        
        if order_column:
            direction = asc if sorted_by == 'asc' else desc
            query = query.order_by(direction(order_column))
            
        # Paginación
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # 4. Preparar filtros para el template (deben ser strings)
        display_filters = {}
        for k, v in filters.items():
             if v is not None:
                if isinstance(v, datetime):
                    display_filters[k] = v.strftime('%Y-%m-%d')
                else:
                    display_filters[k] = str(v)
        
        return {
            'reviews': pagination.items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num,
            'page_range': list(range(max(1, page-2), min(pagination.pages+1, page+3))),
            # Parámetros de ordenamiento
            'order_by': order_by, 
            'sorted_by': sorted_by, 
            # El diccionario de filtros actual (para rellenar el formulario)
            'current_filters': display_filters
        }

    @staticmethod
    def approve_review(review_id: int, moderator_id: int, description: str = "Reseña aprobada") -> bool:
        """
        Aprueba una reseña cambiando su estado a 'Aprobada'.
        
        Args:
            review_id: ID de la reseña a aprobar
            moderator_id: ID del moderador que aprueba
            description: Descripción de la acción
        
        Returns:
            True si se aprobó exitosamente, False en caso contrario
        """
        try:
            review = ReviewService.get_review_by_id(review_id)
            if not review:
                return False

            # Cambiar estado de la reseña
            review.status = 'Aprobada'
            review.updated_at = datetime.now(timezone.utc)

            # Crear auditoría
            audit = ReviewAudit(
                review_id=review_id,
                user_id=moderator_id,
                action_type='APPROVE',
                description=description,
                details=f"Reseña aprobada por moderador {moderator_id}"
            )

            db.session.add(audit)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            return False

    @staticmethod
    def reject_review(review_id: int, moderator_id: int, rejection_reason: str, description: str = "Reseña rechazada") -> bool:
        """
        Rechaza una reseña cambiando su estado a 'Rechazada'.
        
        Args:
            review_id: ID de la reseña a rechazar
            moderator_id: ID del moderador que rechaza
            rejection_reason: Motivo del rechazo (máx. 200 caracteres)
            description: Descripción de la acción
        
        Returns:
            True si se rechazó exitosamente, False en caso contrario
        """
        try:
            if len(rejection_reason) > 200:
                return False

            review = ReviewService.get_review_by_id(review_id)
            if not review:
                return False

            # Cambiar estado de la reseña
            review.status = 'Rechazada'
            review.updated_at = datetime.now(timezone.utc)
            review.rejection_reason = rejection_reason

            # Crear auditoría
            audit = ReviewAudit(
                review_id=review_id,
                user_id=moderator_id,
                action_type='REJECT',
                description=description,
                details=f"Reseña rechazada por moderador {moderator_id}. Motivo: {rejection_reason}"
            )

            db.session.add(audit)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            return False

    @staticmethod
    def delete_review(review_id: int) -> bool:
        """
        Elimina una reseña definitivamente.
        NO se crea auditoría porque la reseña se borra de la BD.
        
        Args:
            review_id: ID de la reseña a eliminar
        
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        try:
            # Buscar la reseña
            review = db.session.query(Review).filter_by(id=review_id).first()
            if not review:
                return False

            # Eliminar primero las auditorías asociadas
            from core.models.ReviewAudit import ReviewAudit
            db.session.query(ReviewAudit).filter_by(review_id=review_id).delete()
            
            # Eliminar la reseña
            db.session.delete(review)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            return False
        
    #--------------------------------------------------------

    @staticmethod
    def create_review_from_api(site_id: int, user_id: int, rating: int, text: str) -> Review:
        """
        Crea una nueva reseña desde la API pública.
        La reseña queda en estado 'Pendiente' para moderación.
        """
        try:
            # 1. Validar que el sitio existe y no está eliminado
            site = db.session.get(Site, site_id)
            if not site or site.deleted:
                raise ValueError("El sitio no existe o fue eliminado")
            
            # 2. Validar que el usuario existe
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError("El usuario no existe")
            
            # 3. Verificar si ya existe una reseña de este usuario para este sitio
            # ⚠️ CAMBIO AQUÍ: Buscar por user_email en vez de user_id
            existing = db.session.query(Review).filter_by(
                site_id=site_id, 
                user_email=user.email  # ← CAMBIO: usar email en vez de user_id
            ).first()
            
            if existing:
                raise ValueError("Ya existe una reseña tuya para este sitio")
            
            # 4. Validar rating (debe ser 1-5)
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                raise ValueError("Rating inválido (debe ser 1-5)")
            
            # 5. Validar texto
            if not text or not isinstance(text, str):
                raise ValueError("El texto es obligatorio")
            
            text = text.strip()
            if len(text) < 20 or len(text) > 1000:
                raise ValueError(f"El texto debe tener entre 20 y 1000 caracteres (actual: {len(text)})")
            
            # 6. Crear la reseña
            # ⚠️ CAMBIO AQUÍ: Quité user_id, solo uso user_email
            review = Review(
                site_id=site_id,
                user_email=user.email,  # ← Solo guardamos el email
                rating=rating,
                content=text,
                status='Pendiente',
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db.session.add(review)
            db.session.commit()
            
            print(f"✅ Reseña creada exitosamente: ID={review.id}, Site={site_id}, User={user.email}")
            
            return review
            
        except ValueError as e:
            # Re-lanzar errores de validación
            raise e
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear reseña: {e}")
            raise Exception(f"Error al guardar la reseña: {str(e)}")

    #--------------------------------------------------------

    @staticmethod
    def get_approved_reviews_by_user_paginated(
        user_id: int,
        page: int = 1,
        per_page: int = 10,
        sort_by: str = 'created_at',
        order: str = 'desc'
    ) -> dict:
        """
        Obtiene las reseñas APROBADAS de un usuario con paginación.
        """
        from core.utils.pagination import paginate_query
        
        # Construir query
        query = db.session.query(Review)\
            .filter(Review.user_id == user_id, Review.status == 'Aprobada')
        
        # Ordenamiento
        order_column = Review.rating if sort_by == 'rating' else Review.created_at
        query = query.order_by(
            order_column.desc() if order == 'desc' else order_column.asc()
        )
        
        # Paginar
        return paginate_query(query, page, per_page)