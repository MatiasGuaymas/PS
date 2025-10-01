from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from core.services.flag_service import FlagService
from core.services.user_service import UserService
from web.utils.auth import login_required, system_admin_required

feature_flag_blueprint = Blueprint("feature-flags", __name__, url_prefix="/feature-flag")


@feature_flag_blueprint.get("/")
#@login_required
#@system_admin_required
def index():
    flags = FlagService.get_all_flags()
    return render_template("flags/index.html", flags=flags)

@feature_flag_blueprint.post("/<int:flag_id>/toggle")
@login_required
@system_admin_required
def toggle(flag_id):
    """Cambiar el estado de un flag"""
    user = UserService.get_user_by_id(session["user_id"])
    flag = FlagService.get_feature_flag_by_id(flag_id)
    new_state = not flag.is_enabled
    # Si es de tipo mantenimiento y el nuevo estado es activado y no tiene mensaje
    if flag.is_maintenance() and new_state and not flag.has_message():
        message = request.form.get("message", "").strip()
        if not message:
            flash("Debe ingresar un mensaje de mantenimiento", "error")
            return redirect(url_for("feature-flags.index"))
        if len(message) > 255:
            flash("El mensaje no puede superar los 255 caracteres", "error")
            return redirect(url_for("feature-flags.index"))
        FlagService.set_maintenance_message(flag_id, message)

    FlagService.toggle_feature_flag(flag_id, new_state, user)
    flash(
        f"Flag '{flag.description}' cambiado a {'ON' if new_state else 'OFF'}",
        "success",
    )
    return redirect(url_for("feature-flags.index"))
