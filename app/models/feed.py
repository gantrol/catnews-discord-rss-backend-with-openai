from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Feed(Base):
    __tablename__ = "feeds"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    url = Column(String, unique=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    owner = relationship("User", back_populates="feeds")
    articles = relationship("Article", back_populates="feed")