from core.database import db
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy import func, Boolean as bool
from sqlalchemy.orm import relationship


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), unique=True, nullable=False)
    # Un Category puede tener muchos Site; usar back_populates para evitar backref duplicado
    sites = relationship("Site", back_populates="category", lazy=True)