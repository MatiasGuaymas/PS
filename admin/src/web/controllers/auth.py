from flask import Blueprint, current_app
from flask import render_template, request, redirect, url_for, flash, session
from core.services.user_service import UserService 
from src.web.handlers.auth import login_required, noLogin_required
from flask import jsonify

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/")
@noLogin_required
def login():
    return render_template("auth/login.html")


@bp.post("/authenticate")
def authenticate():
    params = request.form
    user = UserService.authenticate_user(params.get("email"), params.get("password"))

    if not user:
        flash("Credenciales invalidas", "error")
        return redirect(url_for("auth.login"))
    
    if not user.active:
        flash("El usuario no está activo.", "error")
    
    session["user"] = user.email
    session["user_id"] = user.id
    session["role_name"] = user.role.name if user.role else "No Role"
    session["is_admin"] = user.sysAdmin
    session["role_id"] = user.role.id if user.role else None

    print(user.id)
    flash("Has iniciado sesión correctamente", "success")
    return redirect(url_for("home"))


@bp.get("/login-google")
@noLogin_required
def login_google():
    """Inicia el flujo OAuth con Google"""
    oauth = current_app.oauth
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route("/callback")
@noLogin_required
def callback():
    """Callback de Google OAuth - Procesa la respuesta de Google"""
    try:
        oauth = current_app.oauth
        token = oauth.google.authorize_access_token()
        
        # Obtener información del usuario desde Google
        user_info = token.get('userinfo')
        
        if not user_info:
            # Si no viene en el token, hacer una petición adicional
            resp = oauth.google.get('https://www.googleapis.com/oauth2/v3/userinfo')
            user_info = resp.json()
        
        email = user_info.get('email')
        name = user_info.get('name')
        avatar = user_info.get('picture')
        
        # Buscar o crear usuario en tu base de datos
        user = UserService.find_or_create_google_user(email, name, avatar)
        
        if not user:
            flash(f"No existe una cuenta con el email {email}", "error")
            return redirect(url_for("auth.login"))
        
        if not user.active:
            flash("El usuario no está activo.", "error")
            return redirect(url_for("auth.login"))
        
        session["user"] = user.email
        session["user_id"] = user.id
        session["role_name"] = user.role.name if user.role else "No Role"
        session["is_admin"] = user.sysAdmin
        session["role_id"] = user.role.id if user.role else None
        
        flash(f"Bienvenido {name}!", "success")
        return redirect(url_for("home"))
        
    except Exception as e:
        flash(f"Error al iniciar sesión con Google: {str(e)}", "error")
        return redirect(url_for("auth.login"))

    

@bp.get("/logout")
@login_required
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for("auth.login"))
    

@bp.get("/me")
def me():
    """Endpoint para verificar sesión activa"""
    if "user_id" not in session:
        return jsonify({"error": "No authenticated"}), 401
    
    try:
        user = UserService.get_user_by_id(session["user_id"])
        
        if not user:
            session.clear()
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.name if user.role else None,
            "is_admin": user.sysAdmin,
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500