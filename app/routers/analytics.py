# app/routers/analytics.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from app.db.database import get_db
from app.db.models import SentimentResult, Article
import re
from collections import Counter
from datetime import date


router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Sentiment Summary 
@router.get("/sentiment-summary")
def sentiment_summary(db: Session = Depends(get_db)):
    total = db.query(func.count(SentimentResult.id)).scalar()
    positive = db.query(func.count(SentimentResult.id)).filter(SentimentResult.label == "positive").scalar()
    negative = db.query(func.count(SentimentResult.id)).filter(SentimentResult.label == "negative").scalar()
    neutral = db.query(func.count(SentimentResult.id)).filter(SentimentResult.label == "neutral").scalar()
    error = db.query(func.count(SentimentResult.id)).filter(SentimentResult.label == "error").scalar()

    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "error": error
    }

# Top Sources 
@router.get("/top-sources")
def top_sources(db: Session = Depends(get_db)):
    results = (
        db.query(Article.source, func.count(Article.id).label("count"))
          .group_by(Article.source)
          .order_by(func.count(Article.id).desc())
          .all()
    )

    return [{"source": r[0], "count": r[1]} for r in results]


# Daily trend
@router.get("/daily-sentiment")
def daily_sentiment(db: Session = Depends(get_db)):
    cutoff = date(2025, 11, 1)

    # Group sentiment by DATE(article.published_at)
    results = (
        db.query(
            cast(Article.published_at, Date).label("day"),
            SentimentResult.label,
            func.count(SentimentResult.id).label("count")
        )
        .join(SentimentResult, SentimentResult.article_id == Article.id)
        .filter(cast(Article.published_at, Date) >= cutoff)
        .group_by("day", SentimentResult.label)
        .order_by("day")
        .all()
    )

    trend = {}

    for day, label, count in results:
        day_str = str(day)
        if day_str not in trend:
            trend[day_str] = {"positive": 0, "negative": 0, "neutral": 0, "error": 0}

        trend[day_str][label] = count

    return trend


# Keyword freq
STOPWORDS = set("""
a an the and or but if while then than
of for with without within
to from in on at by about into onto upon
is was are were be been being
it this that these those
you your yours we our us they them their 
as so just very really
what which who whom whose
also too much many most
can could should would may might
do does did doing done
has have had having
not no yes
all any each every some
there here after before during 
such though although however still 
because since until 
over under again once even only 
more less few several
out up down off
i me my mine 
he him his she her hers 
one two three four five
really actually basically literally kinda sort maybe probably
new latest update report reports reporting 
breaking developing announced announcement 
news article media sources source experts
today yesterday tomorrow week month year 
said says saying according
company companies firm firms organization organizations
market markets
global international world national
industry industries sector sectors
""".split())

def extract_keywords(text):
    text = text.lower()
    words = re.findall(r"[a-zA-Z]+", text)
    return [w for w in words if w not in STOPWORDS and len(w) > 3]

@router.get("/keyword-frequency")
def keyword_frequency(db: Session = Depends(get_db)):
    articles = db.query(Article).all()

    all_words = []

    for a in articles:
        if a.title:
            all_words.extend(extract_keywords(a.title))
        if a.content:
            all_words.extend(extract_keywords(a.content))

    freq = Counter(all_words).most_common(50)

    return [{"word": w, "count": c} for w, c in freq]

# Sentiment by source 
@router.get("/source-sentiment")
def source_sentiment(db: Session = Depends(get_db)):
    results = (
        db.query(
            Article.source,
            SentimentResult.label,
            func.count(SentimentResult.id)
        )
        .join(SentimentResult, SentimentResult.article_id == Article.id)
        .group_by(Article.source, SentimentResult.label)
        .all()
    )

    response = {}

    for source, label, count in results:
        if source not in response:
            response[source] = {"positive": 0, "negative": 0, "neutral": 0, "error": 0}
        response[source][label] = count

    return response