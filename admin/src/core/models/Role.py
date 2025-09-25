from core.database import db
from sqlalchemy import Column, Integer, String, Text, DateTime, func

class Role(db.Model):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Role {self.name}>'