from flask import Blueprint, request, jsonify, session
from core.services.review_service import ReviewService 
from core.models.Site import Site 
from core.models.Review import Review 
from core.database import db
from datetime import datetime, timezone



# Definición del Blueprint: La base de URL ahora es solo /api
reviewsAPI_blueprint = Blueprint("reviewsAPI", __name__, url_prefix="/api")



@reviewsAPI_blueprint.route("/reviews", methods=["OPTIONS"])
@reviewsAPI_blueprint.route("/reviews/<int:review_id>", methods=["OPTIONS"])
# Agrega 'review_id=None' como argumento opcional
def handle_reviews_preflight(review_id=None): 
    """Maneja las solicitudes OPTIONS para /api/reviews y /api/reviews/<id>."""
    # El valor de review_id no se usa en esta función, pero es necesario aceptarlo
    return "", 200

@reviewsAPI_blueprint.route("/reviews/check-existing", methods=["GET"])
def api_check_existing_review():
    """
    Verifica si el usuario ya tiene una reseña para un sitio.
    PRIORIDAD: Busca por 'user_email' (parametro URL) si existe, sino usa la sesión.
    """
    user_id = session.get("user_id") # Se mantiene para validar que hay sesión activa
    site_id = request.args.get("site_id", type=int)
    # 🟢 Leer el email opcional de la URL
    email_arg = request.args.get("user_email", default=None)
    
    if not user_id:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    
    if not site_id:
        return jsonify({"ok": False, "error": "Falta site_id"}), 400
    
    try:
        from core.models.User import User
        
        target_user = None
        
        # 🟢 Lógica de Prioridad:
        # 1. Si el frontend manda el email, buscamos el usuario por ese email (fix sesión cruzada)
        if email_arg:
            target_user = User.query.filter_by(email=email_arg).first()
            if not target_user:
                # Si mandaron un email pero no existe usuario, error 404
                 return jsonify({"ok": False, "error": "Usuario del email proporcionado no encontrado"}), 404
        else:
            # 2. Si no manda email, usamos el de la sesión (comportamiento original)
            target_user = db.session.get(User, user_id)
            if not target_user:
                return jsonify({"ok": False, "error": "Usuario de sesión no encontrado"}), 404
        
        # Email para buscar (en minúsculas)
        user_email_lower = target_user.email.lower()
        
        # Buscar reseña existente
        existing_review = Review.query.filter(
            Review.site_id == site_id,
            db.func.lower(Review.user_email) == user_email_lower
        ).first()

        if existing_review:
            return jsonify({
                "ok": True,
                "has_review": True,
                "review_id": existing_review.id
            }), 200
        else:
            return jsonify({
                "ok": True,
                "has_review": False
            }), 200
            
    except Exception as e:
        print(f"Error en check_existing_review: {e}")
        return jsonify({"ok": False, "error": "Error al verificar reseña"}), 500
#-----------------------------------------------------

@reviewsAPI_blueprint.route("/reviews", methods=["POST"])
def api_create_review():
    """
    API para crear una nueva reseña.
    """
    # 1. Se mantiene la verificación de autenticación de sesión Flask
    if not session.get("user_id"):
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    
    data = request.json
    rating = data.get("rating", None)
    text = data.get("text", None)
    email_from_payload = data.get("userEmailOverride", None)

    # 2. Asegurar la conversión de site_id
    try:
        raw_site_id = data.get("site_id")
        site_id = int(raw_site_id) if raw_site_id is not None else None
    except ValueError:
        return jsonify({"ok": False, "error": "El ID del sitio es inválido"}), 400

    if rating is None or text is None or site_id is None:
        return jsonify({"ok": False, "error": "Faltan rating, texto y/o site_id"}), 400

    if not email_from_payload:
         return jsonify({"ok": False, "error": "Falta el email de identidad del usuario (userEmailOverride)"}), 400
        
    try:
        from core.models.User import User
        from core.models.Review import Review
        from core.models.Site import Site 
        
        # 3. Verificar existencia de usuario
        user = User.query.filter_by(email=email_from_payload).first()
        if not user:
            return jsonify({"ok": False, "error": "El email de usuario no corresponde a un usuario registrado."}), 404

        # 4. Verificar que el sitio exista
        site = db.session.get(Site, site_id)
        if not site:
             return jsonify({"ok": False, "error": f"Sitio con ID {site_id} no encontrado en la base de datos."}), 404
             
        final_user_email = user.email
        
        # 5. Verificar reseña existente (Búsqueda Case-Insensitive)
        existing_review = Review.query.filter(
            Review.site_id == site_id,
            # Usamos db.func.lower() para la búsqueda case-insensitive
            db.func.lower(Review.user_email) == final_user_email.lower()
        ).first()

        # 🛑 REINCORPORACIÓN CRÍTICA: Bloquear si ya existe una reseña
        if existing_review:
             return jsonify({"ok": False, "error": "Ya tienes una reseña para este sitio. Por favor, edítala."}), 409

        # 6. Crear reseña:
        new_review = Review(
            site_id=site_id,
            # user_id=user.id,  <-- COMENTADO/ELIMINADO
            user_email=final_user_email,
            rating=rating,
            content=text.strip(),
            status='Pendiente',
            created_at=datetime.now(timezone.utc),
            updated_at=None
        )
        
        db.session.add(new_review)
        db.session.commit()
        
        print(f"✅ Reseña creada: ID={new_review.id}. Email: {final_user_email}")

        return jsonify({
            "ok": True,
            "message": "Reseña creada exitosamente. Pendiente de moderación.",
            "data": new_review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print("-" * 50)
        print(f"❌ ERROR DE BASE DE DATOS AL CREAR RESEÑA: {e}") 
        print("-" * 50)
        return jsonify({"ok": False, "error": "Error al crear la reseña (Consulta el log del servidor para más detalles)"}), 500



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
    
@reviewsAPI_blueprint.route("/reviews/<int:review_id>", methods=["GET"])
def api_get_review_for_edit(review_id):
    """
    API para obtener los datos de una reseña para edición.
    Se ignora la autoría/sesión del usuario para resolver el conflicto.
    """
    user_id = session.get("user_id")
    if not user_id:
        # Se necesita estar autenticado para EDITAR (401)
        return jsonify({"ok": False, "error": "No autenticado. Inicia sesión para editar."}), 401
    
    try:
        # No necesitamos obtener el objeto User, solo la reseña.
        review = db.session.get(Review, review_id)
        if not review:
            return jsonify({"ok": False, "error": "Reseña no encontrada"}), 404
        
        # ❌ Se eliminan todas las verificaciones de autoría
        
        # 3. Devolver los datos de la reseña
        return jsonify({
            "ok": True,
            "data": review.to_dict() 
        }), 200
        
    except Exception as e:
        print(f"❌ Error al obtener reseña para edición: {e}")
        return jsonify({"ok": False, "error": "Error interno al cargar la reseña"}), 500
  




@reviewsAPI_blueprint.route("/reviews/<int:review_id>", methods=["PUT"])
def api_update_review(review_id):
    """
    API para actualizar una reseña.
    CRÍTICO: Usa el user_id de la sesión para obtener el email REAL y VERIFICA la autoría.
    """
    # review_id es el argumento que viene de la URL (ruta /reviews/<int:review_id>)
    # user_id viene de la sesión.
    user_id = session.get("user_id") 
    
    if not user_id:
        return jsonify({"ok": False, "error": "No autenticado. Inicia sesión para editar."}), 401

    try:
        # Importaciones locales (para asegurar que las clases están disponibles)
        from core.models.User import User
        # from core.models.Review import Review # Ya debería estar arriba
        
        # 🟢 PASO CLAVE 1: Obtener el email REAL del usuario LOGUEADO (basado en la sesión)
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"ok": False, "error": "Error de sesión (Usuario no encontrado)"}), 404
        
        session_user_email = user.email # 👈 Email de la sesión (SEGURO)

        data = request.json
        rating = data.get("rating", None)
        text = data.get("text", None)
        email_from_payload = data.get("userEmailOverride", None) # Email que envía el Front (se usa para validación de datos, pero NO para seguridad)

        if rating is None or text is None:
            return jsonify({"ok": False, "error": "Faltan rating y/o texto de la reseña"}), 400
            
        if not email_from_payload:
            return jsonify({"ok": False, "error": "Falta el email de identidad del usuario (userEmailOverride)"}), 400

        review = db.session.get(Review, review_id)
        if not review:
            return jsonify({"ok": False, "error": "Reseña no encontrada"}), 404
        
        # 🚨 PASO CLAVE 2: VERIFICACIÓN DE AUTORÍA (403 Forbidden)
        # Se compara el email de la reseña con el email REAL de la sesión (session_user_email)
        if review.user_email.lower() != session_user_email.lower():
            # ESTE ES EL CÓDIGO QUE PREVIENE QUE user@example.com edite admin@example.com
            print(f"❌ AUTORÍA DENEGADA: Reseña de {review.user_email} intentada por {session_user_email} (por ID de sesión)")
            return jsonify({"ok": False, "error": "No estás autorizado para editar esta reseña."}), 403
            
        # Actualizar campos
        review.rating = rating
        review.content = text.strip()
        review.status = 'Pendiente' # Vuelve a moderación
        review.rejection_reason = None 
        
        # Actualizar la fecha
        review.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        print(f"✅ Reseña actualizada: ID={review_id}. Email: {review.user_email}. Updated_at: {review.updated_at}")
        
        return jsonify({
            "ok": True,
            "message": "Reseña actualizada exitosamente. Pendiente de moderación.",
            "status": "Pendiente"
        }), 200

    except Exception as e:
        db.session.rollback()
        print("-" * 50)
        print(f"❌ ERROR DE BASE DE DATOS AL ACTUALIZAR RESEÑA: {e}")
        print("-" * 50)
        return jsonify({"ok": False, "error": "Error al actualizar la reseña (Consulta el log del servidor para más detalles)"}), 500