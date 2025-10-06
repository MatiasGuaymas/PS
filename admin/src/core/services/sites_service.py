from core.utils.pagination import paginate_query
from core.models.Site import Site
from core.models.Audit import Audit
from core.database import db
from core.utils.search import build_search_query,apply_ordering
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