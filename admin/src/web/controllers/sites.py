from flask import Blueprint, render_template, request, redirect, url_for
from core.models.Site import Site
from core.models.Tag import Tag
from core.database import db
from shapely.geometry import Point
from geoalchemy2.elements import WKTElement

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
        db.session.commit()

        return redirect(url_for("sites.index"))
    elif request.method == "GET":
        page = request.args.get("page", 1, type=int)
        sites = Site.query.paginate(page=page, per_page=25)
        return render_template("sites/index.html", sites=sites)
    else:
        return "Método no permitido", 405

@sites_blueprint.route("/<int:site_id>", methods=["GET"])
def detail(site_id):
    site = Site.query.get_or_404(site_id)
    return render_template("sites/detail.html", site=site)

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
            return render_template("sites/create.html", error="Faltan campos obligatorios")

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
def edit(site_id):
    site = Site.query.get_or_404(site_id)
    if request.method == "POST":
        site.site_name = request.form.get("site_name")
        site.short_desc = request.form.get("short_desc")
        site.full_desc = request.form.get("full_desc")
        site.city = request.form.get("city")
        site.province = request.form.get("province")
        site.operning_year = request.form.get("operning_year")
        site.category_id = request.form.get("category_id")
        site.state_id = request.form.get("state_id")
        # Capturar coordenadas con nombres alternativos por si el front las envía distinto
        latitude = request.form.get("latitude") or request.form.get("lat")
        longitude = request.form.get("longitude") or request.form.get("lng")
        try:
            print(f"[sites.edit] form keys={list(request.form.keys())}")
            print(f"[sites.edit] Recibido lat={latitude}, lon={longitude}")
        except Exception:
            pass
        site.active = request.form.get("active") == "true"
        # Obtener tags como string separado por comas
        tags_str = request.form.get("tags", "")
        tag_ids = [tag_id.strip() for tag_id in tags_str.split(",") if tag_id.strip()] if tags_str else []
        
        # Solo actualizar la ubicación si las coordenadas son válidas; si no, conservar la existente
        new_location = create_point_from_coords(latitude, longitude)
        if new_location is not None:
            site.location = new_location
            try:
                print("[sites.edit] Ubicación actualizada correctamente")
            except Exception:
                pass
        
        # Limpiar tags existentes y agregar nuevos
        site.tag_associations.delete()
        
        # Obtener los tags desde los IDs
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            for tag in tags:
                from core.models.Site_Tag import HistoricSiteTag
                association = HistoricSiteTag(site_id=site.id, tag_id=tag.id)
                db.session.add(association)
        
        db.session.commit()
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
    db.session.delete(site)
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