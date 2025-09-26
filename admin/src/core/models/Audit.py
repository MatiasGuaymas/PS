from core.database import db
from sqlalchemy import Column, Integer, String, Text, DateTime,ForeignKey
from sqlalchemy import func, Boolean as bool
from sqlalchemy.orm import relationship


class Audit(db.Model):
    __tablename__ = 'audits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Mensaje o descripción de la auditoría
    message = Column(String(200), nullable=True)

    # RELACIÓN 1: Una Auditoría es realizada por un único Usuario.
    # CLAVE FORÁNEA: Columna que referencia la tabla 'users'.
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # RELACIÓN 2: una auditoria se hace a un sitio historico.
    # CLAVE FORÁNEA: Columna que referencia la tabla 'site'.
    site_id = Column(Integer, ForeignKey('site.id'), nullable=False)