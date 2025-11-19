from flask import Blueprint, render_template, request, redirect, url_for,session, flash,abort,Response, jsonify
from core.models.Site import Site
from core.models.Tag import Tag
from core.models.Category import Category
from core.models.State import State
from core.database import db
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, and_
from core.services.sites_service import SiteService
from core.models.UserFavorite import UserFavorite
from core.utils.pagination import paginate_query


sitesAPI_blueprint = Blueprint("sitesAPI", __name__, url_prefix="/api/sites")

@sitesAPI_blueprint.route("/", methods=["GET"])
def list_sites():
    """
    Lista sitios históricos con paginación, búsqueda y filtros.
    
    Query params:
        - page: número de página (default: 1)
        - per_page: items por página (default: 12)
        - q: búsqueda por nombre y descripción breve
        - province: filtro por provincia
        - city: filtro por ciudad
        - tags: filtro por tags (IDs separados por coma)
        - state: filtro por nombre de estado
        - sort: ordenamiento (site_name, registration, rating, default: site_name)
        - order: dirección (asc, desc, default: asc)
        - lat: latitud para ordenamiento por distancia (opcional)
        - lng: longitud para ordenamiento por distancia (opcional)
        - radius: radio en km para filtrar por distancia (opcional)
    """
    # Parámetros de paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    # Parámetros de búsqueda y filtros
    search_query = request.args.get('q', '').strip()
    province_filter = request.args.get('province', '').strip()
    city_filter = request.args.get('city', '').strip()
    state_filter = request.args.get('state', '').strip()
    
    # Filtro de tags (string separado por comas)
    tags_param = request.args.get('tags', '').strip()
    tags_filter = []
    if tags_param:
        try:
            tags_filter = [int(t) for t in tags_param.split(',') if t.strip().isdigit()]
        except ValueError:
            pass
    
    # Parámetros de ordenamiento
    sort_by = request.args.get('sort', 'site_name')  # site_name, registration, rating
    order = request.args.get('order', 'asc')  # asc, desc
    
    # Parámetros de geolocalización
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', type=float)  # en km
    
    filters = {
        'active': True,
        'deleted': False 
    }

    if search_query:
        filters['search_text'] = search_query
    
    if city_filter:
        filters['city'] = {'operator': 'ilike', 'value': city_filter}
    
    if province_filter:
        filters['province'] = {'operator': 'ilike', 'value': province_filter}
    
    if state_filter:
        try:
            state_id = int(state_filter)
            filters['state_id'] = state_id
        except ValueError:
            pass
    
    if tags_filter:
        filters['tags'] = tags_filter
    
    pagination = SiteService.get_sites_filtered(
        filters=filters,
        order_by=sort_by,
        sorted_by=order,
        paginate=True,
        page=page,
        per_page=per_page,
        lng=lng,
        lat=lat,
        radius=radius
    )
    
    # Serializar resultados
    sites_json = [site.to_dict() for site in pagination['items']]
    return jsonify({
        'data': sites_json,
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
    })


@sitesAPI_blueprint.route("/tags", methods=["GET"])
def list_tags():
    """
    Lista todos los tags disponibles.
    
    Returns:
        JSON con lista de tags ordenados alfabéticamente
    """
    tags = db.session.query(Tag).order_by(Tag.name.asc()).all()
    tags_json = [{'id': tag.id, 'name': tag.name} for tag in tags]
    
    return jsonify({'data': tags_json})


@sitesAPI_blueprint.route("/provinces", methods=["GET"])
def list_provinces():
    """
    Lista todas las provincias únicas de los sitios activos.
    
    Returns:
        JSON con lista de provincias ordenadas alfabéticamente
    """
    provinces = db.session.query(Site.province)\
        .filter(Site.active == True, Site.deleted == False)\
        .distinct()\
        .order_by(Site.province.asc())\
        .all()
    
    provinces_json = [p[0] for p in provinces if p[0]]
    
    return jsonify({'data': provinces_json})

@sitesAPI_blueprint.route("/states", methods=["GET"])
def list_states():
    """
    Lista todos los estados de conservación disponibles.
    
    Returns:
        JSON con lista de estados
    """
    states = db.session.query(State).order_by(State.id.asc()).all()
    states_json = [{'id': state.id, 'name': state.name} for state in states]
    
    return jsonify({'data': states_json})

@sitesAPI_blueprint.route("/<int:site_id>", methods=["GET"])
def siteDetails(site_id):
    """
    Detalle sobre un sitio. Incrementa el contador de vistas.
    
    Returns:
        JSON con toda la información de un sitio
    """
    
    site = SiteService.get_site_by_id(site_id)
    
    # Incrementar el contador de vistas
    try:
        site.views += 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error incrementando vistas: {e}")
    
    json = site.to_dict()
    
    return jsonify({'data': json})


@sitesAPI_blueprint.route("/<int:site_id>/favorite", methods=["GET"])
def favorite_site(site_id):
    """
    Endpoint para marcar/desmarcar favorito (toggle).
    Body JSON: { "user_id": 1 }
    """
    
    user_id = request.args.get('user_id')
    if user_id is None:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        user_id = int(user_id)
    except Exception:
        return jsonify({'error': 'User id inválido'}), 400

    site = db.session.query(Site).filter(Site.id == site_id, Site.deleted == False).first()
    if not site:
        return jsonify({'error': 'Sitio no encontrado'}), 404

    existing = db.session.query(UserFavorite).filter_by(user_id=user_id, site_id=site_id).first()
    try:
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return jsonify({'status': 'Eliminado de favoritos', 'site_id': site_id, 'user_id': user_id}), 200
        else:
            fav = UserFavorite(user_id=user_id, site_id=site_id)
            db.session.add(fav)
            db.session.commit()
            return jsonify({'status': 'Añadido a favoritos', 'site_id': site_id, 'user_id': user_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno', 'detail': str(e)}), 500



@sitesAPI_blueprint.route("/<int:site_id>/get_favorite", methods=["GET"])
def get_favorite(site_id):
    """
    Devuelve si el usuario tiene marcado el sitio como favorito
    Response: { "favorited": true|false, "site_id": ..., "user_id": ... }
    """

    user_id = request.args.get('user_id')
    if user_id is None:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        user_id = int(user_id)
    except Exception:
        return jsonify({'error': 'User id inválido'}), 400

    site = db.session.query(Site).filter(Site.id == site_id, Site.deleted == False).first()
    if not site:
        return jsonify({'error': 'Sitio no encontrado'}), 404

    try:
        fav = db.session.query(UserFavorite).filter_by(user_id=user_id, site_id=site_id).first()
        favorited = bool(fav)
    except Exception as e:
        favorited = False

    return jsonify({'favorited': favorited, 'site_id': site_id, 'user_id': user_id}), 200


@sitesAPI_blueprint.route("/favorites", methods=["GET"])
def list_favorites():
    """
    Devuelve la lista de sitios marcados como favoritos por un usuario con paginación.
    
    Query params:
        - user_id (required): ID del usuario
        - page: número de página (default: 1)
        - per_page: items por página (default: 12)
        - limit (optional): Número máximo de sitios a devolver (ej: 4 para la home)
        - sort: ordenamiento (added_date, site_name, rating, registration, default: added_date)
        - order: dirección (asc, desc, default: desc)
    
    Response: 
    {
        data: [ site_to_dict, ... ],
        user_id: <id>,
        pagination: {
            page: 1,
            per_page: 12,
            total: 50,
            total_pages: 5,
            has_prev: false,
            has_next: true,
            prev_page: null,
            next_page: 2
        }
    }
    """
    # Parámetros de paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    # Parámetros de ordenamiento
    sort_by = request.args.get('sort', 'added_date')  # added_date, site_name, rating, registration
    order = request.args.get('order', 'desc')  # asc, desc
    
    # Parámetro limit (para usar en home, por ejemplo)
    limit = request.args.get('limit', type=int)
    
    # Validar user_id
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            'error': 'user_id es requerido',
            'data': [],
            'user_id': None,
            'pagination': {
                'page': 1,
                'per_page': per_page,
                'total': 0,
                'total_pages': 0,
                'has_prev': False,
                'has_next': False,
                'prev_page': None,
                'next_page': None
            }
        }), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({
            'error': 'user_id debe ser un número',
            'data': [],
            'user_id': None
        }), 400

    try:
        # ✅ Construir query base con join para obtener Site y fecha de agregado
        query = db.session.query(Site, UserFavorite.created_at)\
            .join(UserFavorite, Site.id == UserFavorite.site_id)\
            .filter(
                UserFavorite.user_id == user_id,
                Site.deleted == False
            )
        
        # ✅ Aplicar ordenamiento
        if sort_by == 'site_name':
            order_column = Site.name
        elif sort_by == 'rating':
            order_column = Site.rating_avg
        elif sort_by == 'registration':
            order_column = Site.registration
        elif sort_by == 'added_date':
            order_column = UserFavorite.created_at
        else:
            # Default: ordenar por fecha de agregado a favoritos
            order_column = UserFavorite.created_at
        
        # Aplicar dirección del ordenamiento
        if order.lower() == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
        # ✅ Si hay limit (para home), devolver sin paginación
        if limit and limit > 0:
            items = query.limit(limit).all()
            
            sites_json = []
            for site, added_date in items:
                site_dict = site.to_dict()
                site_dict['favorited_at'] = added_date.isoformat() if added_date else None
                sites_json.append(site_dict)
            
            return jsonify({
                'data': sites_json,
                'count': len(sites_json),
                'user_id': user_id
            }), 200
        
        # ✅ Aplicar paginación usando paginate_query
        pagination = paginate_query(
            query=query,
            page=page,
            per_page=per_page
        )
        
        # Serializar sitios
        sites_json = []
        for site, added_date in pagination['items']:
            site_dict = site.to_dict()
            # Agregar fecha en que fue agregado a favoritos
            site_dict['favorited_at'] = added_date.isoformat() if added_date else None
            sites_json.append(site_dict)
        
        return jsonify({
            'data': sites_json,
            'user_id': user_id,
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
        print(f"❌ Error en list_favorites: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': 'Error obteniendo favoritos',
            'detail': str(e),
            'data': [],
            'user_id': user_id
        }), 500


@sitesAPI_blueprint.route("/most-visited", methods=["GET"])
def most_visited():
    """
    Obtiene los 4 sitios más visitados (activos y no eliminados).
    
    Returns:
        JSON con los 4 sitios más visitados ordenados por views descendente
    """
    try:
        sites = db.session.query(Site)\
            .filter(Site.active == True, Site.deleted == False)\
            .order_by(Site.views.desc())\
            .limit(4)\
            .all()
        
        if not sites:
            return jsonify({'data': [], 'message': 'No hay sitios disponibles'}), 200
        
        sites_json = [site.to_dict() for site in sites]
        return jsonify({'data': sites_json}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error obteniendo sitios más visitados', 'detail': str(e)}), 500


@sitesAPI_blueprint.route("/recently-added", methods=["GET"])
def recently_added():
    """
    Obtiene los 4 sitios agregados más recientemente (activos y no eliminados).
    
    Returns:
        JSON con los 4 sitios más recientes ordenados por registration descendente
    """
    try:
        sites = db.session.query(Site)\
            .filter(Site.active == True, Site.deleted == False)\
            .order_by(Site.registration.desc())\
            .limit(4)\
            .all()
        
        if not sites:
            return jsonify({'data': [], 'message': 'No hay sitios disponibles'}), 200
        
        sites_json = [site.to_dict() for site in sites]
        return jsonify({'data': sites_json}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error obteniendo sitios recientes', 'detail': str(e)}), 500
