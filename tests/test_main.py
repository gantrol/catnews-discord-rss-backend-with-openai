import pytest
from fastapi import status, Depends
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db


def test_register(test_app):
    user = schemas.UserCreate(username="testuser1", email="testuser1@example.com", password="testpassword")
    response = test_app.post("/auth/register", json=user.dict())
    print(response.content)
    assert response.status_code == status.HTTP_201_CREATED

    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login(test_app):
    user = schemas.UserCreate(username="testuser2", email="testuser2@example.com", password="testpassword")
    test_app.post("/auth/register", json=user.dict())

    response = test_app.post("/auth/token", data={"username": "testuser2@example.com", "password": "testpassword"})
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"
