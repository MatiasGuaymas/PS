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


@reviewsAPI_blueprint.route("/reviews", methods=["POST"])
def api_create_review():
    """
    API para que un usuario del portal cree una reseña.
    Espera 'site_id' en el cuerpo del JSON.
    """
    data = request.get_json() or {}
    
    # 1. Obtener datos de la sesión y el cuerpo
    rating = data.get("rating")
    text = data.get("text")
    site_id = data.get("site_id")
    raw_user_id = session.get("user_id")

    # 2. Validación de Autenticación
    if not raw_user_id:
        return jsonify({"ok": False, "error": "Acceso denegado. Se requiere autenticación."}), 401
    
    # 3. Conversión de Tipos
    try:
        user_id = int(raw_user_id)
        # site_id ya se valida en el servicio, pero lo convertimos aquí para el chequeo de falta
        site_id = int(site_id) 
    except (TypeError, ValueError):
        # Si el site_id o user_id no es convertible, es un error de solicitud
        return jsonify({"ok": False, "error": "ID de usuario o sitio inválido."}), 400
    
    if not site_id:
        return jsonify({"ok": False, "error": "Falta el ID del sitio."}), 400
    
    try:
        # 4. Llamar al servicio
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
            "data": review.to_dict() 
        }), 201
            
    except ValueError as e:
        # Manejo de errores de validación y lógica de negocio (desde el servicio)
        error_message = str(e)
        
        # Estos errores vienen de validaciones en el Servicio (404/409/400)
        if "no existe" in error_message:
             return jsonify({"ok": False, "error": error_message}), 404
             
        if "existe una reseña" in error_message:
             return jsonify({"ok": False, "error": error_message}), 409
             
        # Para "Rating inválido", "Texto inválido" y otros ValueErrors
        return jsonify({"ok": False, "error": error_message}), 400 
        
    except Exception as e:
        import traceback
        import sys
        
        print("-" * 60)
        print("Error DETECTADO en reviewsAPI.py (500 Internal Server Error):")
        # Imprime la traza completa para el diagnóstico
        traceback.print_exc(file=sys.stdout)
        print("-" * 60)
        return jsonify({"ok": False, "error": "Error interno del servidor. Revisa la consola del BACKEND (traza completa)."}, 500)
    


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