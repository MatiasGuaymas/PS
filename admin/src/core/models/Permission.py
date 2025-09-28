from core.database import db
from sqlalchemy import Column, Integer,String,ForeignKey
from sqlalchemy.orm import relationship


class Permission(db.Model):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(70), unique=True, nullable=False)

    # RELACIÓN 1:N: Un Permiso puede estar asociado a múltiples Role_permission.
    # RELACIÓN INVERSA: Permite acceder a los role_permissions asociados a este permiso.
    role_permissions = relationship("Role_permission", backref="permission", lazy=True)