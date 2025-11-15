from core.database import db
from core.models.Review import Review
from core.models.ReviewAudit import ReviewAudit
from core.models.User import User
from core.models.Site import Site
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime


class ReviewService:
    """
    Servicio para gestionar las operaciones de moderación de reseñas.
    """

    @staticmethod
    def get_review_by_id(review_id: int) -> Optional[Review]:
        """Busca una reseña por su ID primario."""
        return db.session.get(Review, review_id)

    @staticmethod
    def get_reviews_paginated(page: int = 1, per_page: int = 25) -> dict:
        """
        Recupera reseñas paginadas.
        
        Args:
            page: Número de página (default: 1)
            per_page: Elementos por página (default: 25)
        
        Returns:
            Dict con información de paginación
        """
        
        query = db.session.query(Review)

        # Paginación
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            'reviews': pagination.items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num,
            'page_range': list(range(max(1, page-2), min(pagination.pages+1, page+3)))
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
        

    @staticmethod
    def get_approved_reviews_by_user(user_id: int) -> List[Review]:
        """
        Obtiene solo las reseñas APROBADAS de un usuario específico.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            List[Review]: Lista de reseñas aprobadas del usuario
        """
        from core.models.Review import Review
        from core.database import db
        
        reviews = db.session.execute(
            db.select(Review)
            .filter_by(user_id=user_id, status='approved')
            .order_by(Review.created_at.desc())
        ).scalars().all()
        
        return reviews