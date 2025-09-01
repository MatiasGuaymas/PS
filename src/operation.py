def division(a, b):
    """Retorna el resultado de la división de a entre b."""
    if b == 0:
        raise ValueError("No se puede dividir por 0.")
    return a / b