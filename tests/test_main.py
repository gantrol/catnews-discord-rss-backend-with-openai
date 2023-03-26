from typing import List

from fastapi import status

from app import schemas

# TODO: local utils function test?
# import respx
# with open("assets/hackernews.xml", "rb") as rss_file:
#     rss_content = rss_file.read()
# respx.get(EXAMPLE_RSS_URL).mock(return_value=respx.MockResponse(content=rss_content))
EXAMPLE_RSS_URL = "https://rsshub.app/hackernews"


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


def test_add_subscription(test_app, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    feed_data = {"url": EXAMPLE_RSS_URL}

    response = test_app.post("/feeds", json=feed_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    print(response.text)
    print(response.json())
    assert response.json()["url"] == feed_data["url"]


def test_list_subscriptions(test_app, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = test_app.get("/feeds", headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert isinstance(response.json(), List)
    assert len(response.json()) > 0


def test_get_feed_articles(test_app, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = test_app.get("/articles", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), List)


def test_remove_subscription(test_app, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    feed_data = {"url": EXAMPLE_RSS_URL}
    response = test_app.post("/feeds/unsubscribe", json=feed_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
