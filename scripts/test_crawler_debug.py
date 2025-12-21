
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Explicitly load .env
from dotenv import load_dotenv, find_dotenv
env_path = find_dotenv()
load_dotenv(env_path)

# Debug logging
print(f"--- DEBUG INFO ---")
print(f".env path: {env_path}")
print(f"NEWS_API_KEY present in os.environ: {'NEWS_API_KEY' in os.environ}")
if 'NEWS_API_KEY' in os.environ:
    print(f"NEWS_API_KEY value check: {os.environ['NEWS_API_KEY'][:5]}***")
else:
    print("NEWS_API_KEY NOT FOUND in os.environ")
print(f"------------------")

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from backend.data.crawlers.multi_source_crawler import MultiSourceNewsCrawler
    import backend.config.settings as app_config
    
    # Patch the global settings object used by other modules
    if 'NEWS_API_KEY' in os.environ:
        print("[DEBUG] Patching global app_config.settings.newsapi_key")
        app_config.settings.newsapi_key = os.environ['NEWS_API_KEY']
    
    # Reference for local checks
    settings = app_config.settings
    
    print(f"[DEBUG] Settings loaded.")
    print(f"[DEBUG] Settings.newsapi_key: {bool(settings.newsapi_key)}")
    if settings.newsapi_key:
         print(f"[DEBUG] Settings Key prefix: {settings.newsapi_key[:4]}...")
except ImportError as e:
    print(f"[DEBUG] Failed to import backend modules: {e}")
    # Mock settings if import fails
    class MockSettings:
        newsapi_key = "test_key"
        max_concurrent_requests = 5
    settings = MockSettings()

async def test_crawler():
    print("=" * 80)
    print("Multi-Source News Crawler Debug Test")
    print("=" * 80)

    start_date = datetime.now() - timedelta(days=2)
    end_date = datetime.now()
    
    keywords = ["Tesla", "Samsung"]
    tickers = ["TSLA"]

    print(f"Time Range: {start_date} ~ {end_date}")
    print(f"Keywords: {keywords}")
    print(f"Tickers: {tickers}")
    print("-" * 50)

    try:
        async with MultiSourceNewsCrawler() as crawler:
            # Check NewsAPI specifically
            print("\n[Testing NewsAPI...]")
            newsapi_articles = await crawler.crawl_newsapi(start_date, end_date, keywords, tickers)
            print(f"NewsAPI Result: {len(newsapi_articles)} articles")
            
            # Check RSS Fallback
            print("\n[Testing Google News RSS...]")
            rss_articles = await crawler.crawl_google_news_rss(keywords=keywords)
            print(f"Google News RSS Result: {len(rss_articles)} articles")

            print("\n[Testing Combined crawl_all...]")
            all_articles = await crawler.crawl_all(start_date, end_date, keywords, tickers)
            print(f"Total Unique Articles from crawl_all: {len(all_articles)}")

            if not all_articles:
                print("\n[WARNING] No articles found.")
    except Exception as e:
        print(f"\n[ERROR] Crawler failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_crawler())
