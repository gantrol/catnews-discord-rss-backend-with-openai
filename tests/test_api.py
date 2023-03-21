from fastapi.testclient import TestClient

from app import crud
from app.database import SessionLocal
from app.main import app
from app.schemas import UserCreate, FeedCreate

client = TestClient(app)

# Test data
# test_feed = FeedCreate(title="Hacker News: Newest", url="https://hnrss.org/newest")


def test_read_feeds(test_app, db, feed):
    response = client.get("/feed/", params={"user_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == feed["title"]
    assert data[0]["url"] == feed["url"]


def test_read_articles(test_app, db, feed):
    response = client.get("/article/feed", params={"feed_id": feed["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "title" in data[0]
    assert "content" in data[0]
    assert "link" in data[0]
    assert "published_at" in data[0]
