from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    print("Initializing database...")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db


def configure_db(app):
    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def reset_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database has been reset.")