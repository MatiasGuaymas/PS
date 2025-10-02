from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask import session
from core.models.User import User
from core.database import db
from sqlalchemy.orm import joinedload
from sqlalchemy import text
from core.models.Role import Role
from src.web.handlers.auth import is_authenticated
from src.web.handlers.auth import login_required
import bcrypt
import bcrypt


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
            return "Missing required fields", 400
        if User.query.filter_by(email=email).first():
            return "Email already exists", 400
        if len(password) < 8:
            return "Password too short", 400
        

        # Crear una nueva instancia de la clase User con los datos recibidos
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            password=hash_password(password),
            email=email,
            active=active,
            role_id=role,
            sysAdmin=False
        )
        db.session.add(new_user)
        db.session.commit()
        
        users = User.query.all()
        
        

        return render_template(
            "users/index.html", users=users
        ),201
    elif request.method == "GET":
        users = User.query.all()
        return render_template(
            "users/index.html", users=users
        )
    else:
        return "Method not allowed", 405

@user_blueprint.route("/update/<int:user_id>", methods=["GET", "POST"])
@login_required
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
        sys_admin = request.form.get("sysAdmin") == "true"
        
        if not first_name or not last_name or not email:
            return "Missing required fields", 400
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            return "Email already exists", 400
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.active = active
        user.role_id = role_id if role_id else None
        user.sysAdmin = sys_admin
        
        if password and len(password) >= 8:
            user.password = hash_password(password)
        elif password and len(password) < 8:
            return "Password too short", 400
        
        db.session.commit()

        return redirect(url_for('users.index'))
    
    else:
        return "Method not allowed", 405
    


@user_blueprint.route("/delete/<int:user_id>", methods=["GET", "POST"])
@login_required
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        db.session.execute(text("""
            DELETE FROM actions 
            WHERE audit_id IN (
                SELECT id FROM audits WHERE user_id = :user_id
            )
        """), {"user_id": user_id})
        
        db.session.execute(text("""
            DELETE FROM audits WHERE user_id = :user_id
        """), {"user_id": user_id})
        
        db.session.execute(text("""
            DELETE FROM flags WHERE user_id = :user_id
        """), {"user_id": user_id})

        db.session.delete(user)
        db.session.commit()
        
        return redirect(url_for('users.index'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar usuario: {e}")
        return f"Error al eliminar usuario: {str(e)}", 500

@user_blueprint.route("/search/", methods=["GET"])
def search_users():
    try:
        email = request.args.get('email', '').strip()
        status = request.args.get('status', '').strip()
        role = request.args.get('role', '').strip()
        
        query = User.query.options(joinedload(User.role))
        
        
        if email:
            query = query.filter(User.email.ilike(f'%{email}%'))
        
        if status:
            if status.lower() == 'active':
                query = query.filter(User.active == True)
            elif status.lower() == 'inactive':
                query = query.filter(User.active == False)
        
        if role:
            query = query.filter(User.role_id == int(role))
        
        users = query.all()
        
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
            'total': len(users_data),
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