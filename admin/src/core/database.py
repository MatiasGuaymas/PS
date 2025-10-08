from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    configure_db(app)

    with app.app_context():
        db.create_all()
    return app


def configure_db(app):
    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()
    return app


def reset_db(app):
    "Elimina la db actual y crea todas las tablas"
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database has been reset.")