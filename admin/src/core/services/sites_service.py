from core.utils.pagination import paginate_query
from core.models.Site import Site
from core.models.SiteImage import SiteImage
from core.models.Audit import Audit
from core.database import db
from core.utils.search import build_search_query,apply_ordering
import logging
logger = logging.getLogger(__name__)
class SiteService:
    def get_sites_filtered(
        filters=None,
        order_by: str = "name",
        sorted_by: str = "asc",
        paginate: bool = True,
        page: int = 1,
        per_page: int = 25,
    ):
        """
        Devuelve sitios históricos filtrados, ordenados y opcionalmente paginados.
        Usa GenericSearchBuilder para filtros    y paginate_query para paginación.

        Args:
            filters (dict): filtros a aplicar (ej: {"city_id": 1, "visible": True})
            order_by (str): columna para ordenar
            sorted_by (str): 'asc' o 'desc'
            paginate (bool): si True devuelve dict con paginación, si False lista completa
            page (int): número de página (si paginate=True)
            per_page (int): tamaño de página (si paginate=True)

        Returns:
            dict de paginación o lista de objetos HistoricSite
        """
        filters = filters or {}
        # Siempre filtrar los sitios no eliminados
        filters['deleted'] = False

        # --- Filtrado por tags (muchos a muchos) ---
        tags = filters.pop('tags', None)

        # Construir query base
        query = build_search_query(Site, filters)

        # Filtrado por tags: solo sitios que tengan TODOS los tags seleccionados
        if tags:
            tag_ids = []
            # Normalización
            if isinstance(tags, (list, tuple)):
                tag_ids = [int(t) for t in tags if str(t).isdigit()]
            elif isinstance(tags, str) and tags.isdigit():
                tag_ids = [int(tags)]
            """
            Si tag_ids tiene valores, se hace un JOIN con la tabla de asociación y
            se filtran los sitios que tengan esos tags. Luego, se agrupa por sitio y se usa
            HAVING para asegurarse que el conteo de tags coincida con la cantidad de tags
            solicitados (es decir, que el sitio tenga todos los tags).
            """
            if tag_ids:
                from core.models.Site_Tag import HistoricSiteTag
                from sqlalchemy import func
                query = query.join(Site.tag_associations)
                query = query.filter(HistoricSiteTag.tag_id.in_(tag_ids))
                query = query.group_by(Site.id)
                query = query.having(func.count(HistoricSiteTag.tag_id) == len(tag_ids))

        # Ordenar
        query = apply_ordering(query, Site, order_by, sorted_by)
        if paginate:
            return paginate_query(
                query, page=page, per_page=per_page, order_by=order_by, sorted_by=sorted_by
            )
        else:
            return query.all()

    def _register_audit_log(site_id: int, user_id: int, action_type: str, description: str, details: str = None):
            """Función interna para crear un registro de auditoría."""
            try:
                log = Audit(
                    site_id=site_id,
                    user_id=user_id,
                    action_type=action_type,
                    description=description,
                    details=details
                )
                db.session.add(log)

            except Exception as e:
                print(f"Error al registrar auditoría: {e}") 
                # Continuamos sin levantar excepción, el registro de historial no debe bloquear la operación principal
                pass

    def get_site_by_id(id: int):
        """Devuelve una Site en base al id"""
        return db.session.get(Site, id)
    

    def get_audit_filtered(
        historical_site_id: int,  
        filters = None,
        order_by: str = "created_at", 
        sorted_by: str = "desc",  
        paginate: bool = True,
        page: int = 1,
        per_page: int = 25,
    ):
        """
        Devuelve Auditorías filtradas para un HistoricalSite específico, ordenadas y opcionalmente paginadas.

        Args:
            historical_site_id (int): ID del sitio histórico al que pertenecen las auditorías.
            filters (dict): filtros adicionales a aplicar (ej: {"user_id": 1, "action_type": "CREATE"})
            order_by (str): columna para ordenar (por defecto "created_at")
            sorted_by (str): 'asc' o 'desc' (por defecto "desc")
            paginate (bool): si True devuelve dict con paginación, si False lista completa
            page (int): número de página (si paginate=True)
            per_page (int): tamaño de página (si paginate=True)

        Returns:
            dict de paginación o lista de objetos Audit
        """
        filters = filters or {}

        # 1. Asegurar el filtro por el sitio histórico
        filters['site_id'] = historical_site_id 

        # 2. Construir query con filtros genéricos
        query = build_search_query(Audit, filters)

        # 3. Ordenar (por defecto: created_at descendente)
        query = apply_ordering(query, Audit, order_by, sorted_by)

        if paginate:
            return paginate_query(
                query, page=page, per_page=per_page, order_by=order_by, sorted_by=sorted_by
            )
        else:
            return query.all()
        
    def get_site_images_count(site_id: int) -> int:
        """
        Obtiene el número total de imágenes asociadas a un sitio.
        
        Args:
            site_id (int): ID del sitio.
            
        Returns:
            int: Cantidad de imágenes.
        """
        return db.session.query(SiteImage).filter_by(site_id=site_id).count()

    def get_cover_image(site_id: int):
        """
        Obtiene el objeto SiteImage marcado como portada para un sitio.
        
        Args:
            site_id (int): ID del sitio.
            
        Returns:
            SiteImage | None: La imagen de portada o None si no se encuentra.
        """
        return db.session.query(SiteImage).filter_by(site_id=site_id, is_cover=True).first()

    def get_next_image_order(site_id: int) -> int:
        """
        Calcula el siguiente índice de orden disponible para una nueva imagen.
        
        Args:
            site_id (int): ID del sitio.
            
        Returns:
            int: El máximo order_index actual + 1, o 1 si no hay imágenes.
        """
        # Encuentra el máximo order_index para el sitio
        max_order = db.session.query(db.func.max(SiteImage.order_index)).filter(SiteImage.site_id == site_id).scalar()
        
        # Si no hay imágenes, el siguiente orden es 1. De lo contrario, max + 1.
        return (max_order or 0) + 1

    # --- MÉTODOS DE MANIPULACIÓN (Lógica de Negocio) ---

    def reorder_image(site_id: int, image_id: int, new_index: int) -> bool:
        """
        Ajusta el índice de orden de una imagen y reajusta las demás si es necesario.
        
        Args:
            site_id (int): ID del sitio.
            image_id (int): ID de la imagen a mover.
            new_index (int): La nueva posición deseada (empezando en 1).
            
        Returns:
            bool: True si la operación fue exitosa.
        """
        try:
            # 1. Obtener la imagen que se va a mover y su orden actual
            image_to_move = db.session.query(SiteImage).filter_by(id=image_id, site_id=site_id).first()
            if not image_to_move:
                logger.warning(f"Intento de reordenar imagen ID={image_id} que no existe en sitio ID={site_id}.")
                return False
                
            old_index = image_to_move.order_index
            
            # 2. Obtener el rango de movimiento
            # Si se mueve hacia abajo (old < new): Desplazar imágenes old < index <= new hacia atrás (index - 1)
            if old_index < new_index:
                db.session.query(SiteImage) \
                    .filter(SiteImage.site_id == site_id, 
                            SiteImage.order_index > old_index,
                            SiteImage.order_index <= new_index) \
                    .update({SiteImage.order_index: SiteImage.order_index - 1}, synchronize_session='fetch')

            # Si se mueve hacia arriba (old > new): Desplazar imágenes new <= index < old hacia adelante (index + 1)
            elif old_index > new_index:
                 db.session.query(SiteImage) \
                    .filter(SiteImage.site_id == site_id, 
                            SiteImage.order_index >= new_index,
                            SiteImage.order_index < old_index) \
                    .update({SiteImage.order_index: SiteImage.order_index + 1}, synchronize_session='fetch')
            
            # 3. Asignar el nuevo índice a la imagen movida
            if old_index != new_index:
                image_to_move.order_index = new_index
                db.session.commit()
                logger.info(f"Imagen ID={image_id} reordenada de {old_index} a {new_index} en sitio {site_id}.")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al reordenar imagen ID={image_id} para sitio {site_id}: {e}", exc_info=True)
            return False

    def set_cover_image(site_id: int, image_id: int) -> bool:
        """
        Establece una imagen específica como portada del sitio, desmarcando la anterior.
        
        Args:
            site_id (int): ID del sitio.
            image_id (int): ID de la imagen a establecer como portada.
            
        Returns:
            bool: True si la operación fue exitosa.
        """
        try:
            # 1. Desmarcar todas las portadas actuales del sitio
            db.session.query(SiteImage) \
                .filter(SiteImage.site_id == site_id, SiteImage.is_cover == True) \
                .update({SiteImage.is_cover: False}, synchronize_session=False)

            # 2. Marcar la nueva imagen como portada
            db.session.query(SiteImage).filter(
                            SiteImage.id == image_id, 
                            SiteImage.site_id == site_id
                        ).update({SiteImage.is_cover: True}, synchronize_session='fetch')
            
            db.session.commit()
            logger.info(f"Imagen ID={image_id} establecida como portada para sitio {site_id}.")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al establecer imagen ID={image_id} como portada: {e}", exc_info=True)
            return False
    
    def process_new_images_transactional(site_id, image_data):
        """
        Procesa un lote de nuevas imágenes: las valida, sube a MinIO y crea registros en BD.
        
        Args:
            site_id (int): ID del sitio al que pertenecen las imágenes.
            image_data (list): Lista de dicts con {"file": file_obj, "title_alt": "...", "description": "..."}.
            
        Returns:
            int: Número de imágenes procesadas con éxito.
        """
        from flask import current_app
        import os
        import uuid

        if not image_data:
            return 0

        client = current_app.storage
        images_processed = 0

        # Pre-cálculos una sola vez
        next_order = SiteService.get_next_image_order(site_id)
        is_first_image_for_site = (SiteService.get_cover_image(site_id) is None)
        for idx, img_info in enumerate(image_data):
            file = img_info["file"]
            titulo_alt = img_info["title_alt"]
            descripcion = img_info["description"]

            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            extension = file.filename.rsplit('.', 1)[1].lower()
            file_uuid = str(uuid.uuid4())
            # Guardar en una subcarpeta con el site_id en MinIO
            minio_path = f"{site_id}/{file_uuid}.{extension}"
            print(current_app)
            try:
                #no hace falta guardar res, esta para deputar errores
                res= client.put_object(bucket_name = current_app.config["MINIO_BUCKET"],
                                    object_name=minio_path,
                                    data=file,
                                    length=file_size,
                                    content_type=file.content_type)
                public_url = f"/{current_app.config['MINIO_BUCKET']}/{minio_path}"
                
                # La primera imagen subida será la portada por defecto
                is_cover = (idx == 0 and is_first_image_for_site)

                new_image = SiteImage(
                    site_id=site_id,
                    public_url=public_url,
                    file_path=minio_path,
                    title_alt=titulo_alt,
                    description=descripcion,
                    order_index=(idx + next_order), # El orden inicial es secuencial
                    is_cover=is_cover
                )
                db.session.add(new_image)
                db.session.flush()
                #TO-? Registrar auditoría
                images_processed += 1
            except Exception as e:
                logger.error(f"Error al subir imagen para sitio ID={site_id}: {e}", exc_info=True)
                continue
        return images_processed
    
    def delete_image_transactional(site_id, image_id, current_user_id):
        """
        Elimina una imagen del sitio (requiere no ser portada), de MinIO y de la BD.
        
        Returns:
            bool: True si se eliminó, False si falló la validación o la eliminación.
        """
        from flask import current_app
        image_to_delete = db.session.query(SiteImage).filter_by(id=image_id, site_id=site_id).first()
        if not image_to_delete:
            return False

        if image_to_delete.is_cover:
            raise ValueError("No se puede eliminar la imagen de portada. Por favor, marque otra imagen como portada primero.")
            
        image_title = image_to_delete.title_alt
        image_filepath = image_to_delete.file_path

        try:
            # 1. Eliminar de MinIO
            current_app.storage.delete_file(image_filepath) # Asumo que tienes una forma de acceder al storage

            # 2. Eliminar de la Base de Datos
            db.session.delete(image_to_delete)
            
            # 3. Registrar auditoría
            SiteService._register_audit_log(
                user_id=current_user_id,
                site_id=site_id,
                action_type='UPDATE',
                description=f"Se eliminó la imagen '{image_title}' (ID: {image_id})."
            )
            # El commit será manejado por la vista o se hace commit aquí si se usa solo
            
            return True
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al eliminar imagen de MinIO/BD para sitio {site_id}, imagen {image_id}: {e}")
            # Relanzar la excepción para que la vista pueda dar un mensaje de error
            raise Exception("Ocurrió un error al intentar eliminar la imagen.")
        
    def build_image_url(site_id: int, image_path: int):
        from flask import current_app
        """
        Obtiene una imagen específica de un sitio.
        
        Args:
            site_id (int): ID del sitio.
            image_path: Path de la imagen.
            
        Returns:
            SiteImage | None: La imagen solicitada o None si no se encuentra.
        """
        client = current_app.storage
        return client.presigned_get_object(
            bucket_name=current_app.config["MINIO_BUCKET"],
            object_name=image_path,
        )