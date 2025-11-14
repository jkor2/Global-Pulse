# app/scrapers/rss_loader.py

from app.scrapers.rss_feeds import RSS_FEEDS

def load_feeds():
    """Return a flattened, validated version of all RSS feeds."""
    
    cleaned = {}

    for category, urls in RSS_FEEDS.items():
        if not urls:
            continue

        cleaned_list = []

        for url in urls:
            if not isinstance(url, str):
                continue
            url = url.strip()
            if not url:
                continue
            if not url.startswith("http"):
                continue
            cleaned_list.append(url)

        cleaned[category] = sorted(set(cleaned_list))

    return cleaned


if __name__ == "__main__":
    feeds = load_feeds()
    print("Loaded feed categories:", list(feeds.keys()))
    print("Total feeds:", sum(len(v) for v in feeds.values()))