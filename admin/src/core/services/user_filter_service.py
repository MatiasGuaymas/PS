from core.models.User import User
from core.models.Tag import Tag
from core.models.Site_Tag import HistoricSiteTag
from sqlalchemy import func

def filter_and_order_users(query, filtros):
    """
    Aplica los filtros y el orden sobre el query de User.
    filtros: dict con los valores de los filtros y orden
    Retorna el query filtrado y ordenado
    """
    email = filtros.get("email")
    status = filtros.get("status")
    role = filtros.get("role")
    sort_by = filtros.get("sort_by", "created_at")
    sort_order = filtros.get("sort_order", "desc")

    # Filtros
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if status:
        query = query.filter(User.status == status)
    if role:
        query = query.filter(User.role == role)

    if sort_by == "created_at":
        order_col = User.created_at
    if sort_order == "desc":
        order_col = order_col.desc()
    else:
        order_col = order_col.asc()

    return query.order_by(order_col)