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