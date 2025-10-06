from dataclasses import dataclass
from flask import render_template,url_for


@dataclass
class HTTPError:
  code: int
  message: str
  descrpition: str
  image:str

def not_found(e):
  error = HTTPError(
    code=404,
    message="Página no encontrada",
    descrpition="Lo sentimos, la página que estás buscando no existe.",
    image=url_for('static', filename='img/error404.png')
  )
  return render_template('error.html', error=error), 404

def unauthorized(e):
  error = HTTPError(
    code=401,
    message="No autorizado",
    descrpition="Acceso denegado debido a credenciales inválidas.",
    image=url_for('static', filename='img/penguin_secret.png')
  )
  return render_template('error.html', error=error), 401

def internal_server(e):
  error = HTTPError(
    code=500,
    message="Error interno del servidor",
    descrpition="Lo sentimos, ocurrió un error, vuelva a intentarlo.",
    image=url_for('static', filename='img/error500.png')
  )
  return render_template('error.html', error=error), 500

def forbidden(e):
  error = HTTPError(
    code=403,
    message="Permisos insuficientes",
    descrpition="Lo sentimos, no cuentas con los permisos de seguridad para ingresar.",
    image=url_for('static', filename='img/penguin_secret.png')
  )
  return render_template('error.html', error=error), 403