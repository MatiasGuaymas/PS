from flask import Blueprint, render_template, request, jsonify
from core.models.Role import Role
from core.database import db
from sqlalchemy.orm import joinedload

roles_blueprint = Blueprint("roles", __name__, url_prefix="/roles")

@roles_blueprint.route("/", methods=["GET", "POST"])
def index():
    roles = Role.query.all()
    roles_data = [{"id": role.id, "name": role.name} for role in roles]
    return jsonify(roles_data)