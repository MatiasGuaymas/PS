from core.database import db
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy import func, Boolean as bool
from sqlalchemy.orm import relationship


class Flag(db.Model):
    __tablename__ = 'flags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), unique=True, nullable=False)
    description = Column(String(200), nullable=False)
    value = Column(bool, default=1)
    last_edit = Column(DateTime(timezone=True), server_default=func.now())
    message = Column(String(100), nullable=True)

    # RELACIÓN 1: Una Flag es modificada por un único Usuario.
    # CLAVE FORÁNEA: Columna que referencia la tabla 'users'.
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)