from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Post(Base):
    """
    Пост
    """

    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
