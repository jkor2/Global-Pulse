# app/scrapers/rss_scraper.py

import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
import traceback
from app.scrapers.rss_feeds import RSS_FEEDS
from app.db.database import SessionLocal
from app.db.models import Article


def clean_html(text: str) -> str:
    """Remove HTML tags from summaries/content."""
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)


def parse_published(entry) -> datetime | None:
    """Convert RSS published time into datetime."""
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
    except:
        pass
    return None


def scrape_rss(custom_feeds=None):
    """
    Scrape all starter RSS feeds, insert new articles into the DB,
    and return a list of new Article objects.
    """

    feeds = custom_feeds or RSS_FEEDS
    db = SessionLocal()
    new_articles = []

    try:
        for category, feed_urls in feeds.items():
            for url in feed_urls:
                try:
                    feed = feedparser.parse(url)
                except Exception as e:
                    print(f"[ERROR] Exception reading feed: {url} -> {e}")
                    traceback.print_exc()
                    continue

                if hasattr(feed, "bozo") and feed.bozo:
                    print(f"[WARN] Feed parse error: {url} -> {feed.bozo_exception}")

                for entry in getattr(feed, "entries", []):
                    try:
                        title = entry.get("title")
                        link = entry.get("link")
                        summary = clean_html(entry.get("summary", ""))
                        published_dt = parse_published(entry)
                        if not link:
                            continue

                        # Avoid duplicates
                        exists = db.query(Article).filter(Article.url == link).first()
                        if exists:
                            continue

                        article = Article(
                            title=title,
                            url=link,
                            source=category,
                            published_at=published_dt,
                            content=summary,
                        )

                        db.add(article)
                        db.commit()
                        db.refresh(article)
                        new_articles.append(article)
                    except Exception as e:
                        print(f"[ERROR] Failed processing entry in {url}: {e}")
                        traceback.print_exc()
                        db.rollback()
                        continue
        return new_articles
    finally:
        db.close()

if __name__ == "__main__":
    results = scrape_rss()
    print(f"Scraped {len(results)} new articles.")