from core.database import db
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy import func, Boolean as bool
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry 
from geoalchemy2.shape import to_shape

class Site(db.Model):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_name = Column(String(50), unique=True, nullable=False)
    short_desc = Column(String(50), nullable=False)
    full_desc = Column(String(255), nullable=False)
    city = Column(String(50), nullable=False)
    province = Column(String(50), nullable=False)
    operning_year = Column(Integer, nullable=False)
    registration = Column(DateTime(timezone=True), server_default=func.now())
    active = Column(bool, default=1)
    deleted = Column(bool, default=0)
    views = Column(Integer, default=0)

    location = Column(
        Geometry(
            'POINT',       # Tipo de geometría: queremos un punto (lat/lon)
            srid=4326,     # Sistema de Referencia Espacial: 4326 es el estándar WGS 84 (GPS)
            spatial_index=True # Recomendado para optimizar consultas de proximidad
        ), 
        nullable=True # Puede ser False si la ubicación es obligatoria
    )
    
    # RELACIÓN 1: Un sitio historico tiene muchas auditorías.
    audits = relationship(
        "Audit", 
        back_populates="site", 
        lazy="dynamic",
        cascade="all, delete-orphan" # Tiene sentido eliminar las auditorías si se elimina el sitio pero si lo hacemos logico no va a pasar :).
    )
    
    # RELACIÓN 2: Un sitio historico pertenece a una categoría.
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship("Category", back_populates="sites", lazy=True)

    # RELACIÓN 3: un sitio historico tiene un estado.
    state_id = Column(Integer, ForeignKey('states.id'), nullable=False)
    state = relationship("State", back_populates="sites", lazy=True)

    # RELACIÓN 4: un sitio historico tiene muchas etiquetas.
    tag_associations = relationship(
        "HistoricSiteTag",
        back_populates="site",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    from geoalchemy2.shape import to_shape

    @property
    def latitude(self):
        if not self.location:
            return None
        try:
            point = to_shape(self.location)
            return float(point.y)
        except Exception as e:
            try:
                print(f"[Site.latitude] Error convirtiendo location={type(self.location)} {self.location}: {e}")
            except Exception:
                pass
            return None

    @property
    def longitude(self):
        if not self.location:
            return None
        try:
            point = to_shape(self.location)
            return float(point.x)
        except Exception as e:
            try:
                print(f"[Site.longitude] Error convirtiendo location={type(self.location)} {self.location}: {e}")
            except Exception:
                pass
            return None

    @property
    def cover_image(self):
        """Retorna la imagen marcada como portada."""
        # Esto usará el backref 'images'
        return self.images.filter_by(is_cover=True).first()
    
    
    
    def to_dict(self):
        """
        Devuelve una representación de diccionario del objeto Site (SERIALIZACIÓN JSON).
        """
        from core.services.sites_service import SiteService
        
        # Obtener la URL pre-firmada de la imagen de portada
        cover_url = None
        if self.cover_image:
            cover_url = SiteService.build_image_url(self.cover_image.file_path)
        
        if not cover_url:
            cover_url = SiteService.build_image_url('/public/default_image.png')

        # Fecha de registro
        registration_str = self.registration.isoformat() if self.registration else None
        
        # Categoria y State
        category_name = self.category.name if self.category else None
        state_name = self.state.name if self.state else None # También incluimos el estado
        
        # Obtener tags del sitio (máximo 5 para el listado)
        tags_list = [{'id': assoc.tag.id, 'name': assoc.tag.name} for assoc in self.tag_associations.limit(5).all()]
        
        return {
            'id': self.id,
            'name': self.site_name,
            'active': self.active,
            'cover_image_url': cover_url, # URL
            'short_desc': self.short_desc,
            'full_desc': self.full_desc,
            'city': self.city,
            'province': self.province,
            'opening_year': self.operning_year, 
            'registration': registration_str,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'category_name': category_name,
            'state_name': state_name, 
            'views': self.views,
            'tags': tags_list,
            'images': [image.to_dict() for image in self.images.all()]
        }