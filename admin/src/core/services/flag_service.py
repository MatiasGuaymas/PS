from core.database import db
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from core.models.Flag import Flag
from datetime import datetime, timezone

class FlagService:
    """
    Servicio para gestionar las operaciones CRUD y de consulta
    relacionadas con el modelo Flag.
    """

    
    def get_all_flags() -> List[Flag]:
        """Recupera todas las flags de la base de datos."""
        return Flag.query.all()

    
    def get_flag_by_id(flag_id: int):
        """Busca una flag por su ID."""
        return Flag.query.get(flag_id)

    
    def get_flag_by_name(name: str) -> Optional[Flag]:
        """Busca una flag por su nombre único."""
        return Flag.query.filter(Flag.name == name).first()
    
    def is_flag_enabled(name: str) -> bool:
        """Comprueba si una flag está habilitada (is_enabled=True)."""
        flag = FlagService.get_flag_by_name(name)
        # Retorna True si existe y su valor es True, sino False
        return flag is not None and flag.is_enabled


    def toggle_feature_flag(id, is_enabled, user):
        """Cambia el estado de un flag y registra quien lo cambio"""
        feature_flag = FlagService.get_flag_by_id(id)
        # Si no se encuentra
        if not feature_flag:
            return None
        if feature_flag.is_maintenance and not is_enabled:
            # Si el nuevo estado es DESACTIVADO, limpiamos el mensaje.
            feature_flag.message = ""
        feature_flag.is_enabled = is_enabled
        feature_flag.user_id = user
        feature_flag.last_edit = datetime.now(timezone.utc)
        
        db.session.commit()
        return feature_flag

    def set_maintenance_message(flag_id: int, message: str) -> Optional[Flag]:
        """
        Establece o actualiza el mensaje de mantenimiento de una flag.
        """
        flag = FlagService.get_flag_by_id(flag_id)
        if flag is None:
            return None
        
        flag.message = message
        return flag        
        
    def create_flag(name: str, description: str, user_id: int, value: bool = True, message: Optional[str] = None) -> Flag:
        """
        Crea una nueva flag en la base de datos.
        Lanza una excepción si el nombre ya existe.
        """
        new_flag = Flag(
            name=name,
            description=description,
            is_enabled=value,
            user_id=user_id,
            message=message
        )
        try:
            db.session.add(new_flag)
            db.session.commit()
            return new_flag
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Ya existe una flag con el nombre '{name}'.")
        except Exception as e:
            db.session.rollback()
            raise e


    def update_flag(flag_id: int, user_id: int, value: Optional[bool] = None, description: Optional[str] = None, message: Optional[str] = None) -> Optional[Flag]:
        """
        Actualiza el valor, la descripción y/o el mensaje de una flag existente.
        También actualiza el last_edit y el user_id.
        """
        flag = FlagService.get_flag_by_id(flag_id)
        if flag is None:
            return None

        # Actualiza solo si se proporciona un nuevo valor
        if value is not None:
            flag.is_enabled = value
        if description is not None:
            flag.description = description
        if message is not None:
            flag.message = message

        # El user_id siempre se actualiza para saber quién hizo el último cambio
        flag.user_id = user_id
        
        # SQLAlchemy manejará la actualización de last_edit gracias a onupdate=func.now()
        
        try:
            db.session.commit()
            return flag
        except Exception as e:
            db.session.rollback()
            raise e
    
    
    def delete_flag(flag_id: int) -> bool:
        """
        Elimina una flag por su ID.
        Retorna True si se elimina, False si no se encuentra.
        """
        flag = FlagService.get_flag_by_id(flag_id)
        if flag:
            db.session.delete(flag)
            try:
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                raise e
        return False