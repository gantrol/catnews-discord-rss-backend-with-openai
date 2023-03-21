from sqlalchemy.orm import Session
from app.schemas import ArticleCreate
from app.models import Article


def create_article(db: Session, article: ArticleCreate, feed_id: int):
    db_article = Article(**article.dict(), feed_id=feed_id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def get_articles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Article).offset(skip).limit(limit).all()


def get_articles_by_feed(db: Session, feed_id, skip: int = 0, limit: int = 10):
    return db.query(Article).filter(Article.feed_id == feed_id).offset(skip).limit(limit).all()
