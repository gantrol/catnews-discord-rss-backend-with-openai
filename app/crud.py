import bcrypt
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime, timedelta
import feedparser

from app.database import get_db
from app.schemas import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# By password
def register_user(user: UserCreate, db: Session) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,  # using the email as the username
        password_hash=hashed_password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(username: str, db: Session):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(email: str, db: Session) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(user_id: int, db: Session):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_github_id(github_id: str, db: Session) -> models.User:
    return db.query(models.User).filter(models.User.github_id == github_id).first()


def get_user_by_discord_id(discord_id: str, db: Session) -> models.User:
    return db.query(models.User).filter(models.User.discord_id == discord_id).first()


def create_user_with_discord(user_data: dict, token: dict, db: Session) -> models.User:
    user = models.User(
        username=user_data["username"],
        email=user_data["email"],
        discord_id=user_data["id"],
        password_hash="",  # Set an empty password hash for OAuth users
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    oauth2_provider = models.OAuth2Provider(
        provider="discord",
        user_id=user.id,
        access_token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        expires_at=datetime.utcnow() + timedelta(seconds=token["expires_in"]),
    )
    db.add(oauth2_provider)
    db.commit()
    db.refresh(oauth2_provider)

    return user


def update_discord_token(user_id: int, token: dict, db: Session):
    oauth2_provider = (
        db.query(models.OAuth2Provider)
        .filter(models.OAuth2Provider.user_id == user_id)
        .filter(models.OAuth2Provider.provider == "discord")
        .first()
    )

    oauth2_provider.access_token = token["access_token"]
    oauth2_provider.refresh_token = token.get("refresh_token")
    oauth2_provider.expires_at = datetime.utcnow() + timedelta(seconds=token["expires_in"])

    db.commit()
    db.refresh(oauth2_provider)


def subscribe_to_feed(feed: schemas.FeedCreate, user: models.User, db: Session):
    # Check if the feed exists, create it if not
    db_feed = db.query(models.Feed).filter(models.Feed.url == feed.url).first()
    if db_feed is None:
        parsed_feed = feedparser.parse(feed.url)
        db_feed = models.Feed(title=parsed_feed.feed.title, url=feed.url, created_at=datetime.utcnow(),
                              updated_at=datetime.utcnow())
        db.add(db_feed)
        db.commit()
        db.refresh(db_feed)

    # Subscribe the user to the feed
    subscription = models.UserFeedSubscription(user_id=user.id, feed_id=db_feed.id, created_at=datetime.utcnow(),
                                               updated_at=datetime.utcnow())
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return db_feed


def unsubscribe_from_feed(feed: schemas.FeedCreate, user: models.User, db: Session):
    db_feed = db.query(models.Feed).filter(models.Feed.url == feed.url).first()
    if db_feed is not None:
        subscription = db.query(models.UserFeedSubscription).filter(models.UserFeedSubscription.user_id == user.id,
                                                                    models.UserFeedSubscription.feed_id == db_feed.id).first()
        if subscription is not None:
            db.delete(subscription)
            db.commit()
            return db_feed
    return None


def list_subscribed_feeds(user: models.User, db: Session):
    subscriptions = db.query(models.Feed).join(models.UserFeedSubscription).filter(
        models.UserFeedSubscription.user_id == user.id).all()
    return subscriptions


def get_feed_articles(user: models.User, db: Session):
    feeds = list_subscribed_feeds(user, db)
    articles = []
    for feed in feeds:
        feed_articles = db.query(models.Article).join(models.FeedArticle).filter(
            models.FeedArticle.feed_id == feed.id).all()
        articles.extend(feed_articles)
    return articles


def authenticate_user(email: str, password: str, db: Session):
    user = get_user_by_email(email, db)
    if user and pwd_context.verify(password, user.password):
        return user
    return None
