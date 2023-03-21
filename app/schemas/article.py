from datetime import datetime
from pydantic import BaseModel


class ArticleBase(BaseModel):
    title: str
    content: str
    link: str
    published_at: datetime


class ArticleCreate(ArticleBase):
    pass


class Article(ArticleBase):
    id: int
    feed_id: int
    added_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
