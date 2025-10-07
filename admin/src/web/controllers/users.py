from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, g
from flask import session
from core.models.User import User
from core.database import db
from sqlalchemy.orm import joinedload
from sqlalchemy import text
from core.models.Role import Role
from src.web.handlers.auth import is_authenticated
from src.web.handlers.auth import login_required, require_role
import bcrypt
import bcrypt
from core.services.user_service import UserService 


user_blueprint = Blueprint("users", __name__, url_prefix="/users")


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def verify_password(password: str, hashed: bytes) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    except Exception:
        return False

@user_blueprint.route("/", methods=["GET", "POST"])
@login_required
@require_role(['Administrador'])
def index():
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
            password=hash_password(password),
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
            user.password = hash_password(password)
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
    try:
        user = User.query.get_or_404(user_id)

        if(user.id == session.get("user_id")):
            flash("No puedes eliminar tu propio usuario", "error")
            return redirect(url_for('users.index'))

        if(user.sysAdmin):
            flash("No puedes eliminar un usuario administrador del sistema", "error")
            return redirect(url_for('users.index'))
        
        
        db.session.execute(text("""
            DELETE FROM audits WHERE user_id = :user_id
        """), {"user_id": user_id})
        
        db.session.execute(text("""
            DELETE FROM flags WHERE user_id = :user_id
        """), {"user_id": user_id})

        db.session.delete(user)
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
    try:
        email = request.args.get('email', '').strip()
        status = request.args.get('status', '').strip()
        role = request.args.get('role', '').strip()
        
        sort_by = request.args.get('sort_by', 'id').strip()
        sort_order = request.args.get('sort_order', 'desc').strip()
        
        query = User.query.options(joinedload(User.role))

        page = request.args.get('page', 1, type=int)
        per_page = 25



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