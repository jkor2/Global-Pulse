# app/scrapers/rss_scraper.py

import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
import traceback
from app.scrapers.rss_loader import load_feeds
from app.db.database import SessionLocal
from app.db.models import Article


def clean_html(text: str) -> str:
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)


def parse_published(entry):
    try:
        if getattr(entry, "published_parsed", None):
            return datetime(*entry.published_parsed[:6])
    except:
        pass
    return None


def scrape_rss(custom_feeds=None):
    feeds = custom_feeds or load_feeds()
    db = SessionLocal()
    new_articles = []

    try:
        for category, feed_urls in feeds.items():
            print(f"[SCRAPER] Category: {category} — {len(feed_urls)} feeds")

            for url in feed_urls:
                try:
                    feed = feedparser.parse(url)
                except Exception as e:
                    print(f"[ERROR] Could not load feed: {url} -> {e}")
                    traceback.print_exc()
                    continue

                if getattr(feed, "bozo", False):
                    print(f"[WARN] Feed parse error: {url} -> {feed.bozo_exception}")

                for entry in getattr(feed, "entries", []):
                    try:
                        title = entry.get("title")
                        link = entry.get("link")

                        if not link:
                            continue

                        existing = db.query(Article).filter(Article.url == link).first()
                        if existing:
                            continue

                        summary = clean_html(entry.get("summary", ""))
                        published_dt = parse_published(entry)

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
                        print(f"[ERROR] Failed processing entry from {url}: {e}")
                        traceback.print_exc()
                        db.rollback()
                        continue

        return new_articles

    finally:
        db.close()


if __name__ == "__main__":
    r = scrape_rss()
    print(f"Scraped {len(r)} new articles.")