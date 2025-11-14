from fastapi import FastAPI
from app.db.database import Base, engine
from app.db import models
from app.services.sentiment_batch import process_unlabeled_articles

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Global Pulse API",
    description="Backend API for scraping, sentiment analysis, and dashboards.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

@app.post("/sentiment/run")
def run_sentiment(limit: int = 25):
    results = process_unlabeled_articles(limit)
    return {"processed": len(results)}