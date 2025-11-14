from core.database import db
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import bcrypt 
import os
from core.models.User import User
from core.models.Role import Role

class UserService:
    """
    Servicio para gestionar las operaciones CRUD y de autenticación
    relacionadas con el modelo User.
    """

    def get_user_by_id(user_id: int) -> Optional[User]:
        """Busca un usuario por su ID primario."""
        return db.session.get(User, user_id)

    def get_user_by_email(email: str) -> Optional[User]:
        """Busca un usuario por su email único."""
        return db.session.execute(
            db.select(User).filter_by(email=email.lower())
        ).scalar_one_or_none()
    
    @staticmethod
    def find_user_by_email(email):
        """Busca un usuario por email"""
        return User.query.filter_by(email=email).first()
    
    def get_all_active_users() -> List[User]:
        """Recupera todos los usuarios que están activos."""
        return db.session.execute(
            db.select(User).filter_by(active=True)
        ).scalars().all()
    
    def get_all_sysAdmin() -> List[User]:
        """Recupera todos los usuarios que son sysAdmin."""
        return db.session.query(User).filter_by(sysAdmin=True).all()
    
    def get_all_users() -> List[User]:
        """Recupera todos los usuarios."""
        return db.session.query(User).all()
    
    def hash_password(raw_password: str) -> bytes:
        """Genera el hash de la contraseña usando Bcrypt."""
        # Se genera un salt (semilla aleatoria) y se hashea la contraseña.
        # El resultado incluye el hash y el salt.
        hashed = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        return hashed

    def check_password(raw_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash."""
        # El hash almacenado DEBE estar codificado como bytes para Bcrypt
        return bcrypt.checkpw(
            raw_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )

    def create_user(email: str, first_name: str, last_name: str, raw_password: str, sysAdmin: bool = False, role_id: Optional[int] = None) -> User:
        """
        Crea un nuevo usuario con la contraseña hasheada con Bcrypt.
        """
        # 1. Hashear la contraseña usando la función de Bcrypt
        hashed_password_bytes = UserService.hash_password(raw_password)
        # La BD necesita una cadena (str), no bytes.
        hashed_password_str = hashed_password_bytes.decode('utf-8') 

        new_user = User(
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            password=hashed_password_str, # Guardamos el hash como cadena
            sysAdmin=sysAdmin,
            role_id=role_id
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Ya existe un usuario con el email '{email}'.")
        except Exception as e:
            db.session.rollback()
            raise e

    def update_user_details(user_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None, role_id: Optional[int] = None, sysAdmin: Optional[bool] = None) -> Optional[User]:
        """Actualiza los detalles básicos de un usuario."""
        user = UserService.get_user_by_id(user_id)
        if user is None:
            return None

        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if role_id is not None:
            user.role_id = role_id
        if sysAdmin is not None:
            user.sysAdmin = sysAdmin
        
        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    def update_user_password(user_id: int, new_raw_password: str) -> Optional[User]:
        """Actualiza la contraseña de un usuario usando Bcrypt."""
        user = UserService.get_user_by_id(user_id)
        if user is None:
            return None
            
        # Hashear la nueva contraseña y guardarla como cadena
        user.password = UserService.hash_password(new_raw_password).decode('utf-8')

        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    def toggle_user_active_status(user_id: int, active: bool) -> Optional[User]:
        """Activa o desactiva un usuario."""
        user = UserService.get_user_by_id(user_id)
        if user is None:
            return None
            
        user.active = active

        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    def verify_password(password: str, hashed) -> bool:
        """Verifica una contraseña contra su hash."""
        try:
            # Si es un string que viene de PostgreSQL (formato \x...)
            if isinstance(hashed, str) and hashed.startswith('\\x'):
                # Quitar el \x y convertir hex a bytes
                hashed = bytes.fromhex(hashed[2:])
            elif isinstance(hashed, str):
                hashed = hashed.encode('utf-8')
            
            result = bcrypt.checkpw(password.encode('utf-8'), hashed)
            return result
        except Exception as e:
            return False

    def authenticate_user(email: str, raw_password: str) -> Optional[User]:
        """
        Verifica el email y la contraseña usando Bcrypt.
        """
        user = UserService.get_user_by_email(email)
        
        # 1. Comprobar que el usuario exista y esté activo
        if user and user.active:
            # 2. Usar la función de verificación de Bcrypt
            if UserService.verify_password(raw_password, user.password):
                return user
        
        return None

    def is_sys_admin(user_id: int) -> bool:
        """Verifica si un usuario es un administrador del sistema."""
        user = UserService.get_user_by_id(user_id)
        return user is not None and user.sysAdmin
    
    def find_or_create_google_user(email, name, avatar):
        
        user = User.query.filter_by(email=email).first()

        if user:
            return user
        
        name_parts = name.split() if name else []
        first_name = name_parts[0] if name_parts else email.split('@')[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else "Usuario"

        default_role = Role.query.filter_by(name="Usuario").first()

        new_user = User(
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            password=None,  # Sin contraseña para OAuth
            active=True,
            sysAdmin=False,
            deleted=False,
            role_id=default_role.id if default_role else None,
            avatar=avatar
        )

        db.session.add(new_user)
        db.session.commit()

        return new_user
        