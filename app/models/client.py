from sqlalchemy import DateTime
from enum import Enum as PyEnum

from passlib.context import CryptContext
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class GenderEnum(PyEnum):
    male = "male"
    female = "female"


class Client(Base):
    """Модель описывающая пользователя"""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    avatar: Mapped[str] = mapped_column(nullable=True)
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum), nullable=False)
    first_name: Mapped[str] = mapped_column(index=True, nullable=False)
    last_name: Mapped[str] = mapped_column(index=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=True)
    latitude: Mapped[float] = mapped_column(nullable=True)
    longitude: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def set_password(self, password: str):
        """Функция хэширует полученный пароль и устанавливает пользователю"""
        self.hashed_password = pwd_context.hash(password)

    def set_latitude(self, latitude: float):
        """Функция устанавливает значение широты"""
        self.latitude = latitude

    def set_longitude(self, longitude: float):
        """Функция устанавливает значение долготы"""
        self.longitude = longitude
