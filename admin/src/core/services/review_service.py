from core.database import db
from core.models.Review import Review
from core.models.ReviewAudit import ReviewAudit
from core.models.User import User
from core.models.Site import Site
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime, timedelta
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
