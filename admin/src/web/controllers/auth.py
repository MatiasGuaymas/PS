from flask import Blueprint
from flask import render_template

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/")
def login():
    return render_template("auth/login.html")

@bp.post("/authenticate")
def authenticate():
    pass

@bp.get("/logout")
def logout():
    pass