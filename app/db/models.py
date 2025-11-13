# app/db/models.py

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500))
    url = Column(String(500), unique=True, index=True)
    source = Column(String(200))
    published_at = Column(DateTime)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationship to sentiment table
    sentiment = relationship("SentimentResult", back_populates="article", uselist=False)


class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    label = Column(String(50))
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="sentiment")