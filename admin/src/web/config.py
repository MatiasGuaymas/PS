import os

class config:
    TESTING = False
    SECRET_KEY = 'secret_key'
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 60,
        "pool_pre_ping": True,
    }


class ProductionConfig(config):
    """Production configuration."""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
    DEBUG=False


class DevelopmentConfig(config):
    """Development configuration."""

    DEBUG = True
    DB_USER = "proyecto_user"
    DB_PASS = "123456"
    DB_HOST = "localhost"
    DB_NAME = "proyecto"
    SESSION_TYPE = "filesystem"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
    )

class TestingConfig(config):
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_current_config(env=None):
    if env is None:
        env = os.getenv("FLASK_ENV", "production")
    return config.get(env, ProductionConfig)
