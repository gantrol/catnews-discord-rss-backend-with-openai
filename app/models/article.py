from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"))
    title = Column(String)
    content = Column(Text)
    link = Column(String)
    published_at = Column(DateTime)
    added_at = Column(DateTime)
    updated_at = Column(DateTime)

    feed = relationship("Feed", back_populates="articles")
