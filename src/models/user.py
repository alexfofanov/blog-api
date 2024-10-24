from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """
    Пользователь
    """

    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
