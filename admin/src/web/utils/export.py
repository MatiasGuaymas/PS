import csv
from datetime import datetime
from io import StringIO

def export_sites_to_csv(sites):
    """
    Exporta sitios históricos a formato CSV según los requisitos del enunciado.
    """
    output = StringIO()

    # Definir columnas mínimas requeridas
    fieldnames = [
        "ID",
        "Nombre",
        "Descripción Breve",
        "Ciudad",
        "Provincia",
        "Estado de Conservación",
        "Fecha de Registro",
        "Latitud",
        "Longitud",
        "Tags",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=",")
    writer.writeheader()

    for site in sites:
        tags_str = f"[{', '.join(assoc.tag.name for assoc in site.tag_associations)}]" if site.tag_associations else ""

        writer.writerow(
            {
                "ID": site.id,
                "Nombre": site.site_name,
                "Descripción Breve": site.short_desc,
                "Ciudad": site.city,
                "Provincia": site.province,
                "Estado de Conservación": site.state.name if site.state else "",
                "Fecha de Registro": (
                    site.registration.strftime("%Y-%m-%d %H:%M:%S")
                    if site.registration
                    else ""
                ),
                "Latitud": site.latitude,
                "Longitud": site.longitude,
                "Tags": tags_str
            }
        )
    # "\ufeff" es denominado BOM y es utilizado para que excel detecte correctamente la codificación
    content = "\ufeff" + output.getvalue()
    output.close()
    return content


def get_csv_filename():
    """Genera nombre del archivo CSV con timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"sitios_{timestamp}.csv"
