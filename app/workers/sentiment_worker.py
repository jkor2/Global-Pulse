# app/workers/sentiment_worker.py

import time
from datetime import datetime
from app.db.database import SessionLocal
from app.db.models import Article
from app.services.sentiment_service import process_sentiment_for_article
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)

def truncate_text(text: str, max_tokens: int = 512) -> str:
    """Trim text to model max length without breaking the pipeline."""
    try:
        tokens = tokenizer.encode(
            text,
            truncation=True,
            max_length=max_tokens
        )
        return tokenizer.decode(tokens, skip_special_tokens=True)
    except Exception:
        return text[:2000]

# Worker will run every SLEEP_SECONDS seconds. 
SLEEP_SECONDS = 10  


def run_worker():
    """Continuously process articles missing sentiment."""

    while True:
        db = SessionLocal()

        try:
            # All articles with NO sentiment yet. 
            articles = (
                db.query(Article)
                  .filter(Article.sentiment == None)
                  .limit(25)
                  .all()
            )

            if not articles:
                print(f"[{datetime.utcnow()}] No new articles. Sleeping...")
                db.close()
                time.sleep(SLEEP_SECONDS)
                continue

            print(f"[{datetime.utcnow()}] Processing {len(articles)} articles...")

            for article in articles:
                try:
                    safe_text = truncate_text(article.content)
                    process_sentiment_for_article(article, db, safe_text)
                    print(f"✓ Processed sentiment for Article {article.id}")
                except Exception as e:
                    print(f"[ERROR] Could not process Article {article.id}: {e}")
                    db.rollback()

        finally:
            db.close()

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    run_worker()