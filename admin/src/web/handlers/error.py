from dataclasses import dataclass
from flask import render_template

@dataclass
class HTTPError:
  code: int
  message: str
  descrpition: str

def not_found(e):
  error = HTTPError(
    code=404,
    message="Página no encontrada",
    descrpition="Lo sentimos, la página que estás buscando no existe.",
  )
  return render_template('error.html', error=error), 404

def unauthorized(e):
  error = HTTPError(
    code=401,
    message="No autorizado",
    descrpition="Acceso denegado debido a credenciales inválidas.",
  )
  return render_template('error.html', error=error), 401

def internal_server(e):
  error = HTTPError(
    code=500,
    message="Error interno del servidor",
    descrpition="Lo sentimos, ocurrió un error, vuelva a intentarlo.",
  )
  return render_template('error.html', error=error), 500