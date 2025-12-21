"""
Multi-Source News Crawler for Historical Data Seeding.

Supports multiple news sources:
- NewsAPI (100 requests/day)
- Google News RSS
- Yahoo Finance News
- Reuters RSS
- Bloomberg RSS (if available)

Author: AI Trading System Team
Date: 2025-12-21
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import hashlib

import aiohttp
import feedparser
from bs4 import BeautifulSoup

try:
    from backend.config.settings import settings
except ImportError:
    class MockSettings:
        newsapi_key = ""
        max_concurrent_requests = 5
    settings = MockSettings()


logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Standardized news article format."""
    title: str
    content: str
    url: str
    source: str
    source_category: str
    published_at: datetime
    tickers: List[str]
    tags: List[str]
    author: Optional[str] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dict for database insertion."""
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "source": self.source,
            "source_category": self.source_category,
            "published_at": self.published_at,
            "tickers": self.tickers,
            "tags": self.tags,
            "author": self.author,
            "metadata": self.metadata or {}
        }

    def generate_hash(self) -> str:
        """Generate unique hash for deduplication."""
        content_str = f"{self.title}|{self.url}|{self.published_at.date()}"
        return hashlib.md5(content_str.encode()).hexdigest()


class MultiSourceNewsCrawler:
    """
    Multi-source news crawler with rate limiting and deduplication.

    Features:
    - NewsAPI integration (100 req/day limit)
    - RSS feed parsing (Google News, Reuters, Bloomberg)
    - Web scraping (Yahoo Finance)
    - Automatic ticker extraction
    - Deduplication
    - Rate limiting per source
    """

    def __init__(self):
        """Initialize crawler."""
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.seen_hashes = set()

        # Rate limiting (requests per minute)
        self.rate_limits = {
            "newsapi": 2,  # 100/day = ~4/hour = ~2/min conservative
            "rss": 10,     # RSS feeds are usually more permissive
            "scraper": 5   # Web scraping - be conservative
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def crawl_all(
        self,
        start_date: datetime,
        end_date: datetime,
        keywords: Optional[List[str]] = None,
        tickers: Optional[List[str]] = None
    ) -> List[NewsArticle]:
        """
        Crawl all sources for given date range.

        Args:
            start_date: Start date for news collection
            end_date: End date for news collection
            keywords: Optional keywords to filter (e.g., ["stock", "market"])
            tickers: Optional tickers to focus on (e.g., ["AAPL", "TSLA"])

        Returns:
            List of NewsArticle objects
        """
        self.logger.info(
            f"Starting multi-source crawl: {start_date.date()} to {end_date.date()}"
        )

        tasks = []

        # NewsAPI (if API key available)
        if hasattr(settings, 'newsapi_key') and settings.newsapi_key:
            tasks.append(
                self.crawl_newsapi(start_date, end_date, keywords, tickers)
            )

        # RSS Feeds
        tasks.extend([
            self.crawl_google_news_rss(keywords, tickers),
            self.crawl_reuters_rss(),
            # self.crawl_bloomberg_rss(),  # Often requires subscription
        ])

        # Web Scrapers
        tasks.append(
            self.crawl_yahoo_finance(tickers)
        )

        # Run all crawlers concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten and deduplicate
        all_articles = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Crawler error: {result}")
            elif isinstance(result, list):
                all_articles.extend(result)

        # Deduplicate by hash
        unique_articles = []
        for article in all_articles:
            article_hash = article.generate_hash()
            if article_hash not in self.seen_hashes:
                self.seen_hashes.add(article_hash)
                unique_articles.append(article)

        self.logger.info(
            f"Crawled {len(all_articles)} articles, "
            f"{len(unique_articles)} unique after dedup"
        )

        return unique_articles

    async def crawl_newsapi(
        self,
        start_date: datetime,
        end_date: datetime,
        keywords: Optional[List[str]] = None,
        tickers: Optional[List[str]] = None
    ) -> List[NewsArticle]:
        """
        Crawl NewsAPI.

        Rate limit: 100 requests/day (conservative: 2 req/min)
        """
        if not hasattr(settings, 'newsapi_key') or not settings.newsapi_key:
            self.logger.warning("NewsAPI key not configured, skipping")
            return []

        self.logger.info("Crawling NewsAPI...")

        articles = []

        # Build query
        query_parts = []
        if keywords:
            query_parts.extend(keywords)
        if tickers:
            query_parts.extend(tickers)

        query = " OR ".join(query_parts) if query_parts else "stock market"

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": settings.newsapi_key,
            "pageSize": 100  # Max per request
        }

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    for item in data.get("articles", []):
                        # Extract tickers from title/content
                        extracted_tickers = self._extract_tickers(
                            f"{item.get('title', '')} {item.get('description', '')}"
                        )

                        article = NewsArticle(
                            title=item.get("title", ""),
                            content=item.get("description", "") or item.get("content", ""),
                            url=item.get("url", ""),
                            source=item.get("source", {}).get("name", "NewsAPI"),
                            source_category="financial",
                            published_at=datetime.fromisoformat(
                                item["publishedAt"].replace("Z", "+00:00")
                            ),
                            tickers=extracted_tickers,
                            tags=keywords or [],
                            author=item.get("author"),
                            metadata={"source_id": item.get("source", {}).get("id")}
                        )
                        articles.append(article)

                    self.logger.info(f"NewsAPI: Fetched {len(articles)} articles")
                else:
                    self.logger.error(f"NewsAPI error: {response.status}")

        except Exception as e:
            self.logger.error(f"NewsAPI crawl failed: {e}")

        # Rate limiting
        await asyncio.sleep(30)  # 2 req/min = 30s between requests

        return articles

    async def crawl_google_news_rss(
        self,
        keywords: Optional[List[str]] = None,
        tickers: Optional[List[str]] = None
    ) -> List[NewsArticle]:
        """
        Crawl Google News RSS feed.

        Rate limit: 10 req/min (RSS is usually permissive)
        """
        self.logger.info("Crawling Google News RSS...")

        articles = []

        # Build RSS URL with search query
        query_parts = []
        if keywords:
            query_parts.extend(keywords)
        if tickers:
            query_parts.extend(tickers)

        query = " ".join(query_parts) if query_parts else "stock market"
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

        try:
            async with self.session.get(rss_url) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    feed = feedparser.parse(xml_content)

                    for entry in feed.entries:
                        # Extract tickers
                        extracted_tickers = self._extract_tickers(
                            f"{entry.get('title', '')} {entry.get('summary', '')}"
                        )

                        # Parse published date
                        published_at = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_at = datetime(*entry.published_parsed[:6])

                        article = NewsArticle(
                            title=entry.get("title", ""),
                            content=entry.get("summary", ""),
                            url=entry.get("link", ""),
                            source="Google News",
                            source_category="general",
                            published_at=published_at,
                            tickers=extracted_tickers,
                            tags=keywords or [],
                            metadata={"source": entry.get("source", {}).get("title")}
                        )
                        articles.append(article)

                    self.logger.info(f"Google News RSS: Fetched {len(articles)} articles")

        except Exception as e:
            self.logger.error(f"Google News RSS crawl failed: {e}")

        await asyncio.sleep(6)  # 10 req/min = 6s between requests

        return articles

    async def crawl_reuters_rss(self) -> List[NewsArticle]:
        """Crawl Reuters markets RSS feed."""
        self.logger.info("Crawling Reuters RSS...")

        articles = []
        rss_url = "https://www.reuters.com/business/finance/rss"

        try:
            async with self.session.get(rss_url) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    feed = feedparser.parse(xml_content)

                    for entry in feed.entries:
                        extracted_tickers = self._extract_tickers(
                            f"{entry.get('title', '')} {entry.get('summary', '')}"
                        )

                        published_at = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_at = datetime(*entry.published_parsed[:6])

                        article = NewsArticle(
                            title=entry.get("title", ""),
                            content=entry.get("summary", ""),
                            url=entry.get("link", ""),
                            source="Reuters",
                            source_category="financial",
                            published_at=published_at,
                            tickers=extracted_tickers,
                            tags=["market", "finance"],
                            metadata={}
                        )
                        articles.append(article)

                    self.logger.info(f"Reuters RSS: Fetched {len(articles)} articles")

        except Exception as e:
            self.logger.error(f"Reuters RSS crawl failed: {e}")

        await asyncio.sleep(6)

        return articles

    async def crawl_yahoo_finance(
        self,
        tickers: Optional[List[str]] = None
    ) -> List[NewsArticle]:
        """
        Scrape Yahoo Finance news for specific tickers.

        Rate limit: 5 req/min (conservative for web scraping)
        """
        if not tickers:
            tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # Default tickers

        self.logger.info(f"Crawling Yahoo Finance for tickers: {tickers}")

        articles = []

        for ticker in tickers[:10]:  # Limit to 10 tickers per batch
            url = f"https://finance.yahoo.com/quote/{ticker}/news"

            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        # Find news articles (Yahoo's structure may change)
                        news_items = soup.find_all('li', class_='js-stream-content')

                        for item in news_items[:5]:  # Top 5 per ticker
                            title_elem = item.find('h3')
                            link_elem = item.find('a')

                            if title_elem and link_elem:
                                title = title_elem.get_text(strip=True)
                                link = link_elem.get('href', '')

                                if not link.startswith('http'):
                                    link = f"https://finance.yahoo.com{link}"

                                article = NewsArticle(
                                    title=title,
                                    content="",  # Yahoo doesn't show full content
                                    url=link,
                                    source="Yahoo Finance",
                                    source_category="financial",
                                    published_at=datetime.now(),  # Scraping doesn't give exact time
                                    tickers=[ticker],
                                    tags=["ticker-specific"],
                                    metadata={"ticker": ticker}
                                )
                                articles.append(article)

                        self.logger.info(f"Yahoo Finance ({ticker}): Fetched {len(news_items[:5])} articles")

            except Exception as e:
                self.logger.error(f"Yahoo Finance crawl failed for {ticker}: {e}")

            await asyncio.sleep(12)  # 5 req/min = 12s between requests

        return articles

    def _extract_tickers(self, text: str) -> List[str]:
        """
        Extract stock tickers from text.

        Simple regex-based extraction: $TICKER or TICKER:
        """
        tickers = set()

        # Pattern 1: $TICKER (e.g., $AAPL)
        pattern1 = r'\$([A-Z]{1,5})\b'
        matches1 = re.findall(pattern1, text)
        tickers.update(matches1)

        # Pattern 2: TICKER: or (TICKER) (e.g., Apple (AAPL))
        pattern2 = r'\b([A-Z]{2,5})(?:\:|\))'
        matches2 = re.findall(pattern2, text)
        tickers.update(matches2)

        # Filter out common false positives
        false_positives = {"CEO", "CFO", "IPO", "ETF", "USA", "USD", "SEC", "FDA", "NYSE", "NASDAQ"}
        tickers = {t for t in tickers if t not in false_positives}

        return list(tickers)


# Standalone test
if __name__ == "__main__":
    import sys

    async def test_crawler():
        """Test the multi-source crawler."""
        print("=" * 80)
        print("Multi-Source News Crawler Test")
        print("=" * 80)
        print()

        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        async with MultiSourceNewsCrawler() as crawler:
            articles = await crawler.crawl_all(
                start_date=start_date,
                end_date=end_date,
                keywords=["stock", "market"],
                tickers=["AAPL", "TSLA"]
            )

            print(f"\nTotal articles collected: {len(articles)}")
            print(f"Unique sources: {len(set(a.source for a in articles))}")
            print()

            # Show first 5
            for i, article in enumerate(articles[:5], 1):
                print(f"{i}. {article.title}")
                print(f"   Source: {article.source}")
                print(f"   Tickers: {article.tickers}")
                print(f"   Published: {article.published_at}")
                print(f"   URL: {article.url[:60]}...")
                print()

    asyncio.run(test_crawler())
