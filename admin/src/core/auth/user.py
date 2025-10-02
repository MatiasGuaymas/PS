import datetime
from src.core.database import db
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

class User(db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    inserted_at: Mapped[str] = mapped_column(
        DateTime, default=lambda: datetime.now(datetime.timezone.utc)
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime, default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc)
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"