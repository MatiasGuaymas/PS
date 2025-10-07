from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.models.Tag import Tag
from core.database import db
from sqlalchemy import func
from src.web.handlers.auth import login_required, require_role

tags_blueprint = Blueprint("tags", __name__, url_prefix="/tags")

def slugify(value):
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = value.lower().replace(' ', '-')
    value = ''.join(c for c in value if c.isalnum() or c == '-')
    return value

@tags_blueprint.route("/", methods=["GET"])
@login_required
@require_role(['Administrador', 'Editor'])
def index():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()
    order = request.args.get("order", "name")
    direction = request.args.get("direction", "asc")
    
    if order not in ["name", "created_at"]:
        order = "name"
    if direction not in ["asc", "desc"]:
        direction = "asc"

    query = Tag.query
    
    if search:
        query = query.filter(func.lower(Tag.name).like(f"%{search.lower()}%"))
    
    if order == "name":
        query = query.order_by(Tag.name.asc() if direction == "asc" else Tag.name.desc())
    elif order == "created_at":
        query = query.order_by(Tag.created_at.asc() if direction == "asc" else Tag.created_at.desc())

    tags = query.paginate(page=page, per_page=25)
    return render_template("tags/index.html", tags=tags, search=search, order=order, direction=direction)

@tags_blueprint.route("/create", methods=["GET", "POST"])
@login_required
@require_role(['Administrador', 'Editor'])
def create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not (3 <= len(name) <= 50):
            flash("El nombre debe tener entre 3 y 50 caracteres.", "danger")
            return render_template("tags/create.html")
        slug = slugify(name)
        if Tag.query.filter(func.lower(Tag.name) == name.lower()).first():
            flash("Ya existe un tag con ese nombre.", "danger")
            return render_template("tags/create.html")
        if Tag.query.filter_by(slug=slug).first():
            flash("Ya existe un tag con ese slug.", "danger")
            return render_template("tags/create.html")
        tag = Tag(name=name, slug=slug)
        db.session.add(tag)
        db.session.commit()
        flash("Tag creado correctamente.", "success")
        return redirect(url_for("tags.index"))
    return render_template("tags/create.html")

@tags_blueprint.route("/<int:tag_id>/edit", methods=["GET", "POST"])
@login_required
@require_role(['Administrador', 'Editor'])
def edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not (3 <= len(name) <= 50):
            flash("El nombre debe tener entre 3 y 50 caracteres.", "danger")
            return render_template("tags/edit.html", tag=tag)
        slug = slugify(name)
        # Validación de unicidad
        if Tag.query.filter(func.lower(Tag.name) == name.lower(), Tag.id != tag.id).first():
            flash("Ya existe un tag con ese nombre.", "danger")
            return render_template("tags/edit.html", tag=tag)
        if Tag.query.filter(Tag.slug == slug, Tag.id != tag.id).first():
            flash("Ya existe un tag con ese slug.", "danger")
            return render_template("tags/edit.html", tag=tag)
        tag.name = name
        tag.slug = slug
        db.session.commit()
        flash("Tag actualizado correctamente.", "success")
        return redirect(url_for("tags.index"))
    return render_template("tags/edit.html", tag=tag)

@tags_blueprint.route("/<int:tag_id>/delete", methods=["POST"])
@login_required
@require_role(['Administrador', 'Editor'])
def delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if tag.site_associations.count() > 0:  
        flash("No se puede eliminar el tag porque está asignado a uno o más sitios.", "danger")
        return redirect(url_for("tags.index"))
    db.session.delete(tag)
    db.session.commit()
    flash("Tag eliminado correctamente.", "success")
    return redirect(url_for("tags.index"))

@tags_blueprint.route("/<int:tag_id>", methods=["GET"])
@login_required
@require_role(['Administrador', 'Editor'])
def detail(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template("tags/detail.html", tag=tag)