import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from httpx import AsyncClient
from app import models, schemas
from app.database import get_db
from main import app

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)


def db_session() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def test_app():
    app.dependency_overrides[get_db] = db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def access_token(test_app):
    user = schemas.UserCreate(username="testuser3", email="testuser3@example.com", password="testpassword3")
    test_app.post("/auth/register", json=user.dict())
    response = test_app.post("/auth/token", data={"username": "testuser3@example.com", "password": "testpassword3"})
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"
    access_token = response.json()["access_token"]
    yield access_token


@pytest.fixture
def respx_fixture():
    with respx.mock:
        yield