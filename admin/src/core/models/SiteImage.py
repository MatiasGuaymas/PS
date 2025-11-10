from core.database import db
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy import func, Boolean
from sqlalchemy.orm import relationship


class SiteImage(db.Model):
    """Modelo para almacenar metadatos de imágenes asociadas a sitios históricos."""
    __tablename__ = 'site_images'
    
    # Restricción:Solo pueda haber una portada (is_cover=True) por sitio.
    # Por simplicidad y rendimiento en este nivel, la validación se hace en el controller/service.

    id = Column(Integer, primary_key=True)
    
    # --- Relación con el Sitio ---
    site_id = Column(Integer, ForeignKey('sites.id', ondelete='CASCADE'), nullable=False)
    # Define la relación inversa para acceder fácilmente a las imágenes desde el sitio
    site = relationship('Site', backref=db.backref('images', lazy='dynamic'),lazy=True)

    public_url = Column(String(512), nullable=False)
    file_path = Column(String(255), nullable=False, unique=True)
    title_alt = Column(String(120), nullable=False)
    description = Column(String(255), nullable=True)
    order_index = Column(Integer, nullable=False)
    is_cover = Column(Boolean, default=False, nullable=False)
    
    # --- Timestamps ---
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())