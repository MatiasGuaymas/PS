from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.models.Review import Review
from core.models.ReviewAudit import ReviewAudit
from core.database import db
from core.services.review_service import ReviewService
from src.web.handlers.auth import login_required, require_role
from sqlalchemy.orm import joinedload

from core.models.Site import Site 
from datetime import datetime,date

reviews_blueprint = Blueprint("reviews", __name__, url_prefix="/reviews")




@reviews_blueprint.route("/<int:review_id>/confirm-delete", methods=["GET"])
@login_required
@require_role(['Administrador', 'Editor', 'Moderador'])
def confirm_delete(review_id):
    """Muestra la página de confirmación para eliminar una reseña"""
    review = ReviewService.get_review_by_id(review_id)
    if not review:
        flash("Reseña no encontrada", "error")
        return redirect(url_for('reviews.index'))
    
    return render_template("reviews/confirm_delete.html", review=review)

@reviews_blueprint.route("/<int:review_id>/delete", methods=["POST"])
@login_required
@require_role(['Administrador', 'Editor', 'Moderador'])
def delete(review_id):
    """Elimina una reseña permanentemente"""
    try:
        success = ReviewService.delete_review(review_id)
        if success:
            flash(" Reseña eliminada exitosamente. La reseña ha sido eliminada permanentemente del sistema.", "success")
        else:
            flash(" No se pudo eliminar la reseña. Inténtalo nuevamente.", "error")
    except Exception as e:
        flash(f"Error al eliminar la reseña: {str(e)}", "error")
    
    return redirect(url_for('reviews.index'))

@reviews_blueprint.route("/", methods=["GET", "POST"])
@login_required
@require_role(['Administrador', 'Editor', 'Moderador'])
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
                success = ReviewService.delete_review(review_id)
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
        
    if request.method == "GET":
        
        # 1. Obtener parámetros de la URL
        page = int(request.args.get('page', 1))
        order_by = request.args.get('order_by', 'created_at') 
        sorted_by = request.args.get('sorted_by', 'desc') 

        # Filtros (strings/None)
        current_filters_str = {
            'status': request.args.get('status'),
            'site_id': request.args.get('site_id'),
            'min_rating': request.args.get('min_rating'),
            'max_rating': request.args.get('max_rating'),
            'date_from': request.args.get('date_from'),
            'date_to': request.args.get('date_to'),
            'user_email': request.args.get('user_email')
        }
        
        # 2. Conversión de Tipos de Datos para el servicio (algunos a int/datetime)
        service_filters = {}
        valid_filters = True
        current_date = date.today()
        dt_from = None
        dt_to = None
        
        # Filtros String (solo si tienen valor)
        if current_filters_str['status']:
            service_filters['status'] = current_filters_str['status']
        
        #Limpiar el email de espacios
        user_email_clean = current_filters_str['user_email']
        if user_email_clean:
            user_email_clean = user_email_clean.strip() # Eliminar espacios en blanco
            if user_email_clean: # Verifica que no esté vacío después de limpiar
                service_filters['user_email'] = user_email_clean

        # Conversión a Integer
        if current_filters_str['site_id'] and current_filters_str['site_id'].isdigit():
            service_filters['site_id'] = int(current_filters_str['site_id'])

        if current_filters_str['min_rating'] and current_filters_str['min_rating'].isdigit():
            service_filters['min_rating'] = int(current_filters_str['min_rating'])

        if current_filters_str['max_rating'] and current_filters_str['max_rating'].isdigit():
            service_filters['max_rating'] = int(current_filters_str['max_rating'])
        
        # Conversión a Datetime y VALIDACIONES DE FECHA 
        try:
            # --- Validación de FECHA DESDE ---
            if current_filters_str['date_from']:
                dt_from = datetime.strptime(current_filters_str['date_from'], '%Y-%m-%d').date()
                if dt_from > current_date:
                    flash("La fecha 'Desde' no puede ser futura.", "error")
                    valid_filters = False
                else:
                    service_filters['date_from'] = datetime.combine(dt_from, datetime.min.time())
            
            # --- Validación de FECHA HASTA ---
            if current_filters_str['date_to']:
                dt_to = datetime.strptime(current_filters_str['date_to'], '%Y-%m-%d').date()
                if dt_to > current_date:
                    flash("La fecha 'Hasta' no puede ser futura.", "error")
                    valid_filters = False
                else:
                    # Usamos datetime.max.time() para incluir todo el día 'Hasta'
                    service_filters['date_to'] = datetime.combine(dt_to, datetime.max.time())
            
            # --- Validación de RANGO (Desde > Hasta) ---
            # Solo chequeamos el rango si ambas fechas fueron válidas en formato y no-futuras.
            if dt_from and dt_to and dt_from > dt_to:
                flash("La fecha 'Desde' no puede ser posterior a la fecha 'Hasta'.", "error")
                valid_filters = False

        except ValueError:
            # Este es el error de formato que tenías.
            flash("Formato de fecha inválido. Usando AAAA-MM-DD.", "error")
            valid_filters = False 
            
        # Si hubo cualquier error de validación de fecha, eliminamos las fechas del filtro 
        # para que la consulta no se ejecute con datos incorrectos o falle.
        if not valid_filters:
            service_filters.pop('date_from', None)
            service_filters.pop('date_to', None)

        # 3. Llamar al servicio
        reviews_data = ReviewService.get_reviews_paginated(
            page=page, 
            per_page=25,
            filters=service_filters,
            order_by=order_by,
            sorted_by=sorted_by
        )
        
        # Obtener lista de sitios para el selector en el formulario
        sites = db.session.query(Site).order_by(Site.site_name).all()

        # 4. Retornar la vista
        return render_template(
            "reviews/index.html",
            reviews=reviews_data['reviews'],
            pagination=reviews_data,
            sites=sites, 
            # Pasar los filtros *originales* (strings) para rellenar el formulario.
            current_filters={k: v for k, v in current_filters_str.items() if v}
        )


@reviews_blueprint.route("/<int:review_id>", methods=["GET"])
@login_required
@require_role(['Administrador', 'Editor', 'Moderador'])
def detail(review_id):
    """
    Muestra el detalle completo de una reseña específica. 
    """
    # GET: Mostrar detalle
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
