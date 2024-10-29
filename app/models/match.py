from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from app.db.base import Base


class Match(Base):
    """Модель таблицы содержащей взаимные симпатии"""
    __tablename__ = "match"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=False)
