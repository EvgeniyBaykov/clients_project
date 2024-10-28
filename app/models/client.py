from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from enum import Enum as PyEnum

Base = declarative_base()


class GenderEnum(PyEnum):
    male = "male"
    female = "female"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    avatar: Mapped[str] = mapped_column(nullable=True)
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum), nullable=False)
    first_name: Mapped[str] = mapped_column(index=True, nullable=False)
    last_name: Mapped[str] = mapped_column(index=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
