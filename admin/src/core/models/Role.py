from core.database import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Role(db.Model):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    # RELACIÓN 1:N: Un Rol puede ser asignado a múltiples Usuarios.
    # RELACIÓN INVERSA: Permite acceder a los usuarios asociados a este rol.
    users = relationship("User", backref="role", lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'