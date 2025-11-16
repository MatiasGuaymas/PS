from core.database import db
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship

class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    site_id = Column(Integer, ForeignKey('sites.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', backref=db.backref('favorites', lazy='dynamic'), lazy=True)
    site = relationship('Site', backref=db.backref('favorites', lazy='dynamic'), lazy=True)