from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash, session
from core.services.user_service import UserService 

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/")
def login():
    return render_template("auth/login.html")


@bp.post("/authenticate")
def authenticate():
    params = request.form
    user = UserService.authenticate_user(params.get("email"), params.get("password"))
    if not user:
        flash("Credenciales incorrectas", "danger")
        return redirect(url_for("auth.login"))
    
    session["user"] = user.email
    flash("Has iniciado sesión correctamente", "success")
    return redirect("/")

    

@bp.get("/logout")
def logout():
    if session.get("user"):
        session.pop("user")
        session.clear()
        flash("Has cerrado sesión correctamente.", "success")
    else:
        flash("No hay ninguna session iniciada.", "danger")
    return redirect(url_for("auth.login"))
    