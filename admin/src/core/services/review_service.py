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
    def get_all_reviews() -> List[Review]:
        """Recupera todas las reseñas con información del sitio."""
        return db.session.query(Review).options(
            joinedload(Review.site)
        ).all()

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
            print(f"Error al aprobar reseña: {e}")
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
            print(f"Error al rechazar reseña: {e}")
            return False

    @staticmethod
    def delete_review(review_id: int, moderator_id: int, description: str = "Reseña eliminada") -> bool:
        """
        Elimina una reseña definitivamente.
        
        Args:
            review_id: ID de la reseña a eliminar
            moderator_id: ID del moderador que elimina
            description: Descripción de la acción
        
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        try:
            review = ReviewService.get_review_by_id(review_id)
            if not review:
                return False

            # Crear auditoría antes de eliminar
            audit = ReviewAudit(
                review_id=review_id,
                user_id=moderator_id,
                action_type='DELETE',
                description=description,
                details=f"Reseña eliminada por moderador {moderator_id}"
            )

            db.session.add(audit)
            db.session.delete(review)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar reseña: {e}")
            return False
