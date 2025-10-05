def paginate_query(query, page, per_page=25, order_by="id", sorted_by="asc",url_params=None):
    """
    Pagina una query de SQLAlchemy

    Args:
        query: Query de SQLAlchemy
        page: Número de página (base 1)
        per_page: Elementos por página
        order_by: Columa de la tabla por la que se ordena le paginacion (nombre, id, etc)
        sorted_by: Forma en la que se ordena la paginacion (asc o desc)
    Returns:
        dict con información de paginación
    """
    try:
        page = int(page) if page else 1
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "items": pagination.items,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": pagination.per_page,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
        "next_num": pagination.next_num,
        "prev_num": pagination.prev_num,
        "page_range": get_page_range(pagination.page, pagination.pages),
        "order_by": order_by,
        "sorted_by": sorted_by,
    }


def get_page_range(current_page, total_pages, delta=2):
    """Obtiene el rango de páginas para mostrar en la paginación"""
    if total_pages <= 2 * delta + 1:
        return list(range(1, total_pages + 1))

    if current_page <= delta + 1:
        return list(range(1, 2 * delta + 2))

    if current_page >= total_pages - delta:
        return list(range(total_pages - 2 * delta, total_pages + 1))

    return list(range(current_page - delta, current_page + delta + 1))