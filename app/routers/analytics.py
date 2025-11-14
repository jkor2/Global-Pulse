from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date
from collections import Counter
import re
from datetime import datetime
from datetime import timedelta

GLOBAL_CUTOFF = date(2025, 10, 1)

from app.db.database import get_db
from app.db.models import Article, SentimentResult, ArticleEntity

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/sentiment-summary")
def sentiment_summary(after: str = None, days: int = None, db: Session = Depends(get_db)):
    cutoff = resolve_cutoff(after, days)
    query = db.query(SentimentResult).join(Article, Article.id == SentimentResult.article_id)
    if cutoff:
        query = query.filter(cast(Article.published_at, Date) >= cutoff)
    total = query.count()
    positive = query.filter(SentimentResult.label == "positive").count()
    negative = query.filter(SentimentResult.label == "negative").count()
    neutral = query.filter(SentimentResult.label == "neutral").count()
    error = query.filter(SentimentResult.label == "error").count()
    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "error": error
    }


@router.get("/top-sources")
def top_sources(after: str = None, days: int = None, db: Session = Depends(get_db)):
    cutoff = resolve_cutoff(after, days)
    query = db.query(Article.source, func.count(Article.id).label("count"))
    if cutoff:
        query = query.filter(cast(Article.published_at, Date) >= cutoff)
    results = query.group_by(Article.source).order_by(func.count(Article.id).desc()).all()
    return [{"source": s, "count": c} for s, c in results]


@router.get("/daily-sentiment")
def daily_sentiment(after: str = None, days: int = None, db: Session = Depends(get_db)):
    cutoff = resolve_cutoff(after, days)
    query = db.query(
        cast(Article.published_at, Date).label("day"),
        SentimentResult.label,
        func.count(SentimentResult.id)
    ).join(SentimentResult, SentimentResult.article_id == Article.id)
    if cutoff:
        query = query.filter(cast(Article.published_at, Date) >= cutoff)
    results = query.group_by("day", SentimentResult.label).order_by("day").all()
    trend = {}
    for day, label, count in results:
        ds = str(day)
        if ds not in trend:
            trend[ds] = {"positive": 0, "negative": 0, "neutral": 0, "error": 0}
        trend[ds][label] = count
    return trend


STOPWORDS = set("""
                will first content post time need cent people like other when appeared best features million free high plan help country back billion make tool online years
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
single game review read
""".split())


def extract_keywords(text: str):
    text = text.lower()
    words = re.findall(r"[a-zA-Z]+", text)
    return [w for w in words if w not in STOPWORDS and len(w) > 3]


def resolve_cutoff(after: str | None, days: int | None):
    user_cutoff = None

    if after:
        try:
            user_cutoff = datetime.strptime(after, "%Y-%m-%d").date()
        except:
            pass

    if days:
        user_cutoff = date.today() - timedelta(days=days)

    if user_cutoff:
        return max(user_cutoff, GLOBAL_CUTOFF)

    return GLOBAL_CUTOFF


@router.get("/keyword-frequency")
def keyword_frequency(after: str = None, days: int = None, db: Session = Depends(get_db)):
    cutoff = resolve_cutoff(after, days)
    query = db.query(Article)
    if cutoff:
        query = query.filter(cast(Article.published_at, Date) >= cutoff)
    articles = query.all()
    all_words = []
    for a in articles:
        if a.title:
            all_words.extend(extract_keywords(a.title))
        if a.content:
            all_words.extend(extract_keywords(a.content))
    freq = Counter(all_words).most_common(50)
    return [{"word": w, "count": c} for w, c in freq]


@router.get("/source-sentiment")
def source_sentiment(after: str = None, days: int = None, db: Session = Depends(get_db)):
    cutoff = resolve_cutoff(after, days)
    query = db.query(
        Article.source,
        SentimentResult.label,
        func.count(SentimentResult.id)
    ).join(SentimentResult, SentimentResult.article_id == Article.id)
    if cutoff:
        query = query.filter(cast(Article.published_at, Date) >= cutoff)
    results = query.group_by(Article.source, SentimentResult.label).all()
    data = {}
    for source, label, count in results:
        if source not in data:
            data[source] = {"positive": 0, "negative": 0, "neutral": 0, "error": 0}
        data[source][label] = count
    return data


@router.get("/top-entities")
def top_entities(limit: int = 100, after: str = None, days: int = None, db: Session = Depends(get_db)):
    cutoff = resolve_cutoff(after, days)
    query = db.query(
        ArticleEntity.entity,
        ArticleEntity.entity_type,
        func.count(ArticleEntity.id)
    ).join(Article, Article.id == ArticleEntity.article_id)

    if cutoff:
        query = query.filter(cast(Article.published_at, Date) >= cutoff)

    results = query.group_by(
        ArticleEntity.entity,
        ArticleEntity.entity_type
    ).order_by(func.count(ArticleEntity.id).desc()).limit(limit).all()
    return [{"entity": e, "type": t, "count": c} for e, t, c in results]


@router.get("/entity-trend/{entity_name}")
def entity_trend(entity_name: str, after: str = None, days: int = None, db: Session = Depends(get_db)):
    cutoff = resolve_cutoff(after, days)
    query = db.query(
        cast(ArticleEntity.created_at, Date).label("day"),
        func.count(ArticleEntity.id)
    ).filter(ArticleEntity.entity.ilike(f"%{entity_name}%"))
    if cutoff:
        query = query.filter(cast(ArticleEntity.created_at, Date) >= cutoff)
    results = query.group_by("day").order_by("day").all()
    return {str(day): count for day, count in results}


@router.get("/entity-sentiment/{entity_name}")
def entity_sentiment(entity_name: str, after: str = None, days: int = None, db: Session = Depends(get_db)):
    cutoff = resolve_cutoff(after, days)
    query = (
        db.query(
            SentimentResult.label,
            func.count(SentimentResult.id)
        )
        .join(Article, Article.id == SentimentResult.article_id)
        .join(ArticleEntity, ArticleEntity.article_id == Article.id)
        .filter(ArticleEntity.entity.ilike(f"%{entity_name}%"))
    )
    if cutoff:
        query = query.filter(cast(Article.published_at, Date) >= cutoff)
    results = query.group_by(SentimentResult.label).all()
    summary = {"positive": 0, "negative": 0, "neutral": 0, "error": 0}
    for label, count in results:
        summary[label] = count
    return summary


@router.get("/article/{article_id}/entities")
def article_entities(article_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(
            ArticleEntity.entity,
            ArticleEntity.entity_type,
            ArticleEntity.created_at
        )
        .filter(ArticleEntity.article_id == article_id)
        .all()
    )
    return [{"entity": e, "type": t, "date": str(d)} for e, t, d in results]


@router.get("/trending-entities")
def trending_entities(days: int = 7, after: str = None, db: Session = Depends(get_db)):
    cutoff = resolve_cutoff(after, days)
    query = db.query(
        ArticleEntity.entity,
        ArticleEntity.entity_type,
        func.count(ArticleEntity.id)
    )
    if cutoff:
        query = query.filter(cast(ArticleEntity.created_at, Date) >= cutoff)
    results = query.group_by(ArticleEntity.entity, ArticleEntity.entity_type).order_by(func.count(ArticleEntity.id).desc()).limit(20).all()
    return [{"entity": e, "type": t, "count": c} for e, t, c in results]