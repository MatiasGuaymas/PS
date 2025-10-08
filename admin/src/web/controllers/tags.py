from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.models.Tag import Tag
from core.database import db
from sqlalchemy import func
from src.web.handlers.auth import login_required, require_role
import logging

logger = logging.getLogger(__name__)

tags_blueprint = Blueprint("tags", __name__, url_prefix="/tags")

def slugify(value):
    """
    Convierte un string a formato slug (URL-friendly).
    
    Un slug es una versión limpia de un texto que se puede usar en URLs.
    Ejemplos: "Mi Sitio Histórico" → "mi-sitio-historico"
    
    Args:
        value (str): Texto a convertir a slug
        
    Returns:
        str: Slug generado (solo letras, números y guiones, en minúsculas)
   
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = value.lower().replace(' ', '-')
    value = ''.join(c for c in value if c.isalnum() or c == '-')
    return value

def validate_tag_name(name):
    """
    Valida el nombre de un tag.
    
    Args:
        name (str): Nombre a validar
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not (3 <= len(name) <= 50):
        return False, "El nombre debe tener entre 3 y 50 caracteres."
    return True, None

def check_tag_uniqueness(name, slug, exclude_id=None):
    """
    Verifica la unicidad del nombre y slug de un tag.
    
    Cada tag debe tener un nombre y slug únicos para evitar duplicados.
    El slug se usa para URLs amigables (ej: /tags/iglesia-de-san-juan).
    
    Args:
        name (str): Nombre del tag
        slug (str): Slug del tag
        exclude_id (int, optional): ID a excluir de la búsqueda (para edición)
        
    Returns:
        tuple: (is_unique, error_message)
            - is_unique (bool): True si es único, False si ya existe
            - error_message (str): Mensaje de error si no es único, None si es único
    """
    # Verificar unicidad del nombre
    name_query = Tag.query.filter(func.lower(Tag.name) == name.lower())
    if exclude_id:
        name_query = name_query.filter(Tag.id != exclude_id)
    
    if name_query.first():
        return False, "Ya existe un tag con ese nombre."
    
    # Verificar unicidad del slug
    slug_query = Tag.query.filter(Tag.slug == slug)
    if exclude_id:
        slug_query = slug_query.filter(Tag.id != exclude_id)
        
    if slug_query.first():
        return False, "Ya existe un tag con ese slug."
    
    return True, None

def validate_and_create_tag(name):
    """
    Valida y crea un tag con el nombre dado.
    
    Procesa el nombre del tag: valida longitud, genera slug automáticamente
    y verifica que no exista otro tag con el mismo nombre o slug.
    
    Args:
        name (str): Nombre del tag
        
    Returns:
        tuple: (tag, error_message)
    """
    # Validar nombre
    is_valid, error_msg = validate_tag_name(name)
    if not is_valid:
        return None, error_msg
    
    # Generar slug
    slug = slugify(name)
    
    # Verificar unicidad
    is_unique, error_msg = check_tag_uniqueness(name, slug)
    if not is_unique:
        return None, error_msg
    
    # Crear tag
    tag = Tag(name=name, slug=slug)
    return tag, None

def validate_and_update_tag(tag, name):
    """
    Valida y actualiza un tag existente.
    
    Procesa el nuevo nombre: valida longitud, genera slug automáticamente
    y verifica que no exista otro tag con el mismo nombre o slug.
    
    Args:
        tag (Tag): Instancia del tag a actualizar
        name (str): Nuevo nombre del tag
        
    Returns:
        tuple: (success, error_message)
    """
    # Validar nombre
    is_valid, error_msg = validate_tag_name(name)
    if not is_valid:
        return False, error_msg
    
    # Generar slug
    slug = slugify(name)
    
    # Verificar unicidad (excluyendo el tag actual)
    is_unique, error_msg = check_tag_uniqueness(name, slug, exclude_id=tag.id)
    if not is_unique:
        return False, error_msg
    
    # Actualizar tag
    tag.name = name
    tag.slug = slug
    return True, None

@tags_blueprint.route("/", methods=["GET"])
@login_required
@require_role(['Administrador', 'Editor'])
def index():
    """
    Muestra la lista de tags con búsqueda, ordenamiento y paginación.
    
    Soporta filtros por nombre y ordenamiento por nombre o fecha de creación.
    
    Query Parameters:
        page (int): Número de página (default: 1)
        search (str): Término de búsqueda en el nombre
        order (str): Campo de ordenamiento ('name' o 'created_at')
        direction (str): Dirección del ordenamiento ('asc' o 'desc')
    
    Returns:
        render_template: Página con la lista de tags paginada
    """
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
    """
    Maneja la creación de nuevos tags.
    
    GET: Muestra el formulario de creación de tags.
    POST: Procesa el formulario y crea el tag tras validar nombre y unicidad.
    
    Returns:
        GET: render_template con el formulario de creación
        POST: redirect a la lista de tags tras crear exitosamente
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        current_user_id = session.get("user_id")
        
        # LOG: Inicio de creación
        logger.info(f"Usuario {current_user_id} intentando crear tag: '{name}'")
        
        # Validar y crear tag usando función auxiliar
        tag, error_msg = validate_and_create_tag(name)
        
        if error_msg:
            # LOG: Error de validación
            logger.warning(f"Error validando tag: {error_msg}")
            flash(error_msg, "danger")
            return render_template("tags/create.html")
        
        # Guardar en base de datos
        db.session.add(tag)
        db.session.commit()
        
        # LOG: Éxito
        logger.info(f"Tag creado exitosamente: ID={tag.id}, nombre='{tag.name}', slug='{tag.slug}'")
        
        flash("Tag creado correctamente.", "success")
        return redirect(url_for("tags.index"))
    
    return render_template("tags/create.html")

@tags_blueprint.route("/<int:tag_id>/edit", methods=["GET", "POST"])
@login_required
@require_role(['Administrador', 'Editor'])
def edit(tag_id):
    """
    Maneja la edición de tags existentes.
    
    GET: Muestra el formulario de edición con los datos del tag.
    POST: Procesa los cambios y actualiza el tag tras validar nombre y unicidad.
    
    Args:
        tag_id (int): ID del tag a editar
        
    Returns:
        GET: render_template con el formulario de edición
        POST: redirect a la lista de tags tras actualizar exitosamente
        
    Raises:
        404: Si el tag no existe
    """
    tag = Tag.query.get_or_404(tag_id)
    current_user_id = session.get("user_id")
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        
        # LOG: Inicio de edición
        logger.info(f"Usuario {current_user_id} editando tag ID={tag_id}: '{tag.name}' -> '{name}'")
        
        # Validar y actualizar tag usando función auxiliar
        success, error_msg = validate_and_update_tag(tag, name)
        
        if not success:
            # LOG: Error de validación
            logger.warning(f"Error validando tag en edición: {error_msg}")
            flash(error_msg, "danger")
            return render_template("tags/edit.html", tag=tag)
        
        # Guardar cambios
        db.session.commit()
        
        # LOG: Éxito
        logger.info(f"Tag editado exitosamente: ID={tag_id}, nuevo_nombre='{tag.name}', nuevo_slug='{tag.slug}'")
        
        flash("Tag actualizado correctamente.", "success")
        return redirect(url_for("tags.index"))
    
    return render_template("tags/edit.html", tag=tag)

@tags_blueprint.route("/<int:tag_id>/delete", methods=["POST"])
@login_required
@require_role(['Administrador', 'Editor'])
def delete(tag_id):
    """
    Elimina un tag de la base de datos.
    
    Verifica que el tag no esté asociado a ningún sitio antes de eliminarlo.
    
    Args:
        tag_id (int): ID del tag a eliminar
    
    Returns:
        redirect: Redirección a la lista de tags
        
    Raises:
        404: Si el tag no existe
    
    Note:
        No se puede eliminar un tag que esté asociado a sitios históricos.
    """
    tag = Tag.query.get_or_404(tag_id)
    current_user_id = session.get("user_id")
    
    # LOG: Inicio de eliminación
    logger.info(f"Usuario {current_user_id} intentando eliminar tag ID={tag_id}: '{tag.name}'")
    
    if tag.site_associations.count() > 0:  
        # LOG: Error por dependencias
        logger.warning(f"No se puede eliminar tag ID={tag_id} porque tiene {tag.site_associations.count()} sitios asociados")
        flash("No se puede eliminar el tag porque está asignado a uno o más sitios.", "danger")
        return redirect(url_for("tags.index"))
    
    # LOG: Eliminación exitosa
    logger.info(f"Tag eliminado exitosamente: ID={tag_id}, nombre='{tag.name}', slug='{tag.slug}'")
    
    db.session.delete(tag)
    db.session.commit()
    flash("Tag eliminado correctamente.", "success")
    return redirect(url_for("tags.index"))

@tags_blueprint.route("/<int:tag_id>", methods=["GET"])
@login_required
@require_role(['Administrador', 'Editor'])
def detail(tag_id):
    """
    Muestra el detalle de un tag específico.
    
    Args:
        tag_id (int): ID del tag a mostrar
    
    Returns:
        render_template: Página con los detalles del tag
        
    Raises:
        404: Si el tag no existe
    """
    tag = Tag.query.get_or_404(tag_id)
    return render_template("tags/detail.html", tag=tag)