from sqlalchemy import Enum
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from enum import Enum as PyEnum
from passlib.context import CryptContext

Base = declarative_base()
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
    hashed_password: Mapped[str] = mapped_column(nullable=True, default='')

    def set_password(self, password: str):
        """Функция хэширует полученный пароль и устанавливает пользователю"""
        self.hashed_password = pwd_context.hash(password)
