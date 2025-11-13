from flask import Blueprint, render_template, request, redirect, url_for,session, flash,abort,Response, jsonify
from core.models.Site import Site
from core.database import db
from sqlalchemy.orm import selectinload
sitesAPI_blueprint = Blueprint("sitesAPI", __name__, url_prefix="/api/sites")

@sitesAPI_blueprint.route("/", methods=["GET"])
def list_sites():
    sites = db.session.query(Site).options(
        selectinload(Site.category),
        selectinload(Site.state),
        #selectinload(Site.images) 
    ).filter_by(active=True, deleted=False).all()
    sites_json = [site.to_dict() for site in sites]
    return jsonify(sites_json)