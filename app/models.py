from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, UniqueConstraint
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    discord_id = Column(String(255), unique=True)
    github_id = Column(String(255), unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    oauth2_providers = relationship("OAuth2Provider", back_populates="user")


class OAuth2Provider(Base):
    __tablename__ = "oauth2_provider"

    id = Column(Integer, primary_key=True)
    provider = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    access_token = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="oauth2_providers")


class Feed(Base):
    __tablename__ = "feed"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class Article(Base):
    __tablename__ = "article"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    content = Column(String)
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    tags = relationship("ArticleTag", back_populates="article")
    summary = relationship("Summary", uselist=False, back_populates="article")


class FeedArticle(Base):
    __tablename__ = "feed_article"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feed.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("article.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    UniqueConstraint("feed_id", "article_id")


class UserFeedSubscription(Base):
    __tablename__ = "user_feed_subscription"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    feed_id = Column(Integer, ForeignKey("feed.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    UniqueConstraint("user_id", "feed_id")


class RequestedArticle(Base):
    __tablename__ = "requested_article"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("article.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    UniqueConstraint("user_id", "article_id")


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    articles = relationship("ArticleTag", back_populates="tag")


class ArticleTag(Base):
    __tablename__ = "article_tag"

    article_id = Column(Integer, ForeignKey("article.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)

    article = relationship("Article", back_populates="tags")
    tag = relationship("Tag", back_populates="articles")


class Summary(Base):
    __tablename__ = "summary"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    article_id = Column(Integer, ForeignKey("article.id"))
