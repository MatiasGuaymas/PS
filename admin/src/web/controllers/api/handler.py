from flask import Blueprint, render_template, request, redirect, url_for,session, flash,abort,Response, jsonify
from src.core.services.flag_service import FlagService

handler_blueprint = Blueprint("handler", __name__, url_prefix="/api/handler")

@handler_blueprint.route("/", methods=["GET"])
def handler_index():
    flag = FlagService.get_flag_by_name("portal_maintenance_mode")
    if flag and flag.is_enabled:
        return jsonify({
            "status": flag.description,
            "message": flag.message
        }), 503
    return jsonify({"status": "ok"}), 200