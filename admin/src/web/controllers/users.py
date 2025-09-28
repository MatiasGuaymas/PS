from flask import Blueprint, render_template, request
from core.models.User import User
from core.database import db
from sqlalchemy.orm import joinedload


user_blueprint = Blueprint("users", __name__, url_prefix="/users")


@user_blueprint.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        active = request.form.get("active") == "true" 
        sys_admin = request.form.get("sys_admin") == "true" 

        #Validaciones basicas agregar handlers
        if not first_name or not last_name or not email or not password:
            return "Missing required fields", 400
        if User.query.filter_by(email=email).first():
            return "Email already exists", 400
        

        # Crear una nueva instancia de la clase User con los datos recibidos
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
            active=active,
            sysAdmin=sys_admin,
            #falta roles
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