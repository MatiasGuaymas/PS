from core.database import db
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy import func, Boolean as bool


class Flag(db.Model):
    __tablename__ = 'flags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), unique=True, nullable=False)
    description = Column(String(200), nullable=False)
    is_enabled = Column(bool, default=1)
    last_edit = Column(DateTime(timezone=True), server_default=func.now())
    message = Column(String(100), nullable=True)

    # RELACIÓN 1: Una Flag es modificada por un único Usuario.
    # CLAVE FORÁNEA: Columna que referencia la tabla 'users'.
    # Puede ser null si se carga desde seeds.
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    
    #Preguntar si puedo tener methods en el modelo
    def is_maintenance(self) -> bool:
        """Determina si la flag es de mantenimiento."""
        if not self.name:
             return False
        # Se asume que cualquier flag cuyo nombre contenga 'maintenance_mode' es de mantenimiento.
        return 'maintenance_mode' in self.name.lower()
    
    def has_message(self) -> bool:
        """Verifica si la flag tiene un mensaje configurado."""
        return bool(self.message and self.message.strip())