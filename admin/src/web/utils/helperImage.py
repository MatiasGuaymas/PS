from core.services.sites_service import SiteService
def getImageUrl(image_record):
    """
    Construye y devuelve la URL completa de una imagen basada en su registro.
    """
    if not image_record:
        return SiteService.build_image_url("/public/default_image.png")
    return SiteService.build_image_url(image_record.file_path)