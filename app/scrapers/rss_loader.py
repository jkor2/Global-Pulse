import json
import os
from app.scrapers.rss_feeds import RSS_FEEDS   # existing Python categories

JSON_FEED_FILE = os.path.join(
    os.path.dirname(__file__),
    "rss_feeds",
    "clean_feeds.json"
)

def load_json_feeds():
    """Load the giant JSON file containing 200k+ RSS URLs."""
    if not os.path.exists(JSON_FEED_FILE):
        print(f"[WARN] No JSON feed file found at: {JSON_FEED_FILE}")
        return {}

    try:
        with open(JSON_FEED_FILE, "r") as f:
            data = json.load(f)

        # Normalize keys to lowercase category names
        normalized = {
            key.lower(): urls
            for key, urls in data.items()
            if isinstance(urls, list)
        }
        return normalized

    except Exception as e:
        print("[ERROR] Failed to load JSON RSS file:", e)
        return {}


def load_feeds():
    """Return merged feeds from python modules + json mega-feed file."""

    # 1) Load Python-defined category feeds
    combined = dict(RSS_FEEDS)

    # 2) Load JSON-defined massive feed categories
    json_feeds = load_json_feeds()

    # 3) Merge JSON feeds into the combined structure
    for category, urls in json_feeds.items():
        if category not in combined:
            combined[category] = []

        combined[category].extend(urls)

    # 4) Clean & dedupe all feeds
    cleaned = {}

    for category, urls in combined.items():
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
    print("Total URLs across all categories:", sum(len(v) for v in feeds.values()))