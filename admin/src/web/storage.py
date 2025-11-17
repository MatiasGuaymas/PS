from minio import Minio
import io
from minio.error import S3Error
import logging
logger = logging.getLogger(__name__)
class Storage:
    def __init__(self, app=None): 
        self._client = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self._client = Minio(app.config["MINIO_SERVER"],
                            access_key=app.config["MINIO_ACCESS_KEY"],
                            secret_key=app.config["MINIO_SECRET_KEY"], 
                            secure=False,
                            )
        app.storage = self._client
        return app

    def delete_file(self, object_name):
        """
        Elimina un archivo de MinIO.

        Args:
            object_name (str): La ruta completa del archivo en el bucket.
        """
        try:
            from flask import current_app
            current_app.storage.remove_object(current_app.config['MINIO_BUCKET'], object_name)
            print("Eliminado")
            logger.info(f"Archivo {object_name} eliminado de MinIO.")
        except S3Error as e:
            logger.error(f"Error al eliminar el archivo {object_name} de MinIO: {e}")
            pass

storage = Storage()