from core.services.sites_service import SiteService
def getImageUrl(image_record):
    """
    Construye y devuelve la URL completa de una imagen basada en su registro.
    """
    return SiteService.build_image_url(image_record.site_id, image_record.file_path)