from datetime import datetime, timedelta
from typing import Union

import jwt
from jwt import PyJWTError

import app.database
from app.config import settings


def create_access_token(subject: Union[str, int], expires_delta: timedelta = None):
    if not expires_delta:
        expires_delta = timedelta(minutes=app.database.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow(),
        "sub": str(subject),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except PyJWTError:
        return None
