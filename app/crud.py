from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime
import feedparser


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def subscribe_to_feed(db: Session, feed: schemas.FeedCreate, user: models.User):
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


def unsubscribe_from_feed(db: Session, feed: schemas.FeedCreate, user: models.User):
    db_feed = db.query(models.Feed).filter(models.Feed.url == feed.url).first()
    if db_feed is not None:
        subscription = db.query(models.UserFeedSubscription).filter(models.UserFeedSubscription.user_id == user.id,
                                                                    models.UserFeedSubscription.feed_id == db_feed.id).first()
        if subscription is not None:
            db.delete(subscription)
            db.commit()
            return db_feed
    return None


def list_subscribed_feeds(db: Session, user: models.User):
    subscriptions = db.query(models.Feed).join(models.UserFeedSubscription).filter(
        models.UserFeedSubscription.user_id == user.id).all()
    return subscriptions


def get_feed_articles(db: Session, user: models.User):
    feeds = list_subscribed_feeds(db, user)
    articles = []
    for feed in feeds:
        feed_articles = db.query(models.Article).join(models.FeedArticle).filter(
            models.FeedArticle.feed_id == feed.id).all()
        articles.extend(feed_articles)
    return articles
