from core.models.Role_permission import Role_permission
from core.models.Role import Role
from core.models.Permission import Permission
from core.database import db

class RoleService:

    def getPermissions(roleId: int):
        return (
            db.session.query(Permission)
            .join(Role_permission, Role_permission.permission_id == Permission.id)
            .filter(Role_permission.role_id == roleId)
            .all()
        )
    
    def getRole(roleName: str):
        return Role.query.filter(Role.name == roleName).first();