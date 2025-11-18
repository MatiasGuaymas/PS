from flask import Blueprint, current_app, make_response
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from core.services.user_service import UserService 
from src.web.handlers.auth import login_required, noLogin_required
from src.web.utils.jwt_utils import (
    create_access_token, 
    create_refresh_token, 
    decode_token,
    jwt_required,
    get_token_from_request
)

bp = Blueprint("auth", __name__, url_prefix="/auth")

def is_json_request():
    """Detecta si la petición espera JSON (desde Vue) o HTML (desde Jinja2)"""
    return request.accept_mimetypes.best == 'application/json' or \
        request.is_json or \
        request.headers.get('Content-Type') == 'application/json'


@bp.get("/")
@noLogin_required
def login():
    return render_template("auth/login.html")


@bp.post("/authenticate")
def authenticate():
    """Autentica usuario - Soporta tanto JSON (Vue) como Form (Jinja2)"""
    params = request.form
    email = params.get("email")
    password = params.get("password")
    
    if not email or not password:
        if is_json_request():
            return jsonify({"error": "Email y contraseña son requeridos"}), 400
        else:
            flash("Email y contraseña son requeridos", "error")
            return redirect(url_for("auth.login"))
    
    user = UserService.authenticate_user(email, password)
    
    if not user:
        if is_json_request():
            return jsonify({"error": "Credenciales inválidas"}), 401
        else:
            flash("Credenciales inválidas", "error")
            return redirect(url_for("auth.login"))
    
    if not user.active:
        if is_json_request():
            return jsonify({"error": "Usuario desactivado"}), 403
        else:
            flash("El usuario no está activo.", "error")
            return redirect(url_for("auth.login"))
    
    if is_json_request():
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.name if user.role else None,
            is_admin=user.sysAdmin
        )
        
        refresh_token = create_refresh_token(user_id=user.id)
        
        response = make_response(jsonify({
            "ok": True,
            "message": "Login exitoso",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "avatar": user.avatar,
                "role": user.role.name if user.role else None,
                "is_admin": user.sysAdmin
            }
        }), 200)

        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3600,
            path='/'  # ✅ AGREGAR
        )
        
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=2592000,
            path='/'  # ✅ AGREGAR
        )
        
        return response

    else:
        session["user"] = user.email
        session["user_id"] = user.id
        session["role_name"] = user.role.name if user.role else "No Role"
        session["is_admin"] = user.sysAdmin
        session["role_id"] = user.role.id if user.role else None
        
        flash("Has iniciado sesión correctamente", "success")
        return redirect(url_for("home"))



@bp.get("/login-google")
@noLogin_required
def login_google():
    """Inicia el flujo OAuth con Google"""
    origin = request.args.get('origin', 'admin')
    session['oauth_origin'] = origin
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
        
        user_info = token.get('userinfo')
        
        if not user_info:
            resp = oauth.google.get('https://www.googleapis.com/oauth2/v3/userinfo')
            user_info = resp.json()
        
        email = user_info.get('email')
        name = user_info.get('name')
        avatar = user_info.get('picture')
        
        user = UserService.find_or_create_google_user(email, name, avatar)
        
        if not user:
            flash(f"No existe una cuenta con el email {email}", "error")
            return redirect(url_for("auth.login"))
        
        if not user.active:
            flash("El usuario no está activo.", "error")
            return redirect(url_for("auth.login"))
        
        origin = session.pop('oauth_origin', 'admin')
        
        # ✅ Si es para la app pública (Vue), crear JWT
        if origin == 'public':
            access_token = create_access_token(
                user_id=user.id,
                email=user.email,
                role=user.role.name if user.role else None,
                is_admin=user.sysAdmin
            )
            
            refresh_token = create_refresh_token(user_id=user.id)
            
            if (current_app.config['DEBUG']):
                response = make_response(redirect('http://localhost:5173/'))
            else:
                response = make_response(redirect('https://admin-grupo21.proyecto2025.linti.unlp.edu.ar/'))
            
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=3600,
                path='/',
                domain=None
            )
            
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=2592000,
                path='/',
                domain=None
            )
            
            return response
        else:
            # ✅ Si es para admin (Flask), usar sesión tradicional
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


    

@bp.route("/logout", methods=["GET", "POST"])
def logout():
    """Cierra sesión - Soporta JWT y Session"""
    
    # Detectar si es petición JSON (Vue)
    is_json = (
        request.accept_mimetypes.best == 'application/json' or 
        request.is_json or 
        request.headers.get('Content-Type') == 'application/json' or
        request.headers.get('Accept') == 'application/json'
    )
    
    if is_json:
        response = make_response(jsonify({
            "ok": True,
            "message": "Sesión cerrada correctamente"
        }), 200)
        
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3600,
            path='/'
        )
        
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=2592000,
            path='/' 
        )
        
        
        return response
    else:
        # Logout tradicional con sesiones (Jinja2)
        print("🚪 LOGOUT desde Jinja2")
        session.clear()
        flash("Has cerrado sesión correctamente.", "success")
        return redirect(url_for("auth.login"))

@bp.get("/me")
@jwt_required
def me():
    """Endpoint para verificar sesión activa"""
    
    try:
        # Los datos del usuario están en request.current_user (agregados por el decorador)
        user_data = request.current_user
        user_id = user_data['user_id']
        
        user = UserService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.name if user.role else None,
            "is_admin": user.sysAdmin,
            "avatar": user.avatar
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bp.post("/register")
def register():
    """Registra un nuevo usuario"""
    try:

        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form
            avatar_file = request.files.get('avatar')
        else:
            data = request.get_json() if request.is_json else request.form
            avatar_file = None
        
        # Validar campos requeridos
        required_fields = ['first_name', 'last_name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"El campo {field} es requerido"}), 400
        
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        # Validar longitud de contraseña
        if len(password) < 8:
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400
        
        # Verificar si el email ya existe
        existing_user = UserService.get_user_by_email(email)
        if existing_user:
            return jsonify({"error": "Este correo electrónico ya está registrado"}), 409
        

        UserService.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            raw_password=password,
            avatar=avatar_file
        )

        new_user = UserService.get_user_by_email(email)
        
        access_token = create_access_token(
            user_id=new_user.id,
            email=new_user.email,
            role=new_user.role.name if new_user.role else None,
            is_admin=new_user.sysAdmin
        )
        
        refresh_token = create_refresh_token(user_id=new_user.id)
        
        response = make_response(jsonify({
            "ok": True,
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "avatar": new_user.avatar
            }
        }), 201)
        
        # ✅ Establecer cookies JWT
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3600
        )
        
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=2592000
        )
        
        return response
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.post("/refresh")
def refresh():
    """Renueva el access token usando el refresh token"""
    refresh_token = request.cookies.get('refresh_token')
    
    if not refresh_token:
        return jsonify({"error": "Refresh token no proporcionado"}), 401
    
    payload = decode_token(refresh_token)
    
    if not payload or payload.get('type') != 'refresh':
        return jsonify({"error": "Refresh token inválido o expirado"}), 401
    
    user_id = payload.get('user_id')
    user = UserService.get_user_by_id(user_id)
    
    if not user or not user.active:
        return jsonify({"error": "Usuario no encontrado o inactivo"}), 404
    
    # Crear nuevo access token
    new_access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.name if user.role else None,
        is_admin=user.sysAdmin
    )
    
    response = make_response(jsonify({
        "ok": True,
        "message": "Token renovado"
    }), 200)
    
    response.set_cookie(
        'access_token',
        new_access_token,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=3600
    )
    
    return response