# app/scrapers/rss_feeds.py

RSS_FEEDS = {
    "world": [
        "http://feeds.bbci.co.uk/news/rss.xml",
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    ],

    "technology": [
        "https://www.theverge.com/rss/index.xml",
        "http://feeds.feedburner.com/TechCrunch/",
        "http://feeds.wired.com/wired/index",
    ],

    "science": [
        "http://feeds.sciencedaily.com/sciencedaily",
        "https://www.npr.org/rss/rss.php?id=1007",
    ],

    "general": [
        "https://news.yahoo.com/rss/mostviewed",
    ],
}