from datetime import datetime

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Literal


class FeedBase(BaseModel):
    title: str
    url: str


class FeedCreate(BaseModel):
    url: str


class FeedRemove(BaseModel):
    url: str


class Feed(FeedBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ArticleBase(BaseModel):
    title: str
    url: str
    content: Optional[str]
    published_at: datetime


class ArticleCreate(ArticleBase):
    pass


class Article(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    token_source: Literal["Discord", "Password", "Github"]


class TokenData(BaseModel):
    username: Optional[str] = None
