from minio import Minio

class Storage:
    def __init__(self, app=None): 
        self._client = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self._client = Minio(app.config["MINIO_SERVER"],
                            access_key=app.config["MINIO_ACCESS_KEY"],
                            secret_key=app.config["MINIO_SECRET_KEY"], 
                            secure=app.config.get("MINIO_SECURE", False),
                            )
        app.storage = self._client
        return app
storage = Storage()