from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash, session
from core.services.user_service import UserService 
from src.web.handlers.auth import login_required, noLogin_required

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

    

@bp.get("/logout")
@login_required
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for("auth.login"))
    