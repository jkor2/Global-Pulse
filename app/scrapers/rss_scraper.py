# app/scrapers/rss_scraper.py

import feedparser
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup
import traceback

from app.scrapers.rss_loader import load_feeds
from app.db.database import SessionLocal
from app.db.models import Article


# -------------------------
# Helper: Clean HTML safely
# -------------------------
def clean_html(text: str) -> str:
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)


# -------------------------
# Helper: Parse published date
# -------------------------
def parse_published(entry):
    try:
        if getattr(entry, "published_parsed", None):
            return datetime(*entry.published_parsed[:6])
    except:
        pass
    return None


# -------------------------
# CRITICAL FIX:
# Safe feed parsing wrapper
# -------------------------
def safe_parse(url: str):
    """Feedparser wrapper that avoids RemoteDisconnected & redirect loops."""
    try:
        # Add browser-level headers to avoid feed blocking
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36 GlobalPulseRSS/1.0"
                )
            }
        )

        # Fail fast so we don't hang on bad feeds
        raw_data = urllib.request.urlopen(req, timeout=10).read()

        # Parse RSS/XML from memory
        return feedparser.parse(raw_data)

    except Exception as e:
        print(f"[RSS ERROR] Could not parse feed: {url}\n -> {e}")
        return None
    
# -------------------------
# Main scraper
# -------------------------
def scrape_rss(custom_feeds=None):
    feeds = custom_feeds or load_feeds()
    db = SessionLocal()
    new_articles = []

    try:
        for category, feed_urls in feeds.items():
            print(f"[SCRAPER] Category: {category} — {len(feed_urls)} feeds")

            for url in feed_urls:

                # SAFE parse instead of direct feedparser.parse
                feed = safe_parse(url)
                if not feed or not getattr(feed, "entries", None):
                    continue  # skip broken feed

                # warn if feed is malformed but still usable
                if getattr(feed, "bozo", False):
                    print(f"[WARN] Feed parse issue ({url}): {feed.bozo_exception}")

                for entry in feed.entries:
                    try:
                        title = entry.get("title")
                        link = entry.get("link")

                        if not link:
                            continue

                        # Prevent duplicates
                        if db.query(Article).filter(Article.url == link).first():
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

        return new_articles

    finally:
        db.close()


if __name__ == "__main__":
    r = scrape_rss()
    print(f"Scraped {len(r)} new articles.")