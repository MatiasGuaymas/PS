from core.database import db
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy import func, Boolean as bool
from sqlalchemy.orm import relationship


class Tag(db.Model):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), unique=True, nullable=False)
    slug = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # RELACIÓN 1: Una Etiqueta puede estar asociada a muchos Sitios Históricos.
    # La relación es bidireccional, 'back_populates' conecta ambas tablas.
    site_associations = relationship(
        "HistoricSiteTag",
        back_populates="tag",
        lazy="dynamic"
    )