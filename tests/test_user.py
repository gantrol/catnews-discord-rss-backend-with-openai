# tests/test_user.py
import pytest
from app import schemas, crud
from app.models.user import User


def test_create_user(test_app, db):
    user = schemas.UserCreate(username="test_user", email="test@example.com", password="test_password")
    db_user = crud.create_user(db, user=user)
    assert db_user is not None
    assert db_user.username == user.username
    assert db_user.email == user.email


def test_get_user_by_username(test_app, db):
    username = "test_user"
    user = crud.get_user_by_username(db, username=username)
    assert user is not None
    assert user.username == username


def test_get_user(test_app, db):
    user_id = 1
    user = crud.get_user(db, user_id=user_id)
    assert user is not None
    assert user.id == user_id


def test_get_users(test_app, db):
    users = crud.get_users(db, skip=0, limit=10)
    assert len(users) > 0
