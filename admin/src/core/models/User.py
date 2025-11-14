from core.database import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import func, Boolean
from sqlalchemy.orm import relationship


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    password = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at= Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    sysAdmin = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)
    
    # RELACIÓN 1: Un Usuario tiene un Rol.
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    
    # RELACIÓN 2: Un Usuario realiza muchas Auditorías.
    audits = relationship("Audit", backref="user", lazy=True, cascade="all, delete-orphan")

    # RELACIÓN 3: Un Usuario realiza muchas Flags Feature.
    flags = relationship("Flag", backref="user", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.email}>'
