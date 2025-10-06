from functools import wraps
from flask import session, redirect, url_for, flash, abort
from src.core.services.flag_service import FlagService

def is_authenticated(session):
    return session.get("user") is not None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated(session):
            flash("Debes iniciar sesión para acceder a esta página.", "danger")
        return f(*args, **kwargs)
    return decorated_function


def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if ((not session.get("is_admin") and session.get("role_name") not in allowed_roles)):
                flash("No tienes permiso para acceder a esta funcionalidad.", "danger")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def noLogin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_authenticated(session):
            flash("Ya has iniciado sesión.", "info")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def system_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            abort(401)

        if not session.get('is_admin'):
            abort(403)

        return f(*args, **kwargs)

    return decorated_function
