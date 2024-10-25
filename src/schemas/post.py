from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    title: str
    content: str


class PostUpdate(PostBase):
    title: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[int] = None


class PostCreate(PostBase):
    user_id: Optional[int] = None


class PostInDB(PostCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
