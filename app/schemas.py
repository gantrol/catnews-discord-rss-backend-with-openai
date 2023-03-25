from pydantic import BaseModel
from typing import List, Optional


class FeedBase(BaseModel):
    title: str
    url: str


class FeedCreate(FeedBase):
    pass


class Feed(FeedBase):
    id: int

    class Config:
        orm_mode = True


class ArticleBase(BaseModel):
    title: str
    url: str
    content: Optional[str]
    published_at: str


class ArticleCreate(ArticleBase):
    pass


class Article(ArticleBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
