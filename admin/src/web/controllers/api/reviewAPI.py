from flask import Blueprint, request, jsonify
from core.database import db
from core.models.Review import Review
from core.models.User import User
from core.utils.pagination import paginate_query
from core.services.sites_service import SiteService

reviewsAPI_blueprint = Blueprint("reviewsAPI", __name__, url_prefix="/api/reviews")

@reviewsAPI_blueprint.route("/user/<int:user_id>", methods=["GET"])
def list_user_reviews(user_id):
    """
    Devuelve todas las reseñas de un usuario con paginación.
    
    Query params:
        - page: número de página (default: 1)
        - per_page: items por página (default: 10)
        - sort: ordenamiento (created_at, rating, default: created_at)
        - order: dirección (asc, desc, default: desc)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    print("=" * 80)
    print(f"📋 GET /api/reviews/user/{user_id}")
    print(f"   - page: {page}, per_page: {per_page}")
    print(f"   - sort: {sort_by}, order: {order}")
    
    try:
        # ✅ Obtener el email del usuario
        user = db.session.query(User).filter(User.id == user_id).first()
        
        if not user:
            print(f"❌ Usuario {user_id} no encontrado")
            return jsonify({
                'error': 'Usuario no encontrado',
                'data': [],
                'user_id': user_id
            }), 404
        
        user_email = user.email
        print(f"   - user_email: {user_email}")
        
        # ✅ Query filtrando por user_email
        query = db.session.query(Review)\
            .filter(Review.user_email == user_email)
        
        # Ordenamiento
        if sort_by == 'rating':
            order_column = Review.rating
        elif sort_by == 'created_at':
            order_column = Review.created_at
        else:
            order_column = Review.created_at
        
        if order.lower() == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
        # Contar total
        total = query.count()
        print(f"   - Total reseñas: {total}")
        
        # Paginar
        pagination = paginate_query(
            query=query,
            page=page,
            per_page=per_page
        )
        
        # Serializar
        reviews_json = []
        for review in pagination['items']:
            review_dict = {
                'id': review.id,
                'site_id': review.site_id,
                'user_email': review.user_email,
                'rating': review.rating,
                'comment': review.content,  # ✅ En el modelo se llama 'content'
                'status': review.status,
                'rejection_reason': review.rejection_reason,
                'created_at': review.created_at.isoformat() if review.created_at else None,
                'updated_at': review.updated_at.isoformat() if review.updated_at else None
            }
            
            # ✅ Incluir información del sitio usando el objeto review original
            site = SiteService.get_site_by_id(review.site_id)
            if site:
                # ✅ Obtener la URL de la imagen correctamente
                cover_url = None
                if site.cover_image:
                    # cover_image es un objeto SiteImage con atributo public_url
                    cover_url = getattr(site.cover_image, 'public_url', None)
                
                # Si no hay imagen de portada, usar imagen por defecto
                if not cover_url:
                    cover_url = SiteService.build_image_url('/public/default_image.png')
                
                review_dict['site'] = {
                    'id': site.id,
                    'name': site.site_name,
                    'image': cover_url,  # ✅ Ahora es una URL string
                    'brief_description': getattr(site, 'short_desc', None)
                }
            
            reviews_json.append(review_dict)
        
        print(f"✅ Devolviendo {len(reviews_json)} reseñas")
        print("=" * 80)
        
        return jsonify({
            'data': reviews_json,
            'user_id': user_id,
            'user_email': user_email,
            'pagination': {
                'page': pagination['current_page'],
                'per_page': pagination['per_page'],
                'total': pagination['total'],
                'total_pages': pagination['pages'],
                'has_prev': pagination['has_prev'],
                'has_next': pagination['has_next'],
                'prev_page': pagination['prev_num'],
                'next_page': pagination['next_num']
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error en list_user_reviews: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        
        return jsonify({
            'error': 'Error obteniendo reseñas',
            'detail': str(e),
            'data': [],
            'user_id': user_id
        }), 500