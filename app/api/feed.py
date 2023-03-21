from typing import List

import feedparser
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app import crud, schemas, models
from app.database import get_db
from app.utils.dateutils import date_from_string

router = APIRouter()


@router.post("/", response_model=schemas.Feed)
def create_feed(feed: schemas.FeedCreate, user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch and parse RSS feed
    rss_feed = feedparser.parse(feed.url)

    if not rss_feed:
        raise HTTPException(status_code=400, detail="Invalid RSS feed URL")

    db_feed = models.Feed(title=rss_feed.feed.title, url=feed.url, user_id=user_id, created_at=datetime.now(),
                          updated_at=datetime.now())
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)

    # Store articles in the database
    for entry in rss_feed.entries:
        article = schemas.ArticleCreate(
            title=entry.title,
            content=entry.summary,
            link=entry.link,
            published_at=date_from_string(entry.published)
        )
        db_article = models.Article(**article.dict(), feed_id=db_feed.id,
                                    added_at=datetime.now(), updated_at=datetime.now())
        db.add(db_article)
    db.commit()

    return db_feed


@router.get("/", response_model=List[schemas.Feed])
def read_feeds(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    feeds = crud.get_feeds(db, user_id=user_id, skip=skip, limit=limit)
    return feeds


@router.get("/{feed_id}/", response_model=schemas.Feed)
def read_feed(feed_id: int, db: Session = Depends(get_db)):
    feed = crud.get_feed(db, feed_id=feed_id)
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    return feed


@router.put("/{feed_id}/", response_model=schemas.Feed)
def update_feed(feed_id: int, feed: schemas.FeedCreate, db: Session = Depends(get_db)):
    db_feed = crud.get_feed(db, feed_id=feed_id)
    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")

    db_feed.title = feed.title
    db_feed.url = feed.url
    db_feed.updated_at = datetime.now()

    db.commit()
    db.refresh(db_feed)

    return db_feed


@router.delete("/{feed_id}/")
def delete_feed(feed_id: int, db: Session = Depends(get_db)):
    db_feed = crud.get_feed(db, feed_id=feed_id)
    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")

    db.delete(db_feed)
    db.commit()

    return {"detail": "Feed deleted"}
