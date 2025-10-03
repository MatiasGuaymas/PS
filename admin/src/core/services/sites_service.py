from src.web.utils.pagination import paginate_query
from core.models.Site import Site

def get_sites_filtered(
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

    if paginate:
        return paginate_query(
            Site, page=page, per_page=per_page, order_by=order_by, sorted_by=sorted_by
        )
    else:
        return Site.all()
