import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import schemas, crud, token
from app.main import app
from app.utils.auth import verify_password

client = TestClient(app)


def test_register_new_user(db: Session):
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    user = crud.user.get_user_by_email(db=db, email=user_data["email"])
    assert user
    assert user.username == user_data["username"]
    assert verify_password(user_data["password"], user.hashed_password)



@pytest.mark.parametrize("email,password",
                         [("testuser@example.com", "wrongpassword"), ("wrongemail@example.com", "testpassword")])
def test_login_invalid_credentials(email: str, password: str):
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 401


def test_login_valid_credentials(db: Session):
    user_data = {
        "email": "testuser@example.com",
        "password": "testpassword",
    }
    response = client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    user = crud.user.get_user_by_email(db=db, email=user_data["email"])
    assert user
