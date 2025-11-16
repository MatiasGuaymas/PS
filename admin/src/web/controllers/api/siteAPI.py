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
        per_page=per_page
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
    Detalle sobre un sitio.
    
    Returns:
        JSON con toda la información de un sitio
    """
    
    site = SiteService.get_site_by_id(site_id)
    json = site.to_dict()
    
    return jsonify({'data': json})


@sitesAPI_blueprint.route("/<int:site_id>/favorite", methods=["POST"])
def favorite_site(site_id):
    """
    Endpoint para marcar/desmarcar favorito (toggle).
    Body JSON: { "user_id": 1 }
    """
    
    user_id = request.json.get('user_id')

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



@sitesAPI_blueprint.route("/<int:site_id>/favorite", methods=["GET"])
def get_favorite(site_id):
    """
    Devuelve si el usuario tiene marcado el sitio como favorito
    Response: { "favorited": true|false, "site_id": ..., "user_id": ... }
    """

    user_id = request.args.get('user_id')

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
    Devuelve la lista de sitios marcados como favoritos por un usuario.
    Query params:
      - user_id

    Response: { data: [ site_to_dict, ... ], user_id: <id> }
    """

    user_id = request.args.get('user_id', 1)

    try:
        fav_rows = db.session.query(UserFavorite).filter(UserFavorite.user_id == user_id).order_by(UserFavorite.id.desc()).all()
        site_ids = [int(f.site_id) for f in fav_rows] if fav_rows else []
    except Exception as e:
        site_ids = []

    sites_json = []
    if site_ids:
        try:
            sites = db.session.query(Site).filter(Site.id.in_(site_ids), Site.deleted == False).all()
            sites_map = {s.id: s for s in sites}
            for sid in site_ids:
                s = sites_map.get(sid)
                if s:
                    sites_json.append(s.to_dict())
        except Exception as e:
            sites_json = []

    return jsonify({'data': sites_json, 'user_id': user_id}), 200
