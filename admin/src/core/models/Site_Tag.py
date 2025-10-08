from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import db

class HistoricSiteTag(db.Model):
    __tablename__ = 'historic_site_tag'

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(Integer, ForeignKey('sites.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False)

    site = relationship("Site", back_populates="tag_associations")
    tag = relationship("Tag", back_populates="site_associations")