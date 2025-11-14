# app/workers/sentiment_worker.py

import time
from datetime import datetime
from app.db.database import SessionLocal
from app.db.models import Article
from app.services.sentiment_service import process_sentiment_for_article
from app.services.entity_service import process_entities_for_article

def wait_for_database():
    import time
    from sqlalchemy import text
    from app.db.database import SessionLocal

    while True:
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            print("Database is ready.")
            return
        except Exception as e:
            print(f"Database not ready yet... {e}")
            time.sleep(3)

SLEEP_SECONDS = 10  

def run_worker():
    wait_for_database()
    """Continuously process articles missing sentiment."""

    while True:
        with SessionLocal() as db:

            articles = (
                db.query(Article)
                  .filter(Article.sentiment == None)
                  .limit(25)
                  .all()
            )

            if not articles:
                print(f"[{datetime.utcnow()}] No new articles. Sleeping...")
                time.sleep(SLEEP_SECONDS)
                continue

            print(f"[{datetime.utcnow()}] Processing {len(articles)} articles...")

            for article in articles:
                try:
                    process_sentiment_for_article(article, db)
                    process_entities_for_article(article, db)
                    print(f"✓ Processed sentiment for Article {article.id}")
                except Exception as e:
                    print(f"[ERROR] Could not process Article {article.id}: {e}")
                    db.rollback()

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    run_worker()