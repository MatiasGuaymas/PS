from core.database import db
from sqlalchemy import Column, Integer, String,ForeignKey


class Action(db.Model):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(70), unique=True, nullable=False)

    # RELACIÓN 1: Una Action es realizada en una única auditoria.
    # CLAVE FORÁNEA: Columna que referencia la tabla 'audits'.
    audit_id = Column(Integer, ForeignKey('audits.id'), nullable=False)