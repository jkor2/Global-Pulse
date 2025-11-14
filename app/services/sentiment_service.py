# app/services/sentiment_service.py

from datetime import datetime
from sqlalchemy.orm import Session
from app.utils.nlp import analyze_sentiment
from app.db.models import Article, SentimentResult


def process_sentiment_for_article(article: Article, db: Session) -> SentimentResult:
    """Run sentiment analysis on a single article and store the result."""

    # Skip if sentiment already exists
    if article.sentiment:
        return article.sentiment

    text = article.content or article.title
    result = analyze_sentiment(text)

    sentiment = SentimentResult(
        article_id=article.id,
        label=result["label"],
        score=float(result["score"]),
        created_at=datetime.utcnow(),
    )

    db.add(sentiment)
    db.commit()
    db.refresh(sentiment)

    return sentiment