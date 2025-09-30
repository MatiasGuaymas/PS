from flask import Blueprint, render_template, request, redirect, url_for
from core.models.Site import Site
from core.models.Tag import Tag
from core.database import db

sites_blueprint = Blueprint("sites", __name__, url_prefix="/sites")

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
        location = f"POINT({longitude} {latitude})" if latitude and longitude else None
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
        tag_ids = request.form.getlist("tags")

        # Validación básica
        if not site_name or not short_desc or not full_desc or not city or not province or not operning_year:
            return render_template("sites/create.html", error="Faltan campos obligatorios")

        location = f"POINT({longitude} {latitude})" if latitude and longitude else None
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
        # Asigna los tags
        tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        new_site.tags = tags
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
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        site.active = request.form.get("active") == "true"
        tag_ids = request.form.getlist("tags")
        if latitude and longitude:
            site.location = f"POINT({longitude} {latitude})"
        tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        site.tags = tags
        db.session.commit()
        return redirect(url_for("sites.detail", site_id=site.id))
    tags = Tag.query.order_by(Tag.name.asc()).all()
    selected_tag_ids = [tag.id for tag in site.tags]
    return render_template("sites/edit.html", site=site, tags=tags, selected_tag_ids=selected_tag_ids)

@sites_blueprint.route("/<int:site_id>/delete", methods=["POST"])
def delete(site_id):
    site = Site.query.get_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    return redirect(url_for("sites.index"))