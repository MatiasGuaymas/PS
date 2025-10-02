from flask import Flask
from flask import render_template
from flask_session import Session

from web.handlers import error
from core import database
from web.config import config
from web.controllers.users import user_blueprint
from web.controllers.roles import roles_blueprint
from src.web.controllers.sites import sites_blueprint
from src.web.controllers.tags import tags_blueprint
from src.web.controllers.auth import bp as auth_bp
from src.web.handlers.auth import is_authenticated

import bcrypt
import os
from dotenv import load_dotenv
from core import seeds

load_dotenv()

session = Session()

def create_app(env = 'development', static_folder = "../../static"):

    app = Flask(__name__, static_folder=static_folder)

    app.config["SQLALCHEMY_ECHO"] = os.getenv("SQLALCHEMY_ECHO")
    app.config.from_object(config[env])

    database.init_db(app)
    session.init_app(app)

    with app.app_context():
        database.db.drop_all()
        database.db.create_all()
        seeds.seed_data()

    @app.route('/')
    def home():
        return render_template('home.html')
    
    app.register_blueprint(user_blueprint)
    app.register_blueprint(roles_blueprint)
    app.register_blueprint(sites_blueprint)
    app.register_blueprint(tags_blueprint)
    app.register_blueprint(auth_bp)
    
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.internal_server)
    
    app.jinja_env.globals['is_authenticated'] = is_authenticated

    return app
