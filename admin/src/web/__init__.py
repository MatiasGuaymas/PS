from flask import Flask
from flask import render_template
from src.web.handlers import error

def create_app(env = 'development', static_folder = "../../static"):

    app = Flask(__name__, static_folder=static_folder)
    
    @app.route('/')
    def home():
        return render_template('home.html')

    app.register_error_handler(404, error.not_found)

    return app
