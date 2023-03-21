from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.Article)
def create_article(article: schemas.ArticleCreate, feed_id: int, db: Session = Depends(get_db)):
    db_article = crud.create_article(db, article=article, feed_id=feed_id)
    return db_article


@router.get("/", response_model=List[schemas.Article])
def read_articles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return articles


@router.get("/feed", response_model=List[schemas.Article])
def read_feed(feed_id: int, db: Session = Depends(get_db)):
    feed = crud.get_feed(db, feed_id=feed_id)
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    articles = crud.get_articles_by_feed(db, feed_id)
    return articles
