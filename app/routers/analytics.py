# app/routers/analytics.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SentimentResult
from sqlalchemy import func

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/sentiment-summary")
def sentiment_summary(db: Session = Depends(get_db)):
    """Return aggregate sentiment statistics from the database."""

    total = db.query(func.count(SentimentResult.id)).scalar()
    positive = db.query(func.count(SentimentResult.id)).filter(SentimentResult.label == "positive").scalar()
    negative = db.query(func.count(SentimentResult.id)).filter(SentimentResult.label == "negative").scalar()
    neutral = db.query(func.count(SentimentResult.id)).filter(SentimentResult.label == "neutral").scalar()
    error = db.query(func.count(SentimentResult.id)).filter(SentimentResult.label == "error").scalar()

    return {
        "total_articles_with_sentiment": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "error": error
    }