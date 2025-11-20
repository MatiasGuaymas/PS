from flask import Blueprint, request, jsonify, session
from core.services.review_service import ReviewService 
from core.models.Site import Site 
from core.models.Review import Review 
from core.database import db

# Definición del Blueprint: La base de URL ahora es solo /api
reviewsAPI_blueprint = Blueprint("reviewsAPI", __name__, url_prefix="/api")



@reviewsAPI_blueprint.route("/reviews", methods=["OPTIONS"])
@reviewsAPI_blueprint.route("/reviews/<int:review_id>", methods=["OPTIONS"])
def handle_reviews_preflight():
    """Maneja las solicitudes OPTIONS para /api/reviews y /api/reviews/<id>."""
    return "", 200

#-----------------------------------------------------
@reviewsAPI_blueprint.route("/reviews", methods=["POST"])
def api_create_review():
    """
    API para que un usuario del portal cree una reseña.
    """
    data = request.get_json() or {}
    
    # 1. Obtener user_id: primero del body, sino de la sesión
    user_id = data.get("user_id") or session.get("user_id")
    
    if not user_id:
        return jsonify({
            "ok": False, 
            "error": "Debes iniciar sesión para dejar una reseña"
        }), 401
    

    print(f"🔍 DEBUG - user_id recibido: {user_id}")
    print(f"🔍 DEBUG - session user_id: {session.get('user_id')}")
    
    # 3. Obtener datos del request
    rating = data.get("rating")
    text = data.get("text")
    site_id = data.get("site_id")
    
    # 4. Validación básica
    if not site_id:
        return jsonify({"ok": False, "error": "Falta el ID del sitio"}), 400
    
    try:
        # 5. Llamar al servicio
        review = ReviewService.create_review_from_api(
            site_id=int(site_id),
            user_id=int(user_id),  # Ahora usa el user_id correcto
            rating=rating,
            text=text
        )
        # 5. Éxito: devolver 201 Created
        return jsonify({
            "ok": True,
            "message": "Reseña creada exitosamente. Pendiente de moderación.",
            "data": review.to_dict()
        }), 201
        
    except ValueError as e:
        # 6. Errores de validación del servicio
        error_msg = str(e)
        
        # Determinar código de estado según el error
        if "no existe" in error_msg or "fue eliminado" in error_msg:
            status_code = 404
        elif "Ya existe" in error_msg:
            status_code = 409  # Conflict
        else:
            status_code = 400  # Bad Request
            
        return jsonify({"ok": False, "error": error_msg}), status_code
        
    except Exception as e:
        # 7. Error inesperado
        print(f"❌ ERROR INESPERADO en api_create_review: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "ok": False, 
            "error": "Error interno del servidor. Revisa los logs del backend."
        }), 500
#-----------------------------------------------------

# GET en /api/reviews

@reviewsAPI_blueprint.route("/reviews", methods=["GET"])
def api_get_public_reviews():
    """
    API pública para devolver SOLO reseñas aprobadas.
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
            "page": pagination.page,
            "per_page": pagination.per_page,
            "reviews": reviews_data
        }), 200

    except Exception as e:
        print(f"Error al obtener reseñas públicas: {e}")
        return jsonify({"ok": False, "error": "Error al procesar la solicitud."}), 500