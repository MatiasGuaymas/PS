from flask import Blueprint, render_template, request, redirect, url_for,session, flash,abort,Response
from core.models.Site import Site
from core.models.Tag import Tag
from core.models.Audit import Audit
from core.database import db
from shapely.geometry import Point
from geoalchemy2.elements import WKTElement
from core.services.sites_service import SiteService
from core.services.user_service import UserService
from src.web.handlers.auth import login_required, require_role
from src.web.utils.export import export_sites_to_csv, get_csv_filename
from datetime import date
import json
import logging

logger = logging.getLogger(__name__)


sites_blueprint = Blueprint("sites", __name__, url_prefix="/sites")


def create_point_from_coords(latitude, longitude):
    """Crea un punto desde coordenadas lat/lon, tolerando comas y espacios (WKTElement SRID=4326)."""
    if latitude is None or longitude is None:
        return None
    try:
        lat_str = str(latitude).strip().replace(',', '.')
        lon_str = str(longitude).strip().replace(',', '.')
        if lat_str == '' or lon_str == '':
            return None
        lat = float(lat_str)
        lon = float(lon_str)
        # Validar rangos básicos
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        # GeoAlchemy2 con WKTElement explícito y SRID
        wkt = f"SRID=4326;POINT({lon} {lat})"
        return WKTElement(wkt, srid=4326)
    except (ValueError, TypeError):
        return None

def get_coords_from_point(point):
    """Extrae lat/lon desde un punto geoalchemy2"""
    if point:
        try:
            # Convertir a shapely Point
            shapely_point = Point(point.x, point.y)
            return shapely_point.y, shapely_point.x  # (lat, lon)
        except:
            return None, None
    return None, None

@sites_blueprint.route("/", methods=["GET", "POST"])
@login_required
@require_role(['Administrador', 'Editor'])
def index():
    """
    Maneja la página principal de sitios históricos.
    
    GET: Muestra la lista de sitios con filtros, ordenamiento y paginación.
         Reutiliza la lógica de la función search() para evitar duplicación de código.
    
    POST: Crea un nuevo sitio histórico.
          Valida los campos obligatorios y registra la acción en el log de auditoría.
    
    Returns:
        GET: render_template con la lista de sitios filtrados
        POST: redirect a la página principal tras crear el sitio
        
    Raises:
        400: Si faltan campos obligatorios en el POST
        405: Si se usa un método HTTP no permitido
    """
    if request.method == "POST":
        site_name = request.form.get("site_name")
        short_desc = request.form.get("short_desc")
        full_desc = request.form.get("full_desc")
        city = request.form.get("city")
        province = request.form.get("province")
        operning_year = request.form.get("operning_year")
        category_id = request.form.get("category_id")
        state_id = request.form.get("state_id")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        active = request.form.get("active") == "true"

        # Validaciones básicas
        if not site_name or not short_desc or not full_desc or not city or not province or not operning_year:
            return "Faltan campos obligatorios", 400

        # Crear instancia Site
        location = create_point_from_coords(latitude, longitude)
        new_site = Site(
            site_name=site_name,
            short_desc=short_desc,
            full_desc=full_desc,
            city=city,
            province=province,
            operning_year=operning_year,
            category_id=category_id,
            state_id=state_id,
            location=location,
            active=active,
        )
        db.session.add(new_site)
        db.session.flush()

        # Registrar el log de auditoria
        SiteService._register_audit_log(
            user_id=session.get("user_id"),
            site_id= new_site.id,
            action_type='CREATE',
            description= f"Se creó un nuevo sitio {new_site.site_name}"
        )
        db.session.commit()

        return redirect(url_for("sites.index"))
    elif request.method == "GET":
        # Reutilizar la lógica de search()
        return search()
    else:
        return "Método no permitido", 405

@sites_blueprint.route("/<int:site_id>", methods=["GET"])
@login_required
@require_role(['Administrador', 'Editor'])
def detail(site_id):
    """
    Muestra el detalle junto al historial de auditorías para un sitio histórico específico,
    con filtros, ordenamiento y paginación.
    """
    site = SiteService.get_site_by_id(site_id)
    if not site:
        return abort(404, description=f"Historical Site with ID {site_id} not found")
        
    # El 'dynamic' te permite usar métodos de Query en la relación
    query = site.audits.order_by(Audit.updated_at.desc())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    order_by = request.args.get('order_by', 'created_at', type=str)
    sorted_by = request.args.get('sorted_by', 'desc', type=str)
    filters = {}

    # Filtro para mostrar no borrados
    filters['not_deleted'] = True

    # Filtro por usuario (asumiendo que 'user_id' es una columna en Audit)
    user_id = request.args.get('user_id', type=int)
    if user_id is not None:
        filters['user_id'] = user_id

    # Filtro por tipo de acción (asumiendo que 'action_type' es una columna en Audit)
    action_type = request.args.get('action_type', type=str)
    if action_type:
        filters['action_type'] = action_type
        
    # Filtro por rango de fechas (usando los filtros especiales 'date_from' y 'date_to')
    date_from = request.args.get('date_from', type=str) # Formato YYYY-MM-DD
    if date_from:
        filters['date_from'] = date_from

    date_to = request.args.get('date_to', type=str) # Formato YYYY-MM-DD
    if date_to:
        filters['date_to'] = date_to

    # --- 4. Llamar al service para obtener el historial paginado ---
    pagination_data = SiteService.get_audit_filtered(
        historical_site_id=site_id,
        filters=filters,
        order_by=order_by,
        sorted_by=sorted_by,
        paginate=True,
        page=page,
        per_page=per_page,
    )
    history = pagination_data["items"]
    all_users = UserService.get_all_users()
    all_actions_types = ['CREATE', 'UPDATE', 'DELETE', 'STATE_CHANGE', 'TAG_CHANGE']

    user_id_to_email_map = {user.id: user.email for user in all_users}

    for item in history:
        try:
            item.parsed_details = json.loads(item.details)
        except (json.JSONDecodeError, TypeError):
            item.parsed_details = None

    # 5. Renderizar la plantilla
    return render_template(
        'sites/detail.html',
        site=site,
        all_users=all_users,
        all_actions_types=all_actions_types,
        history=history,
        site_id= site_id,
        pagination=pagination_data,
        order_by=order_by,
        sorted_by=sorted_by,
        filters=filters,
        user_id_to_email_map=user_id_to_email_map,
        url='sites.detail'
    )

@sites_blueprint.route("/create", methods=["GET", "POST"])
@login_required
@require_role(['Administrador', 'Editor'])
def create():
    """
    Maneja la creación de nuevos sitios históricos.
    
    GET: Muestra el formulario de creación de sitios con todas las etiquetas disponibles.
    
    POST: Procesa el formulario de creación.
          Valida campos obligatorios, coordenadas y crea el sitio con sus etiquetas asociadas.
          Registra la acción en el log de auditoría.
    
    Returns:
        GET: render_template con el formulario de creación
        POST: redirect a la página principal tras crear exitosamente el sitio
        
    Raises:
        render_template con error: Si hay errores de validación en el POST
    """
    if request.method == "POST":
        site_name = request.form.get("site_name")
        short_desc = request.form.get("short_desc")
        full_desc = request.form.get("full_desc")
        city = request.form.get("city")
        province = request.form.get("province")
        operning_year = request.form.get("operning_year")
        category_id = request.form.get("category_id")
        state_id = request.form.get("state_id")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        active = request.form.get("active") == "true"
        # Obtener tags como string separado por comas
        tags_str = request.form.get("tags", "")
        tag_ids = [tag_id.strip() for tag_id in tags_str.split(",") if tag_id.strip()] if tags_str else []
        
        current_user_id = session.get("user_id")
        
        # LOG: Inicio de creación
        logger.info(f"Usuario {current_user_id} intentando crear sitio: '{site_name}' en {city}, {province}")

        # Validación básica
        if not site_name or not short_desc or not full_desc or not city or not province or not operning_year:
            logger.warning(f"Intento de crear sitio con campos faltantes: usuario={current_user_id}, sitio='{site_name}'")
            return render_template("sites/create.html", tags=Tag.query.order_by(Tag.name.asc()).all(), error="Faltan campos obligatorios")
        
        # Validación de coordenadas
        if not latitude or not longitude:
            logger.warning(f"Intento de crear sitio sin coordenadas: usuario={current_user_id}, sitio='{site_name}'")
            return render_template("sites/create.html", tags=Tag.query.order_by(Tag.name.asc()).all(), error="Debe seleccionar una ubicación en el mapa")
        
        # Validar que las coordenadas sean números válidos
        try:
            lat_float = float(latitude)
            lon_float = float(longitude)
            if not (-90 <= lat_float <= 90 and -180 <= lon_float <= 180):
                logger.warning(f"Coordenadas inválidas para sitio: usuario={current_user_id}, sitio='{site_name}', lat={latitude}, lon={longitude}")
                return render_template("sites/create.html", tags=Tag.query.order_by(Tag.name.asc()).all(), error="Las coordenadas seleccionadas no son válidas")
        except (ValueError, TypeError) as e:
            logger.warning(f"Error convirtiendo coordenadas: usuario={current_user_id}, sitio='{site_name}', lat={latitude}, lon={longitude}, error={e}")
            return render_template("sites/create.html", tags=Tag.query.order_by(Tag.name.asc()).all(), error="Las coordenadas seleccionadas no son válidas")

        location = create_point_from_coords(latitude, longitude)
        new_site = Site(
            site_name=site_name,
            short_desc=short_desc,
            full_desc=full_desc,
            city=city,
            province=province,
            operning_year=operning_year,
            category_id=category_id,
            state_id=state_id,
            location=location,
            active=active,
        )
        db.session.add(new_site)
        db.session.flush()

        # Registrar el log de auditoria
        SiteService._register_audit_log(
            user_id=session.get("user_id"),
            site_id= new_site.id,
            action_type='CREATE',
            description= f"Se creó un nuevo sitio {new_site.site_name}"
        )
        db.session.commit()
        
        # LOG: Éxito
        logger.info(f"Sitio creado exitosamente: ID={new_site.id}, nombre='{new_site.site_name}', ciudad='{city}', provincia='{province}', usuario={current_user_id}")
        
        # Asigna los tags usando la relación correcta
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            for tag in tags:
                from core.models.Site_Tag import HistoricSiteTag
                association = HistoricSiteTag(site_id=new_site.id, tag_id=tag.id)
                db.session.add(association)
            db.session.commit()
            logger.info(f"Tags asignados al sitio {new_site.id}: {[tag.name for tag in tags]}")
        
        return redirect(url_for("sites.index"))
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return render_template("sites/create.html", tags=tags)

@sites_blueprint.route("/<int:site_id>/edit", methods=["GET", "POST"])
@login_required
@require_role(['Administrador', 'Editor'])
def edit(site_id):
    """
    Maneja la edición de sitios históricos existentes.
    
    GET: Muestra el formulario de edición con los datos del sitio.
    
    POST: Procesa los cambios del formulario.
          Registra cambios específicos en el log de auditoría:
          - Cambios de estado (STATE_CHANGE)
          - Cambios de etiquetas (TAG_CHANGE) 
          - Cambios generales de campos (UPDATE)
    
    Args:
        site_id (int): ID del sitio histórico a editar
    
    Returns:
        GET: render_template con el formulario de edición
        POST: redirect al detalle del sitio tras actualizar exitosamente
        
    Raises:
        404: Si el sitio no existe
    """
    site = Site.query.get_or_404(site_id)
    current_user_id = session.get("user_id")
    if request.method == "POST":
        #Valores viejos 
        original_state_id = site.state_id
        original_tag_ids = set(assoc.tag_id for assoc in site.tag_associations)
        
        # --- 2. APLICAR CAMBIOS DE PROPIEDADES GENERALES ---
        
        # Guardar valores antiguos para registro de Edición general
        general_changes = {}

        # Mapeo de campos y registro de cambios
        fields_to_check = {
            "site_name": request.form.get("site_name"),
            "short_desc": request.form.get("short_desc"),
            "full_desc": request.form.get("full_desc"),
            "city": request.form.get("city"),
            "province": request.form.get("province"),
            "operning_year": request.form.get("operning_year"),
            "category_id": request.form.get("category_id"),
            "state_id": request.form.get("state_id"),
            "active": request.form.get("active") == "true"
        }
        
        for attr, new_value in fields_to_check.items():
            old_value = getattr(site, attr)
            # Manejar conversión de tipos si es necesario (ej: int a str para comparación)
            if str(old_value) != str(new_value):
                # Aplicar el cambio
                setattr(site, attr, new_value)
                # Registrar el cambio (para la auditoría de Edición general)
                general_changes[attr] = {"old": old_value, "new": new_value}

        # Capturar coordenadas con nombres alternativos por si el front las envía distinto
        latitude = request.form.get("latitude") or request.form.get("lat")
        longitude = request.form.get("longitude") or request.form.get("lng")
        
        # Solo actualizar la ubicación si las coordenadas son válidas; si no, conservar la existente
        new_location = create_point_from_coords(latitude, longitude)
        
        location_changed = False
        if new_location is not None and (site.location is None):
            site.location = new_location
            location_changed = True
            #No deberia darse el caso en que site.location sea None pero por las dudas lo reviso
            general_changes["location"] = {"old": site.location if site.location else "N/A", "new": new_location}

        # Obtener tags como string separado por comas
        tags_str = request.form.get("tags", "")
        new_tag_ids = [tag_id.strip() for tag_id in tags_str.split(",") if tag_id.strip()] if tags_str else []
        tag_ids_from_form = [int(tag_id.strip()) for tag_id in tags_str.split(",") if tag_id.strip().isdigit()]
        new_tag_ids = set(tag_ids_from_form)
        tag_change = False
        if original_tag_ids != new_tag_ids:
            tag_change = True

        # Limpiar tags existentes y agregar nuevos
        site.tag_associations.delete()
        
        # Obtener los tags desde los IDs
        if new_tag_ids:
            tags = Tag.query.filter(Tag.id.in_(new_tag_ids)).all()
            for tag in tags:
                from core.models.Site_Tag import HistoricSiteTag
                association = HistoricSiteTag(site_id=site.id, tag_id=tag.id)
                db.session.add(association)
        
        db.session.commit()
        # --- REGISTRO DE AUDITORÍA ---
        ####################################################################################################
        # A. Registro de CAMBIO DE ESTADO
        final_state_id = site.state_id
        if (original_state_id != final_state_id):
            # Asumo que tienes una forma de obtener el nombre del estado por ID
            desc = f"Estado de sitio cambiado de ID={original_state_id} a ID={final_state_id}."
            SiteService._register_audit_log(
                site_id=site.id, 
                user_id=current_user_id, 
                action_type='STATE_CHANGE', 
                description=desc
            )
            
        # B. Registro de CAMBIO DE TAGS
        if tag_change:
            new_tag_ids = set(new_tag_ids)
            all_tags = Tag.query.all()
            tags_map = {tag.id: tag.name for tag in all_tags}
            added_tags = [str(tags_map[id]) for id in new_tag_ids - original_tag_ids]
            removed_tags = [str(tags_map[id]) for id in original_tag_ids - new_tag_ids]
            
            desc = f"Tags modificados. Añadidos IDs: {', '.join(added_tags)}. Eliminados IDs: {', '.join(removed_tags)}."
            SiteService._register_audit_log(
                site_id=site.id, 
                user_id=current_user_id, 
                action_type='TAG_CHANGE', 
                description=desc
            )
            
        # C. Registro de EDICIÓN GENERAL (Otros campos)
        if general_changes or location_changed:
            
            # Excluir state_id si ya fue registrado arriba, para no duplicar logs
            if "state_id" in general_changes:
                del general_changes["state_id"] 

            if general_changes:
                # Opcional: Serializa los cambios exactos para el campo `details` queda más lindo y lo mapeo más tarde por colores
                details_json = json.dumps(general_changes, default=str)
                
                # Descripción genérica
                desc = f"Campos de detalle y/o ubicación modificados. ({len(general_changes)} campos afectados)."
                
                SiteService._register_audit_log(
                    site_id=site.id, 
                    user_id=current_user_id, 
                    action_type='UPDATE', 
                    description=desc,
                    details=details_json
                )
        
        db.session.commit() 
        flash("Sitio actualizado con éxito.", "success")

        try:
            db.session.refresh(site)
            print(f"[sites.edit] Persistido lat={site.latitude}, lon={site.longitude}")
        except Exception:
            pass
        return redirect(url_for("sites.detail", site_id=site.id))
    
    tags = Tag.query.order_by(Tag.name.asc()).all()
    selected_tag_ids = [association.tag_id for association in site.tag_associations]
    return render_template("sites/edit.html", site=site, tags=tags, selected_tag_ids=selected_tag_ids)

@sites_blueprint.route("/<int:site_id>/delete", methods=["POST"])
@login_required
@require_role(['Administrador'])
def delete(site_id):
    """
    Elimina (soft delete) un sitio histórico.
    
    Marca el sitio como eliminado (deleted=True) en lugar de borrarlo físicamente.
    Registra la acción de eliminación en el log de auditoría.
    
    Args:
        site_id (int): ID del sitio histórico a eliminar
    
    Returns:
        redirect: Redirección a la página principal tras eliminar el sitio
        
    Raises:
        404: Si el sitio no existe
    
    Note:
        Solo usuarios con rol 'Administrador' pueden eliminar sitios.
    """
    site = Site.query.get_or_404(site_id)
    current_user_id = session.get("user_id")
    
    # LOG: Inicio de eliminación
    logger.info(f"Usuario {current_user_id} intentando eliminar sitio ID={site_id}: '{site.site_name}'")
    
    if site:
        site.deleted = True
        
        # Registrar el log de auditoría con parámetros correctos
        SiteService._register_audit_log(
            site_id=site.id,
            user_id=session.get("user_id"),
            action_type='DELETE',
            description=f"Se eliminó el sitio {site.site_name}"
        )
        
        db.session.commit()
        
        # LOG: Éxito
        logger.info(f"Sitio eliminado exitosamente: ID={site_id}, nombre='{site.site_name}', ciudad='{site.city}', provincia='{site.province}', usuario={current_user_id}")
        
        flash("Sitio eliminado correctamente.", "success")
    
    return redirect(url_for("sites.index"))

@sites_blueprint.route("/search", methods=["GET"])
@login_required
@require_role(['Administrador', 'Editor'])
def search():
    """
    Busca y filtra sitios históricos con parámetros avanzados.
    
    Procesa múltiples filtros de búsqueda desde query parameters:
    - site_name: Búsqueda por nombre del sitio
    - city: Filtro por ciudad
    - province: Filtro por provincia
    - tags: Filtro por etiquetas (múltiples valores)
    - registration_from/registration_to: Rango de fechas de registro
    - active: Filtro por estado activo/inactivo
    - state_id: Filtro por estado de conservación
    - order_by: Campo de ordenamiento
    - sentido: Dirección del ordenamiento (asc/desc)
    
    Valida rangos de fechas y maneja errores de formato.
    
    Returns:
        render_template: Página de resultados con sitios filtrados y paginados
        
    Query Parameters:
        site_name (str): Nombre del sitio a buscar
        city (str): Ciudad para filtrar
        province (str): Provincia para filtrar
        tags (list): Lista de IDs de etiquetas
        registration_from (str): Fecha de inicio (YYYY-MM-DD)
        registration_to (str): Fecha de fin (YYYY-MM-DD)
        active (str): Estado activo ('true'/'false')
        state_id (str): ID del estado de conservación
        order_by (str): Campo de ordenamiento
        sentido (str): Dirección del ordenamiento
        page (int): Número de página
    """
    tags_raw = request.args.getlist("tags")
    tags = [int(t) for t in tags_raw if str(t).isdigit()]
    
    registration_from = request.args.get("registration_from", "")
    registration_to = request.args.get("registration_to", "")
    
    filtros = {
        "site_name": request.args.get("site_name", ""),
        "city": request.args.get("city", ""),
        "province": request.args.get("province", ""),
        "tags": tags,
        "registration_from": registration_from,
        "registration_to": registration_to,
        "active": request.args.get("active", ""),
        "order_by": request.args.get("order_by", "site_name"),
        "sentido": request.args.get("sentido", "asc"),
    }

    state_id_raw = request.args.get("state_id", "")
    if state_id_raw and state_id_raw.isdigit():
        filtros["state_id"] = int(state_id_raw)
    error_msg = None
    page = request.args.get("page", 1, type=int)

    if registration_from and registration_to:
        try:
            from datetime import datetime
            date_from = datetime.strptime(registration_from, "%Y-%m-%d")
            date_to = datetime.strptime(registration_to, "%Y-%m-%d")
            if date_from > date_to:
                error_msg = "La fecha 'desde' no puede ser mayor que la fecha 'hasta'."
                flash(error_msg, "error")
        except Exception:
            error_msg = "Formato de fecha inválido."

    service_filters = {
        "site_name": filtros["site_name"],
        "city": filtros["city"],
        "province": filtros["province"],
        "tags": filtros["tags"],
        "active": filtros["active"],
    }

    if registration_from:
        service_filters["date_from"] = registration_from
    if registration_to:
        service_filters["date_to"] = registration_to
    
    if state_id_raw and state_id_raw.isdigit():
        service_filters["state_id"] = int(state_id_raw)
    
    if state_id_raw and state_id_raw.isdigit():
        service_filters["state_id"] = int(state_id_raw)

    pagination = None
    if not error_msg:
        pagination = SiteService.get_sites_filtered(
            filters=service_filters,
            order_by=filtros["order_by"],
            sorted_by=filtros["sentido"],
            paginate=True,
            page=page,
            per_page=25,
        )
    sites = pagination["items"] if pagination else []

    print(f"Encontrado {len(sites)} sitios con filtros: {filtros}")

    provincias = [row[0] for row in db.session.query(Site.province).distinct().order_by(Site.province).all()]
    all_tags = Tag.query.order_by(Tag.name.asc()).all()

    return render_template(
        "sites/index.html",
        sites=sites,
        pagination=pagination,
        filtros=filtros,
        provincias=provincias,
        tags=all_tags,
        error_msg=error_msg,
        hoy=date.today().isoformat()
    )

@sites_blueprint.route("/export_csv", methods=["POST"])
@login_required
@require_role(['Administrador'])
def export_csv():
    """
    Exporta sitios históricos filtrados a formato CSV.
    
    Aplica los mismos filtros que la función de búsqueda pero exporta
    todos los resultados (sin paginación) a un archivo CSV descargable.
    
    Filtros soportados (desde form data):
    - site_name: Nombre del sitio
    - city: Ciudad
    - province: Provincia
    - tags: Etiquetas asociadas
    - registration_from/registration_to: Rango de fechas
    - active: Estado activo
    - state_id: Estado de conservación
    - order_by: Campo de ordenamiento
    - sentido: Dirección del ordenamiento
    
    Returns:
        Response: Archivo CSV con headers apropiados para descarga
        
    Raises:
        400: Si no hay datos para exportar
        
    Note:
        Solo usuarios con rol 'Administrador' pueden exportar datos.
        El archivo se genera con timestamp en el nombre.
    """

    tags_raw = request.form.getlist("tags")
    tags = [int(t) for t in tags_raw if t and str(t).isdigit()]

    registration_from = request.form.get("registration_from", "")
    registration_to = request.form.get("registration_to", "")

    filtros = {
        "site_name": request.form.get("site_name", ""),
        "city": request.form.get("city", ""),
        "province": request.form.get("province", ""),
        "tags": tags,
        "registration_from": registration_from,
        "registration_to": registration_to,
        "active": request.form.get("active", ""),
        "order_by": request.form.get("order_by", "site_name"),
        "sentido": request.form.get("sentido", "asc"),
    }

    print("Filtros recibidos en export_csv:", filtros)

    state_id_raw = request.form.get("state_id", "")
    if state_id_raw and state_id_raw.isdigit():
        filtros["state_id"] = int(state_id_raw)

    service_filters = {
        "site_name": filtros["site_name"],
        "city": filtros["city"],
        "province": filtros["province"],
        "tags": filtros["tags"],
        "active": filtros["active"],
    }
    
    if registration_from:
        service_filters["date_from"] = registration_from
    if registration_to:
        service_filters["date_to"] = registration_to
    
    if state_id_raw and state_id_raw.isdigit():
        service_filters["state_id"] = int(state_id_raw)

    sites = SiteService.get_sites_filtered(
        filters=service_filters,
        order_by=filtros["order_by"],
        sorted_by=filtros["sentido"],
        paginate=False,
    )

    print(f"Exportando {len(sites)} sitios con filtros: {filtros}")

    if not sites:
        return "No hay datos para exportar", 400

    csv_content = export_sites_to_csv(sites)
    filename = get_csv_filename()
    return Response(
        csv_content,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
