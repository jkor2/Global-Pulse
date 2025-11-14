# app/services/sentiment_batch.py

from app.db.database import SessionLocal
from app.db.models import Article
from app.services.sentiment_service import process_sentiment_for_article


def process_unlabeled_articles(limit=50):
    """Find articles without sentiment and process them."""

    db = SessionLocal()

    try:
        articles = (
            db.query(Article)
            .filter(Article.sentiment == None)
            .limit(limit)
            .all()
        )

        processed = []

        for article in articles:
            try:
                sentiment = process_sentiment_for_article(article, db)
                processed.append(sentiment)
            except Exception as e:
                print(f"[ERROR] Failed to analyze Article ID {article.id}: {e}")
                db.rollback()

        return processed

    finally:
        db.close()