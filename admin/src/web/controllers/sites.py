from flask import Blueprint, render_template, request, redirect, url_for,session, flash,abort
from core.models.Site import Site
from core.models.Tag import Tag
from core.database import db
from shapely.geometry import Point
from geoalchemy2.elements import WKTElement
from core.models.Audit import Audit
from core.services.sites_service import SiteService
from core.services.user_service import UserService
from web.handlers.auth import login_required
import json

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
def index():
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
            details= f"Se creó un nuevo sitio {new_site.site_name}"
        )
        db.session.commit()

        return redirect(url_for("sites.index"))
    elif request.method == "GET":
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1)

        pagination = SiteService.get_sites_filtered(
            order_by=order_by,
            sorted_by=sorted_by,
            paginate=True,
            page=page,
            per_page=25,
        )

        sites = pagination["items"]


        #page = request.args.get("page", 1, type=int)
        #sites = Site.query.paginate(page=page, per_page=25)
        return render_template("sites/index.html", sites=sites,
                               pagination=pagination,
                               order_by=order_by,
                               sorted_by=sorted_by,)
    else:
        return "Método no permitido", 405

@sites_blueprint.route("/<int:site_id>", methods=["GET"])
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
def create():
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

        # Validación básica
        if not site_name or not short_desc or not full_desc or not city or not province or not operning_year:
            return render_template("sites/create.html", tags=Tag.query.order_by(Tag.name.asc()).all(), error="Faltan campos obligatorios")
        
        # Validación de coordenadas
        if not latitude or not longitude:
            return render_template("sites/create.html", tags=Tag.query.order_by(Tag.name.asc()).all(), error="Debe seleccionar una ubicación en el mapa")
        
        # Validar que las coordenadas sean números válidos
        try:
            lat_float = float(latitude)
            lon_float = float(longitude)
            if not (-90 <= lat_float <= 90 and -180 <= lon_float <= 180):
                return render_template("sites/create.html", tags=Tag.query.order_by(Tag.name.asc()).all(), error="Las coordenadas seleccionadas no son válidas")
        except (ValueError, TypeError):
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
        # Asigna los tags usando la relación correcta
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            for tag in tags:
                from core.models.Site_Tag import HistoricSiteTag
                association = HistoricSiteTag(site_id=new_site.id, tag_id=tag.id)
                db.session.add(association)
            db.session.commit()
        return redirect(url_for("sites.index"))
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return render_template("sites/create.html", tags=tags)

@sites_blueprint.route("/<int:site_id>/edit", methods=["GET", "POST"])
@login_required
def edit(site_id):
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
            added_tags = [str(id) for id in new_tag_ids - original_tag_ids]
            removed_tags = [str(id) for id in original_tag_ids - new_tag_ids]
            
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
                # Opcional: Serializa los cambios exactos para el campo `details`
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
        
        # Commit final para asegurar que los logs de auditoría se guarden
        db.session.commit() 
        flash("Sitio actualizado con éxito.", "success")


        # Confirmar valores persistidos en logs
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
def delete(site_id):
    site = Site.query.get_or_404(site_id)
    if(site):
        site.deleted = True
        # Crear instancia Audit
        SiteService._register_audit_log(
            user_id=session.get("user_id"),
            site_id= site.id,
            action_type='DELETED',
            details= f"Se elimino un nuevo sitio {site.site_name}"
        )
    db.session.commit()
    return redirect(url_for("sites.index"))

@sites_blueprint.route("/search", methods=["GET"])
def search():
    # Filtros del querystring
    site_name = request.args.get("site_name")
    city = request.args.get("city")
    province = request.args.get("province")
    state_id = request.args.get("state_id")
    tags = request.args.getlist("tags")
    registration_from = request.args.get("registration_from")
    registration_to = request.args.get("registration_to")
    error_msg = None
    active = request.args.get("active")
    orden = request.args.get("order_by", "site_name")
    sentido = request.args.get("sentido", "asc")
    page = request.args.get("page", 1, type=int)

    # Consulta base
    query = Site.query
    
    if registration_from and registration_to:
        try:
            from datetime import datetime
            date_from = datetime.strptime(registration_from, "%Y-%m-%d")
            date_to = datetime.strptime(registration_to, "%Y-%m-%d")
            if date_from > date_to:
                error_msg = "La fecha 'desde' no puede ser mayor que la fecha 'hasta'."
        except Exception:
            error_msg = "Formato de fecha inválido."

    # Filtros combinados
    if not error_msg:
        if site_name:
            query = query.filter(
                (Site.site_name.ilike(f"%{site_name}%")) |
                (Site.short_desc.ilike(f"%{site_name}%"))
            )
        if city:
            query = query.filter(Site.city.ilike(f"%{city}%"))
        if province:
            query = query.filter(Site.province == province)
        if state_id:
            query = query.filter(Site.state_id == state_id)
        if registration_from:
            query = query.filter(Site.registration >= registration_from)
        if registration_to:
            query = query.filter(Site.registration <= registration_to)
        if active:
            query = query.filter(Site.active == True)
        if tags:
            query = query.join(Site.tags).filter(Tag.id.in_(tags))

    # Orden
    if orden == "site_name":
        order_col = Site.site_name
    elif orden == "city":
        order_col = Site.city
    elif orden == "province":
        order_col = Site.province
    elif orden == "registration":
        order_col = Site.registration
    else:
        order_col = Site.site_name

    if sentido == "desc":
        order_col = order_col.desc()
    else:
        order_col = order_col.asc()

    if not error_msg:
        query = query.order_by(order_col)
        sites = query.paginate(page=page, per_page=5)
    else:
        sites = None

    # Provincias únicas para el selector
    provincias = [row[0] for row in db.session.query(Site.province).distinct().order_by(Site.province).all()]

    return render_template(
        "sites/list.html",
        sites=sites,
        filtros=request.args,
        provincias=provincias,
        error_msg=error_msg
    )