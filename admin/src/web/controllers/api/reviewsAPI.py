from flask import Blueprint, request, jsonify, session
from src.core.services.review_service import ReviewService 
from src.core.models.Site import Site 
from src.core.models.Review import Review 
from src.core.database import db
from src.web.handlers.auth import login_required 


reviews_api_blueprint = Blueprint("reviews_api", __name__, url_prefix="/api/reviews")


@reviews_api_blueprint.route("/sites/<int:site_id>/reviews", methods=["POST"])
@login_required 
def api_create_review(site_id):
    """
    API para que un usuario del portal cree una reseña.
    """
    data = request.get_json() or {}
    
    # Obtener datos de la sesión y el cuerpo
    rating = data.get("rating")
    text = data.get("text")
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"ok": False, "error": "Acceso denegado. Se requiere autenticación."}), 401
    
    try:
        # Llamar al servicio, que contiene toda la lógica de validación y persistencia
        review = ReviewService.create_review_from_api(
            site_id=site_id,
            user_id=user_id,
            rating=rating,
            text=text
        )
        
        # Éxito: devolver 201 Created
        return jsonify({
            "ok": True, 
            "message": "Reseña creada. Pendiente de moderación.",
            "review": review.to_dict() 
        }), 201
            
    except ValueError as e:
        # Manejo de errores de validación y lógica de negocio (desde el servicio)
        error_message = str(e)
        
        if "no existe" in error_message:
             return jsonify({"ok": False, "error": error_message}), 404
             
        if "existe una reseña" in error_message:
             return jsonify({"ok": False, "error": error_message}), 409
             
        # Para "Rating inválido", "Texto inválido"
        return jsonify({"ok": False, "error": error_message}), 400 
        
    except Exception as e:
        # Manejo de errores internos del servidor
        print(f"Error al crear reseña: {e}")
        return jsonify({"ok": False, "error": "Error interno del servidor."}), 500
    

@reviews_api_blueprint.route("/reviews", methods=["GET"])
def api_get_public_reviews():
    """
    API pública para devolver SOLO reseñas aprobadas, usado por el portal público.
    """
    try:
        site_id = request.args.get("site_id", type=int)
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Filtro por 'Aprobada' y que el sitio no esté eliminado
        query = Review.query.filter_by(status="Aprobada").join(Site).filter(Site.deleted == False)

        if site_id:
            query = query.filter(Review.site_id == site_id)

        pagination = query.order_by(Review.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        reviews_data = [r.to_dict() for r in pagination.items]

        return jsonify({
            "ok": True,
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "reviews": reviews_data
        }), 200

    except Exception as e:
        print(f"Error al obtener reseñas públicas: {e}")
        return jsonify({"ok": False, "error": "Error al procesar la solicitud."}), 500