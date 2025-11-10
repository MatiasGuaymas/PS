from flask import Flask
from flask import render_template
from flask_session import Session
from flask_cors import CORS
from web.handlers import error
from core import database
from web.config import config
from web.controllers.users import user_blueprint
from web.controllers.roles import roles_blueprint
from src.web.controllers.sites import sites_blueprint
from src.web.controllers.tags import tags_blueprint
from src.web.controllers.flags import feature_flag_blueprint
from src.web.controllers.reviews import reviews_blueprint
from src.web.controllers.auth import bp as auth_bp
from src.web.handlers.auth import is_authenticated,is_superAdmin,is_granted
from .utils.hooks import hook_admin_maintenance
from .utils.helperImage import getImageUrl
from .config import get_current_config
import os
from dotenv import load_dotenv
from core import seeds
from src.web.storage import storage
load_dotenv()

session = Session()

def create_app(env = 'development', static_folder = "../../static"):

    app = Flask(__name__, static_folder=static_folder)

    app.config.from_object(get_current_config(env))

    database.init_db(app)
    session.init_app(app)
    storage.init_app(app)

    CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}}) 

    @app.route('/')
    def home():
        return render_template('home.html')
    
    # Hooks
    app.before_request(hook_admin_maintenance)


    #Blueprints
    app.register_blueprint(user_blueprint)
    app.register_blueprint(roles_blueprint)
    app.register_blueprint(sites_blueprint)
    app.register_blueprint(tags_blueprint)
    app.register_blueprint(feature_flag_blueprint)
    app.register_blueprint(reviews_blueprint)
    app.register_blueprint(auth_bp)

    #Manejo de errores
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.internal_server)
    app.register_error_handler(403, error.forbidden)
    
    # Variables globales para las plantillas
    app.jinja_env.globals.update(is_authenticated=is_authenticated)
    app.jinja_env.globals.update(is_superAdmin=is_superAdmin)
    app.jinja_env.globals.update(is_granted=is_granted)
    app.jinja_env.globals.update(getImageUrl=getImageUrl)

    # Commands
    @app.cli.command("reset-db")
    def reset_db_command():
        from core.database import reset_db

        reset_db(app)

    @app.cli.command("seed-db")
    def seed_db_command():
        import os

        from core.seeds import seed_data

        #env = os.getenv("FLASK_ENV", "production")

        seed_data()

    # Inicialización automática para producción
    with app.app_context():
        if env == "production":
            from core.database import reset_db
            from core.seeds import seed_data as seed_db
            # Borra y crea la base de datos
            reset_db(app)
            # Corre los seeds
            seed_db()
    


    return app
