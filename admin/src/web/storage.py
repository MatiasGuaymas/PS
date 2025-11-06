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
    
    def upload_file(self, file, object_name):
        """
        Sube un archivo cargado a MinIO.

        Args:
            file (FileStorage): Objeto de archivo de Flask/Werkzeug.
            object_name (str): La ruta completa del archivo en el bucket (ej: '123/imagen_uuid.jpg').

        Returns:
            str: La URL pública para acceder al archivo.
        """
        try:
            file_data = file.read()
            file_stream = io.BytesIO(file_data)
            file_size = len(file_data)
            file.seek(0)
            # Obtener el tipo de contenido
            content_type = file.content_type if file.content_type else 'application/octet-stream'
            # Usar el cliente inicializado
            if not self._client:
                raise Exception("Cliente de almacenamiento no inicializado")
            if not self.bucket_name:
                raise Exception("Bucket de MinIO no configurado")

            self._client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_stream,
                length=file_size,
                content_type=content_type,
            )
            return f"/{self.bucket_name}/{object_name}" 
            
        except S3Error as e:
            logger.error(f"Error al subir el archivo {object_name} a MinIO: {e}")
            raise Exception("Error en el servicio de almacenamiento al subir el archivo.")

    def delete_file(self, object_name):
        """
        Elimina un archivo de MinIO.

        Args:
            object_name (str): La ruta completa del archivo en el bucket.
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Archivo {object_name} eliminado de MinIO.")
        except S3Error as e:
            logger.error(f"Error al eliminar el archivo {object_name} de MinIO: {e}")
            # En muchos casos, no queremos que la eliminación de la DB falle
            # solo porque el archivo ya no estaba en MinIO.
            pass

storage = Storage()