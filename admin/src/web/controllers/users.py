from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, g
from flask import session
from core.models.User import User
from core.database import db
from sqlalchemy.orm import joinedload
from src.web.handlers.auth import login_required, require_role, system_admin_required
from core.services.user_service import UserService 


user_blueprint = Blueprint("users", __name__, url_prefix="/users")

@user_blueprint.route("/", methods=["GET", "POST"])
@login_required
@require_role(['Administrador'])
def index():
    """
    Controlador principal para la gestión de usuarios.
    
    Maneja tanto la visualización paginada de usuarios (GET) como la creación 
    de nuevos usuarios (POST) en el sistema administrativo.
    
    Métodos HTTP soportados:
        GET: Muestra la lista paginada de usuarios con formulario de creación
        POST: Procesa la creación de un nuevo usuario con validaciones
    
    Parámetros de consulta (GET):
        page (int, opcional): Número de página para paginación. Default: 1
        
    Parámetros de formulario (POST):
        first_name (str): Nombre del usuario. Requerido.
        last_name (str): Apellido del usuario. Requerido.
        email (str): Email único del usuario. Requerido.
        password (str): Contraseña (mín. 8 caracteres). Requerida.
        active (str): Estado del usuario ('true'/'false'). Default: 'false'.
        role (str): ID del rol asignado. Requerido.
    
    Validaciones:
        - Campos obligatorios no pueden estar vacíos
        - Email debe ser único en el sistema
        - Contraseña debe tener al menos 8 caracteres
        - Debe seleccionarse un rol válido
    
    Retorna:
        GET: Renderiza 'users/index.html' con usuarios paginados (25 por página)
        POST exitoso: Redirección a la misma página con mensaje de éxito
        POST con errores: Renderiza template con mensajes de error y código 400
        
    Excepciones:
        405: Método HTTP no permitido
        
    Decoradores:
        @login_required: Requiere autenticación de usuario
        @require_role(['Administrador']): Solo acceso para administradores
        
    Ejemplo de uso:
        GET /users/ -> Lista usuarios con paginación
        POST /users/ -> Crea nuevo usuario con datos del formulario
    """
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        active = request.form.get("active") == "true" 
        role = request.form.get("role")

        #Validaciones basicas agregar handlers
        if not first_name or not last_name or not email or not password:
            flash("Faltan campos obligatorios", "error")
            users = User.query.all()
            return render_template("users/index.html", users=users), 400
        
        if not role or role.strip() == "":
            flash("Debe seleccionar un rol para el usuario", "error")
            users = User.query.all()
            return render_template("users/index.html", users=users), 400
            
            
        if User.query.filter_by(email=email).first():
            flash("El email ya existe en el sistema", "error")
            users = User.query.all()
            return render_template("users/index.html", users=users), 400
            
        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres", "error")
            users = User.query.all()
            return render_template("users/index.html", users=users), 400
        

        # Crear una nueva instancia de la clase User con los datos recibidos
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            password=UserService.hash_password(password),
            email=email,
            active=active,
            role_id=int(role),
            sysAdmin=False
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash(f"Usuario {first_name} {last_name} creado exitosamente", "success")
        return redirect(url_for('users.index'))
        
    elif request.method == "GET":
        page = request.args.get('page', 1, type=int)

        users_paginated = User.query.paginate(
            page=page,
            per_page=25,
            error_out=False
        )
        return render_template(
            "users/index.html", users=users_paginated.items, pagination=users_paginated
        )
    else:
        return "Method not allowed", 405

@user_blueprint.route("/update/<int:user_id>", methods=["GET", "POST"])
@login_required
@require_role(['Administrador'])
def update(user_id):
    """
    Controlador para actualizar datos de un usuario existente.
    
    Permite visualizar y modificar la información de un usuario específico
    identificado por su ID.
    
    Métodos HTTP soportados:
        GET: Muestra el formulario de edición con datos actuales del usuario
        POST: Procesa la actualización de datos del usuario
    
    Parámetros de ruta:
        user_id (int): ID único del usuario a actualizar. Requerido.
        
    Parámetros de formulario (POST):
        first_name (str): Nuevo nombre del usuario. Requerido.
        last_name (str): Nuevo apellido del usuario. Requerido.
        email (str): Nuevo email único del usuario. Requerido.
        password (str, opcional): Nueva contraseña (mín. 8 caracteres).
        active (str): Nuevo estado ('true'/'false'). 
        role_id (str, opcional): ID del nuevo rol asignado.
    
    Validaciones:
        - Campos obligatorios (nombre, apellido, email) no pueden estar vacíos
        - Email debe ser único (excepto para el usuario actual)
        - Si se proporciona contraseña, debe tener al menos 8 caracteres
        - Usuario debe existir en el sistema
    
    Retorna:
        GET: Renderiza 'users/update.html' con datos del usuario
        POST exitoso: Redirección a users.index con mensaje de éxito
        POST con errores: Renderiza template con mensajes de error
        404: Si el usuario no existe
        
    Excepciones:
        405: Método HTTP no permitido
        404: Usuario no encontrado
        
    Decoradores:
        @login_required: Requiere autenticación de usuario
        @require_role(['Administrador']): Solo acceso para administradores
        
    Ejemplo de uso:
        GET /users/update/5 -> Formulario para editar usuario ID 5
        POST /users/update/5 -> Actualiza datos del usuario ID 5
    """
    user = User.query.get_or_404(user_id)
    
    if request.method == "GET":
        return render_template("users/update.html", user=user)
    
    elif request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        active = request.form.get("active") == "true"
        role_id = request.form.get("role_id")
        
        if not first_name or not last_name or not email:
            flash("Faltan campos obligatorios", "error")
            return render_template("users/update.html", user=user)
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            flash("El email ya existe en el sistema", "error")
            return render_template("users/update.html", user=user)
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.active = active
        user.role_id = role_id if role_id else None
        
        if password and len(password) >= 8:
            user.password = UserService.hash_password(password)
        elif password and len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres", "error")
            return render_template("users/update.html", user=user)
        
        db.session.commit()
        flash(f"Usuario {user.first_name} {user.last_name} actualizado exitosamente", "success")
        return redirect(url_for('users.index'))
    
    else:
        return "Method not allowed", 405
    


@user_blueprint.route("/delete/<int:user_id>", methods=["GET", "POST"])
@login_required
@require_role(['Administrador'])
def delete_user(user_id):
    """
    Controlador para eliminar (soft delete) un usuario del sistema.
    
    Realiza una eliminación lógica marcando el usuario como eliminado
    en lugar de borrarlo físicamente de la base de datos.
    
    Métodos HTTP soportados:
        GET, POST: Ambos procesan la eliminación del usuario
    
    Parámetros de ruta:
        user_id (int): ID único del usuario a eliminar. Requerido.
    
    Restricciones de seguridad:
        - No permite eliminar el propio usuario (auto-eliminación)
        - No permite eliminar usuarios administradores del sistema
        - Solo administradores pueden realizar eliminaciones
    
    Lógica de eliminación:
        - Marca el campo 'deleted' como True (soft delete)
        - Mantiene la integridad referencial del sistema
        - Preserva datos para auditoría y relaciones
    
    Retorna:
        Exitoso: Redirección a users.index con mensaje de éxito
        Error de restricción: Redirección con mensaje de error específico
        Error de sistema: Redirección con mensaje de error genérico
        404: Si el usuario no existe
        
    Manejo de errores:
        - Rollback automático en caso de excepción
        - Logging de errores para debugging
        - Mensajes de error user-friendly
        
    Decoradores:
        @login_required: Requiere autenticación de usuario
        @require_role(['Administrador']): Solo acceso para administradores
        
    Ejemplo de uso:
        POST /users/delete/5 -> Elimina (soft delete) usuario ID 5
        
    Nota:
        Esta es una eliminación lógica. El usuario sigue existiendo en la
        base de datos pero está marcado como eliminado.
    """
    try:
        user = User.query.get_or_404(user_id)

        if(user.id == session.get("user_id")):
            flash("No puedes eliminar tu propio usuario", "error")
            return redirect(url_for('users.index'))

        if(user.sysAdmin):
            flash("No puedes eliminar un usuario administrador del sistema", "error")
            return redirect(url_for('users.index'))
        
        
        user.deleted = True
        db.session.commit()
        
        flash(f"Usuario {user.first_name} {user.last_name} eliminado exitosamente", "success")
        return redirect(url_for('users.index'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar usuario: {e}")
        flash(f"Error al eliminar usuario: {str(e)}", "error")
        return redirect(url_for('users.index'))

@user_blueprint.route("/search/", methods=["GET"])
@login_required
@require_role(['Administrador'])
def search_users():
    """
    API endpoint para búsqueda y filtrado avanzado de usuarios.
    
    Proporciona funcionalidad de búsqueda, filtrado, ordenamiento y paginación
    de usuarios del sistema. Retorna datos en formato JSON para consumo AJAX.
    
    Métodos HTTP soportados:
        GET: Ejecuta búsqueda con parámetros de consulta especificados
    
    Parámetros de consulta (todos opcionales):
        email (str): Búsqueda parcial por email (case-insensitive)
        status (str): Filtro por estado ('active', 'inactive')
        role (str): Filtro por ID de rol específico
        sort_by (str): Campo de ordenamiento ('id'). Default: 'id'
        sort_order (str): Dirección de orden ('asc', 'desc'). Default: 'desc'
        page (int): Número de página para paginación. Default: 1
    
    Funcionalidades:
        - Búsqueda por coincidencia parcial en email
        - Filtrado por estado de activación
        - Filtrado por rol asignado
        - Ordenamiento configurable por ID
        - Paginación con 25 usuarios por página
        - Carga optimizada de relaciones (joinedload)
        - Filtro automático de usuarios eliminados para no-admins
    
    Formato de respuesta JSON:
        {
            "success": bool,
            "users": [
                {
                    "id": int,
                    "first_name": str,
                    "last_name": str,
                    "email": str,
                    "active": bool,
                    "sysAdmin": bool,
                    "deleted": bool,
                    "created_at": str (ISO format),
                    "role": {"id": int, "name": str} | null
                }
            ],
            "pagination": {
                "page": int,
                "pages": int,
                "per_page": int,
                "total": int,
                "has_next": bool,
                "has_prev": bool,
                "next_num": int | null,
                "prev_num": int | null
            },
            "sort_by": str,
            "sort_order": str,
            "filters": {
                "email": str,
                "status": str,
                "role": str
            }
        }
    
    Retorna:
        200: JSON con resultados de búsqueda y metadatos de paginación
        500: JSON con mensaje de error en caso de excepción
        
    Optimizaciones:
        - Uso de joinedload para evitar consultas N+1
        - Paginación para limitar carga de datos
        - Filtros aplicados a nivel de base de datos
        
    Decoradores:
        @login_required: Requiere autenticación de usuario
        @require_role(['Administrador']): Solo acceso para administradores
        
    Ejemplo de uso:
        GET /users/search/?email=admin&status=active&page=2
        -> Busca usuarios con email que contenga 'admin', activos, página 2
    """
    try:
        email = request.args.get('email', '').strip()
        status = request.args.get('status', '').strip()
        role = request.args.get('role', '').strip()
        
        sort_by = request.args.get('sort_by', 'id').strip()
        sort_order = request.args.get('sort_order', 'desc').strip()
        
        query = User.query.options(joinedload(User.role))

        page = request.args.get('page', 1, type=int)
        per_page = 25

        if session.get("is_admin") == False:
            query = query.filter(User.deleted == False)

        if email:
            query = query.filter(User.email.ilike(f'%{email}%'))
        
        if status:
            if status.lower() == 'active':
                query = query.filter(User.active == True)
            elif status.lower() == 'inactive':
                query = query.filter(User.active == False)
        
        if role:
            query = query.filter(User.role_id == int(role))
        
        if sort_by == 'id':
            if sort_order == 'asc':
                query = query.order_by(User.id.asc())
            else:
                query = query.order_by(User.id.desc())

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        users = pagination.items

        users_data = []
        for user in users:
            user_data = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'active': user.active,
                'sysAdmin': user.sysAdmin,
                'deleted': user.deleted,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'role': {
                    'id': user.role.id,
                    'name': user.role.name
                } if user.role else None
            }
            users_data.append(user_data)
        
        return jsonify({
            'success': True,
            'users': users_data,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_num': pagination.next_num if pagination.has_next else None,
                'prev_num': pagination.prev_num if pagination.has_prev else None
            },
            'sort_by': sort_by,
            'sort_order': sort_order,
            'filters': {
                'email': email,
                'status': status,
                'role': role
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@user_blueprint.route("/deactivate/<int:user_id>", methods=["POST"])
@login_required
@require_role(['Administrador'])
def deactivate_user(user_id):
    try:
        user = User.query.get_or_404(user_id);

        if(user.role_id == 1):
            flash("No se puede bloquear el usuario de un administrador", "danger");
            return redirect(url_for("users.index"));
        
        user.active = not user.active;

        db.session.commit();
        
        return redirect(url_for('users.index'));
        
    except Exception as e:
        db.session.rollback();
        print(f"Error al bloquear el usuario: {e}");
        return f"Error al bloquear el usuario: {str(e)}", 500;

@user_blueprint.route("/profile", methods=["POST"])
@login_required
def view_profile():
    try:
        user_mail = request.form.get("user")
        
        if not user_mail:
            flash("Primero iniciá sesión para poder ver tu perfil", "danger");
            return redirect(url_for('auth.login'));

        user = UserService.get_user_by_email(user_mail);

        return render_template("users/profile.html", user=user)

    except Exception as e:
        return f"Ocurrió un error al cargar tu perfil: {e}", 500
    
@user_blueprint.route("/restore/<int:user_id>", methods=["POST"])
@login_required
@system_admin_required
def restore_user(user_id):
    user = UserService.get_user_by_id(user_id)
    if (user):
        user.deleted = False
        db.session.commit()
    else:
        flash("Usuario no encontrado", "warning")
    return redirect(url_for('users.index'))