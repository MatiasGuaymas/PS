from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash, session
from src.core import auth
import bcrypt

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/")
def login():
    return render_template("auth/login.html")


@bp.post("/authenticate")
def authenticate():
    params = request.form
    user = auth.find_user(params.get("email"), params.get("password"))
    if not user:
        return redirect(url_for("auth.login"))
    
    session["user"] = user.email
    return redirect(url_for("users.index"))

    

@bp.get("/logout")
def logout():
    pass