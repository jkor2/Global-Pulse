# app/workers/rss_worker.py

import time
from datetime import datetime
from app.scrapers.rss_scraper import scrape_rss

# How often the scraper runs (in seconds)
SCRAPE_INTERVAL = 1800  # 30 minutes

def run_worker():
    while True:
        print(f"\n[{datetime.utcnow()}] Running RSS scraper...")
        
        try:
            articles = scrape_rss()
            print(f"[✓] Scraped {len(articles)} articles.")

        except Exception as e:
            print(f"[ERROR] RSS scrape failed: {e}")

        print(f"Sleeping for {SCRAPE_INTERVAL/60} minutes...\n")
        time.sleep(SCRAPE_INTERVAL)

if __name__ == "__main__":
    run_worker()