import os
from datetime import timedelta, datetime

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from starlette import status

from app import crud, models
from app.config import settings
from dotenv import load_dotenv
import os

load_dotenv()

if os.environ.get("TESTING"):
    load_dotenv(".env.test")

# JWT Authentication



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if user is None or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt


def get_current_user(db: Session, token: str = Depends(oauth2_scheme)) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    except (JWTError, ValidationError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    user = await crud.get_user_by_id(db, user_id)  # <- Pass the db parameter
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
