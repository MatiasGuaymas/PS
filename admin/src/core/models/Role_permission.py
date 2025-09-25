from core.database import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey


class Role_permission(BaseModel):
    __tablename__ = 'role_permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    permission_id = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<Role_permission {self.role_id} - {self.permission}>'