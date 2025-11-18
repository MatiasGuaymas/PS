from core.database import db
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy import func, Boolean as bool
from sqlalchemy.orm import relationship


class Review(db.Model):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(Integer, ForeignKey('sites.id'), nullable=False)
    user_email = Column(String(120), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    content = Column(Text, nullable=False)
    status = Column(String(20), default='Pendiente')  # Pendiente, Aprobada, Rechazada
    rejection_reason = Column(Text, nullable=True)  # Max 200 caracteres
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # RELACIÓN 1: Una reseña pertenece a un sitio histórico.
    # CLAVE FORÁNEA: Columna que referencia la tabla 'sites'.
    site = relationship("Site", backref="reviews", lazy=True)

    def to_dict(self):
        """Convierte la reseña a diccionario"""
        return {
            "id": self.id,
            "site_id": self.site_id,
            "user_email": self.user_email,
            "rating": self.rating,
            "content": self.content,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

