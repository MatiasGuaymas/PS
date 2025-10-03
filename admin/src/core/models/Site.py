from core.database import db
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy import func, Boolean as bool
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry 
from geoalchemy2.shape import to_shape

class Site(db.Model):
    __tablename__ = 'site'

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_name = Column(String(50), unique=True, nullable=False)
    short_desc = Column(String(50), nullable=False)
    full_desc = Column(String(120), nullable=False)
    city = Column(String(50), nullable=False)
    province = Column(String(50), nullable=False)
    operning_year = Column(Integer, nullable=False)
    registration = Column(DateTime(timezone=True), server_default=func.now())
    active = Column(bool, default=1)
    #images = Column(String, nullable=False)

    location = Column(
        Geometry(
            'POINT',       # Tipo de geometría: queremos un punto (lat/lon)
            srid=4326,     # Sistema de Referencia Espacial: 4326 es el estándar WGS 84 (GPS)
            spatial_index=True # Recomendado para optimizar consultas de proximidad
        ), 
        nullable=True # Puede ser False si la ubicación es obligatoria
    )
    
    # RELACIÓN 1: Un sitio historico tiene muchas auditorías.
    # El 'backref' crea la propiedad 'site' en el modelo Audit.
    audits = relationship("Audit", backref="site", lazy=True)
    
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
        lazy="dynamic"
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


