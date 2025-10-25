from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.models.Review import Review
from core.models.ReviewAudit import ReviewAudit
from core.database import db
from core.services.review_service import ReviewService
from src.web.handlers.auth import login_required, require_role
from sqlalchemy.orm import joinedload


reviews_blueprint = Blueprint("reviews", __name__, url_prefix="/reviews")


@reviews_blueprint.route("/", methods=["GET", "POST"])
@login_required
@require_role(['Moderador', 'Editor', 'Administrador'])
def index():
    """
    Controlador principal para la moderación de reseñas.
    
    GET: Muestra la lista de reseñas
    POST: Procesa acciones de moderación (aprobar/rechazar/eliminar)
    """
    if request.method == "POST":
        action = request.form.get("action")
        review_id = request.form.get("review_id")
        rejection_reason = request.form.get("rejection_reason", "").strip()
        
        # Validaciones básicas
        if not action or not review_id:
            flash("Faltan parámetros obligatorios", "error")
            return redirect(url_for('reviews.index'))
        
        try:
            review_id = int(review_id)
            moderator_id = session.get("user_id")
            
            if action == "approve":
                success = ReviewService.approve_review(
                    review_id=review_id,
                    moderator_id=moderator_id,
                    description="Reseña aprobada desde panel de moderación"
                )
                if success:
                    flash("Reseña aprobada exitosamente", "success")
                else:
                    flash("Error al aprobar la reseña", "error")
                    
            elif action == "reject":
                if not rejection_reason:
                    flash("El motivo de rechazo es obligatorio", "error")
                    return redirect(url_for('reviews.index'))
                
                if len(rejection_reason) > 200:
                    flash("El motivo de rechazo no puede exceder 200 caracteres", "error")
                    return redirect(url_for('reviews.index'))
                
                success = ReviewService.reject_review(
                    review_id=review_id,
                    moderator_id=moderator_id,
                    rejection_reason=rejection_reason,
                    description="Reseña rechazada desde panel de moderación"
                )
                if success:
                    flash("Reseña rechazada exitosamente", "success")
                else:
                    flash("Error al rechazar la reseña", "error")
                    
            elif action == "delete":
                success = ReviewService.delete_review(
                    review_id=review_id,
                    moderator_id=moderator_id,
                    description="Reseña eliminada desde panel de moderación"
                )
                if success:
                    flash("Reseña eliminada exitosamente", "success")
                else:
                    flash("Error al eliminar la reseña", "error")
            else:
                flash("Acción no válida", "error")
                
        except ValueError:
            flash("ID de reseña inválido", "error")
        except Exception as e:
            flash(f"Error inesperado: {str(e)}", "error")
        
        return redirect(url_for('reviews.index'))
        
    elif request.method == "GET":
        # Obtener todas las reseñas
        reviews = ReviewService.get_all_reviews()
        
        return render_template(
            "reviews/index.html",
            reviews=reviews
        )


@reviews_blueprint.route("/<int:review_id>")
@login_required
@require_role(['Moderador', 'Editor', 'Administrador'])
def detail(review_id):
    """
    Muestra el detalle completo de una reseña específica.
    """
    review = ReviewService.get_review_by_id(review_id)
    
    if not review:
        flash("Reseña no encontrada", "error")
        return redirect(url_for('reviews.index'))
    
    # Obtener auditorías relacionadas
    audits = db.session.query(ReviewAudit).filter_by(review_id=review_id).options(
        joinedload(ReviewAudit.user)
    ).order_by(ReviewAudit.created_at.desc()).all()
    
    return render_template(
        "reviews/detail.html",
        review=review,
        audits=audits
    )
