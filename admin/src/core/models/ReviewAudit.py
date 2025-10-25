from core.database import db
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship


class ReviewAudit(db.Model):
    __tablename__ = 'review_audits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey('reviews.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action_type = Column(String(50), nullable=False)  # APPROVE, REJECT, DELETE
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # RELACIÓN 1: Una auditoría de reseña pertenece a una reseña.
    # CLAVE FORÁNEA: Columna que referencia la tabla 'reviews'.
    review = relationship("Review", backref="audits", lazy=True)

    # RELACIÓN 2: Una auditoría de reseña es realizada por un usuario.
    # CLAVE FORÁNEA: Columna que referencia la tabla 'users'.
    user = relationship("User", backref="review_audits", lazy=True)