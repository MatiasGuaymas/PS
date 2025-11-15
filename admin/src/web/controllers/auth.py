from flask import Blueprint, current_app
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from core.services.user_service import UserService 
from src.web.handlers.auth import login_required, noLogin_required
from flask import jsonify

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
    
    session["user"] = user.email
    session["user_id"] = user.id
    session["role_name"] = user.role.name if user.role else "No Role"
    session["is_admin"] = user.sysAdmin
    session["role_id"] = user.role.id if user.role else None
    
    if is_json_request():
        return jsonify({
            "ok": True,
            "message": "Login exitoso",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "avatar": user.avatar
            }
        }), 200
    else:
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
        
        origin = session.pop('oauth_origin', 'admin')
        
        flash(f"Bienvenido {name}!", "success")
        
        # ✅ Redirigir según el origen
        if origin == 'public':
            # Redirigir a la app pública (Vue)
            return redirect('http://localhost:5173/')
        else:
            # Redirigir al admin (Flask)
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
        
        vatar_url = None
        if avatar_file and avatar_file.filename:
            # Validar extensión
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            filename = secure_filename(avatar_file.filename)
            
            if '.' in filename:
                extension = filename.rsplit('.', 1)[1].lower()
                
                if extension in allowed_extensions:
                    # Generar nombre único
                    unique_filename = f"avatar_{int(time.time())}_{filename}"
                    
                    # Guardar en carpeta static/avatars
                    upload_folder = os.path.join(current_app.static_folder, 'avatars')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    filepath = os.path.join(upload_folder, unique_filename)
                    avatar_file.save(filepath)
                    
                    avatar_url = f"/static/avatars/{unique_filename}"
        

        UserService.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            raw_password=password
        )

        new_user = UserService.get_user_by_email(email)
        
        # Crear sesión automáticamente
        session["user"] = new_user.email
        session["user_id"] = new_user.id
        session["role_name"] = new_user.role.name if new_user.role else "No Role"
        session["is_admin"] = new_user.sysAdmin
        session["role_id"] = new_user.role.id if new_user.role else None
        
        return jsonify({
            "ok": True,
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500