from fastapi.testclient import TestClient
import pytest

from app import crud
from main import app
from app.database import async_session, Base, engine
from app.schemas import UserCreate, FeedCreate
from app.utils.auth import verify_password


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db_session = async_session()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)


test_user = UserCreate(username="testuser", email="testuser@example.com", password="testpassword")


@pytest.fixture(scope="module")
def user(test_app, db):
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
    }
    response = test_app.post("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    user = crud.user.get_user_by_email(db=db, email=user_data["email"])
    assert user
    assert user.username == user_data["username"]
    assert verify_password(user_data["password"], user.hashed_password)
    yield user


test_feed = FeedCreate(title="Hacker News", url="https://rsshub.app/hackernews")
# test_feed = FeedCreate(title="小众软件", url="https://www.appinn.com/feed/")


@pytest.fixture(scope="module")
def feed(test_app, db, user):
    response = test_app.post("/feed/", json=test_feed.dict(), params={"user_id": user.id})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_feed.title
    assert data["url"] == test_feed.url
    print(data)
    yield data
