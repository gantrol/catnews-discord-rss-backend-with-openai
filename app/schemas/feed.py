from pydantic import BaseModel
from datetime import datetime


class FeedBase(BaseModel):
    title: str
    url: str


class FeedCreate(FeedBase):
    pass


class Feed(FeedBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
