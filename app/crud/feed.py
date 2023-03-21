from sqlalchemy.orm import Session
from app import models
from app.schemas import FeedCreate


def get_feeds(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Feed).filter(models.Feed.user_id == user_id).offset(skip).limit(limit).all()


def get_feed(db: Session, feed_id: int):
    return db.query(models.Feed).filter(models.Feed.id == feed_id)


def create_feed(db: Session, feed: FeedCreate):
    db_feed = models.Feed(url=feed.url)
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    return db_feed

def get_feed(db: Session, feed_id: int):
    return db.query(models.Feed).filter(models.Feed.id == feed_id).first()

def get_articles(db: Session, feed_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Article).filter(models.Article.feed_id == feed_id).offset(skip).limit(limit).all()