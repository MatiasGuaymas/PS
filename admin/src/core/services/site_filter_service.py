from core.models.Site import Site
from core.models.Tag import Tag
from core.models.Site_Tag import HistoricSiteTag
from sqlalchemy import func

def filter_and_order_sites(query, filtros):
    """
    Aplica los filtros y el orden sobre el query de Site.
    filtros: dict con los valores de los filtros y orden
    Retorna el query filtrado y ordenado
    """
    site_name = filtros.get("site_name")
    city = filtros.get("city")
    province = filtros.get("province")
    state_id = filtros.get("state_id")
    tags = filtros.get("tags", [])
    registration_from = filtros.get("registration_from")
    registration_to = filtros.get("registration_to")
    active = filtros.get("active")
    orden = filtros.get("order_by", "site_name")
    sentido = filtros.get("sentido", "asc")

    # Filtros
    if site_name:
        query = query.filter(
            (Site.site_name.ilike(f"%{site_name}%")) |
            (Site.short_desc.ilike(f"%{site_name}%"))
        )
    if city:
        query = query.filter(Site.city == city)
    if province:
        query = query.filter(Site.province == province)
    if state_id:
        query = query.filter(Site.state_id == state_id)
    if registration_from:
        query = query.filter(Site.registration >= registration_from)
    if registration_to:
        query = query.filter(Site.registration <= registration_to)
    if active:
        query = query.filter(Site.active == True)
    if tags:
        query = query.join(Site.tag_associations)
        query = query.filter(HistoricSiteTag.tag_id.in_(tags))
        query = query.group_by(Site.id)
        query = query.having(func.count(HistoricSiteTag.tag_id) >= len(tags))

    # Orden
    if orden == "site_name":
        order_col = Site.site_name
    elif orden == "city":
        order_col = Site.city
    elif orden == "province":
        order_col = Site.province
    elif orden == "registration":
        order_col = Site.registration
    else:
        order_col = Site.site_name

    if sentido == "desc":
        order_col = order_col.desc()
    else:
        order_col = order_col.asc()

    return query.order_by(order_col)
