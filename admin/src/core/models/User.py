from core.database import db
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy import func, Boolean as bool
from sqlalchemy.orm import relationship


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    password = Column(String, nullable=False)
    active = Column(bool, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sysAdmin = Column(bool, default=0)
    #role = relationship("Role", backref="users", lazy=True)
    #Fue solo para probar la base de datos, hay que agregar relacion con Role pero sin la tabla no podia
    def __repr__(self):
        return f'<User {self.email}>'
