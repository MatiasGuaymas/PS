from core.database import db
from sqlalchemy import Column, Integer, ForeignKey


class Role_permission(db.Model):
    __tablename__ = 'role_permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    # permission_id should reference permissions.id
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)

    def __repr__(self):
        return f'<Role_permission {self.role_id} - {self.permission_id}>'