import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.scrapers.rss_scraper import scrape_rss, clean_html, parse_published

# ---------------------------
# 1. Test HTML cleaning
# ---------------------------
def test_clean_html():
    html = "<p>Hello <b>World</b></p>"
    assert clean_html(html) == "Hello World"


# ---------------------------
# 2. Test published date parsing
# ---------------------------
def test_parse_published_valid():
    class MockEntry:
        published_parsed = (2024, 1, 2, 10, 30, 00, 0, 0, 0)

    entry = MockEntry()
    dt = parse_published(entry)
    assert isinstance(dt, datetime)
    assert dt.year == 2024


def test_parse_published_missing():
    class MockEntry:
        published_parsed = None

    entry = MockEntry()
    assert parse_published(entry) is None


# ---------------------------
# 3. Core scraper tests with mocks
# ---------------------------
@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy session."""
    mock_session = MagicMock()
    mock_session.query().filter().first.return_value = None  # default: no duplicate
    return mock_session


@pytest.fixture
def article_entry():
    """Mock feed entry."""
    return {
        "title": "Breaking News",
        "link": "https://example.com/article1",
        "summary": "<p>Great news!</p>",
        "published_parsed": (2024, 1, 2, 10, 30, 00, 0, 0, 0),
    }


# ---------------------------
# 4. Test normal scraper behavior
# ---------------------------
@patch("app.scrapers.rss_scraper.RSS_FEEDS", {"test": ["http://fake.com/rss"]})
@patch("app.scrapers.rss_scraper.SessionLocal")
@patch("app.scrapers.rss_scraper.feedparser.parse")
def test_scraper_inserts_articles(mock_parse, mock_session_cls, mock_db_session, article_entry):
    # configure mock DB
    mock_session_cls.return_value = mock_db_session

    # mock feedparser output
    mock_parse.return_value = MagicMock(
        bozo=False,
        entries=[article_entry],
    )

    result = scrape_rss()

    assert len(result) == 1
    assert result[0].title == "Breaking News"
    assert result[0].url == "https://example.com/article1"

    # verify DB insert was called
    assert mock_db_session.add.called
    assert mock_db_session.commit.called


# ---------------------------
# 5. Test duplicate skipping
# ---------------------------
@patch("app.scrapers.rss_scraper.SessionLocal")
@patch("app.scrapers.rss_scraper.feedparser.parse")
def test_scraper_skips_duplicates(mock_parse, mock_session_cls, mock_db_session, article_entry):
    mock_session_cls.return_value = mock_db_session

    # Mark entry as duplicate
    mock_db_session.query().filter().first.return_value = True

    # mock feed entries
    mock_parse.return_value = MagicMock(
        bozo=False,
        entries=[article_entry],
    )

    result = scrape_rss()

    assert len(result) == 0
    assert not mock_db_session.add.called


# ---------------------------
# 6. Test feedparser failure handling
# ---------------------------
@patch("app.scrapers.rss_scraper.SessionLocal")
@patch("app.scrapers.rss_scraper.feedparser.parse")
def test_feed_parse_failure(mock_parse, mock_session_cls, mock_db_session):
    mock_session_cls.return_value = mock_db_session

    # simulate feedparser throwing
    mock_parse.side_effect = Exception("Feed error!")

    result = scrape_rss()

    # Should not crash → should return empty list
    assert result == []


# ---------------------------
# 7. Test entry-level failure handling
# ---------------------------
@patch("app.scrapers.rss_scraper.SessionLocal")
@patch("app.scrapers.rss_scraper.feedparser.parse")
def test_entry_failure(mock_parse, mock_session_cls, mock_db_session, article_entry):
    mock_session_cls.return_value = mock_db_session

    # simulate broken entry by causing .get() to fail
    class BrokenEntry:
        def get(self, key):
            raise ValueError("broken entry")

    mock_parse.return_value = MagicMock(
        bozo=False,
        entries=[BrokenEntry()],
    )

    result = scrape_rss()

    # Should skip entry, scrape nothing, but not crash
    assert result == []