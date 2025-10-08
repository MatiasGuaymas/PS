from core.database import db
from sqlalchemy import Column, Integer, String, Text, DateTime,ForeignKey
from sqlalchemy import func, Boolean as bool
from sqlalchemy.orm import relationship


class Audit(db.Model):
    __tablename__ = 'audits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    action_type=Column(String(50), nullable=False)

    description = Column(Text, nullable=False)

    # Detalles especificos de la auditoría
    details = Column(Text, nullable=True)

    # RELACIÓN 1: Una Auditoría es realizada por un único Usuario.
    # CLAVE FORÁNEA: Columna que referencia la tabla 'users'.
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # RELACIÓN 2: una auditoria se hace a un sitio historico.
    # CLAVE FORÁNEA: Columna que referencia la tabla 'site'.
    site_id = Column(Integer, ForeignKey('sites.id'), nullable=False)
    site = relationship("Site", back_populates="audits")