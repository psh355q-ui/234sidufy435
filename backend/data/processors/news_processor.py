"""
News Processing Pipeline for Historical Data Seeding.

Features:
- Sentiment Analysis (Gemini 2.0 Flash)
- Named Entity Recognition (Ticker extraction)
- Text Embedding Generation (OpenAI text-embedding-3-small)
- Batch processing with progress tracking

Author: AI Trading System Team
Date: 2025-12-21
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

import google.generativeai as genai
from openai import AsyncOpenAI

try:
    from backend.config.settings import settings
    from backend.data.crawlers.multi_source_crawler import NewsArticle
except ImportError:
    class MockSettings:
        google_api_key = ""
        openai_api_key = ""
    settings = MockSettings()

    @dataclass
    class NewsArticle:
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


logger = logging.getLogger(__name__)


@dataclass
class ProcessedNews:
    """Processed news article with NLP enhancements."""
    article: NewsArticle
    sentiment_score: float  # -1.0 (negative) to 1.0 (positive)
    sentiment_label: str    # "positive", "negative", "neutral"
    embedding: List[float]  # 1536-dim vector
    embedding_model: str
    processed_at: datetime
    processing_errors: List[str]

    def to_db_dict(self) -> Dict:
        """Convert to database-ready dict."""
        base = self.article.to_dict() if hasattr(self.article, 'to_dict') else {}
        return {
            **base,
            "sentiment_score": self.sentiment_score,
            "sentiment_label": self.sentiment_label,
            "embedding": self.embedding,
            "embedding_model": self.embedding_model,
            "processed_at": self.processed_at
        }


class NewsProcessor:
    """
    News processing pipeline with NLP capabilities.

    Pipeline:
    1. Sentiment Analysis (Gemini)
    2. Embedding Generation (OpenAI)
    3. Batch processing with rate limiting
    """

    def __init__(self):
        """Initialize processors."""
        self.logger = logging.getLogger(__name__)

        # Initialize Gemini
        # Initialize Gemini
        # Support both google_api_key and gemini_api_key
        api_key = getattr(settings, 'google_api_key', None) or getattr(settings, 'gemini_api_key', None)
        
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.logger.warning("Google/Gemini API key not configured")
            self.gemini_model = None

        # Initialize OpenAI
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        else:
            self.logger.warning("OpenAI API key not configured")
            self.openai_client = None

        # Rate limiting
        self.gemini_rpm = 15  # Gemini: 15 requests/min (free tier)
        self.openai_rpm = 3000  # OpenAI: 3000 requests/min (tier 1)

    async def process_batch(
        self,
        articles: List[NewsArticle],
        batch_size: int = 10
    ) -> List[ProcessedNews]:
        """
        Process a batch of news articles.

        Args:
            articles: List of NewsArticle objects
            batch_size: Number of articles to process concurrently

        Returns:
            List of ProcessedNews objects
        """
        self.logger.info(f"Processing {len(articles)} articles in batches of {batch_size}")

        processed = []

        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]

            tasks = [self.process_article(article) for article in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.error(f"Processing error: {result}")
                elif result:
                    processed.append(result)

            self.logger.info(f"Processed {len(processed)}/{len(articles)} articles")

            # Rate limiting between batches
            await asyncio.sleep(4)  # 15 req/min = 4s between batches

        return processed

    async def process_article(self, article: NewsArticle) -> Optional[ProcessedNews]:
        """
        Process a single article through the full pipeline.

        Args:
            article: NewsArticle object

        Returns:
            ProcessedNews object or None if processing fails
        """
        errors = []

        try:
            # 1. Content Analysis (Sentiment + NER)
            analysis_result = await self.analyze_content(
                article.title, article.content
            )
            
            sentiment_score = analysis_result["score"]
            sentiment_label = analysis_result["label"]
            
            # Update article with extracted data
            article.tickers = analysis_result["tickers"]
            article.tags = analysis_result["tags"]

            # 2. Generate Embedding
            embedding = await self.generate_embedding(
                f"{article.title}. {article.content}"
            )

            if embedding is None:
                errors.append("Embedding generation failed")
                embedding = [0.0] * 1536  # Fallback empty embedding

            return ProcessedNews(
                article=article,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                embedding=embedding,
                embedding_model="text-embedding-3-small",
                processed_at=datetime.now(),
                processing_errors=errors
            )

        except Exception as e:
            self.logger.error(f"Article processing failed: {e}")
            errors.append(str(e))
            return None

    async def analyze_content(
        self,
        title: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Analyze content using Gemini for Sentiment, Tickers, and Tags.

        Args:
            title: Article title
            content: Article content

        Returns:
            Dict with keys: score, label, tickers, tags
        """
        default_result = {
            "score": 0.0,
            "label": "neutral",
            "tickers": [],
            "tags": []
        }

        if not self.gemini_model:
            return default_result

        try:
            prompt = f"""Analyze this financial news article and return ONLY a JSON object with this format:
{{
    "score": <float -1.0 to 1.0>,
    "label": "<positive|negative|neutral>",
    "tickers": ["EXTRACTED_TICKER_1", "EXTRACTED_TICKER_2"],
    "tags": ["relevant_tag1", "relevant_tag2"]
}}

Extract relevant stock tickers (e.g., AAPL, NVDA, TSLA) mentioned or implied.
Extract key thematic tags (e.g., "Earnings", "Merger", "AI", "Macro").

Title: {title}
Content: {content[:1000]}

Remember: Return ONLY the JSON, no other text."""

            response = await self.gemini_model.generate_content_async(prompt)

            if response and response.text:
                # Extract JSON from response
                text = response.text.strip()

                # Handle markdown code blocks
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()

                # Parse JSON
                import json
                result = json.loads(text)

                score = float(result.get("score", 0.0))
                label = result.get("label", "neutral")
                tickers = result.get("tickers", [])
                tags = result.get("tags", [])

                # Validate
                score = max(-1.0, min(1.0, score))
                if label not in ["positive", "negative", "neutral"]:
                    label = "neutral"
                
                return {
                    "score": score,
                    "label": label,
                    "tickers": tickers,
                    "tags": tags
                }

        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")

        return default_result

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate text embedding using OpenAI.

        Args:
            text: Text to embed (title + content)

        Returns:
            1536-dimensional embedding vector or None if failed
        """
        if not self.openai_client:
            return None

        try:
            # Truncate text to 8000 chars (safe limit)
            text = text[:8000]

            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                encoding_format="float"
            )

            if response.data:
                embedding = response.data[0].embedding
                return embedding

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "insufficient_quota" in error_msg:
                self.logger.warning(f"OpenAI Rate Limit/Quota exceeded: {error_msg}. Using empty embedding.")
            else:
                self.logger.error(f"Embedding generation failed: {error_msg}")

        return None

    def extract_topics(self, text: str) -> List[str]:
        """
        Extract key topics/tags from text (simple keyword-based).

        Args:
            text: Text to analyze

        Returns:
            List of topic tags
        """
        topics = set()

        # Financial keywords
        keywords_map = {
            "earnings": ["earnings", "eps", "revenue", "profit"],
            "merger": ["merger", "acquisition", "m&a", "buyout"],
            "ipo": ["ipo", "initial public offering"],
            "dividend": ["dividend", "payout"],
            "bankruptcy": ["bankruptcy", "chapter 11"],
            "regulation": ["sec", "regulation", "compliance", "fine"],
            "lawsuit": ["lawsuit", "litigation", "settlement"],
            "product": ["product", "launch", "release"],
            "ceo": ["ceo", "chief executive", "management"],
            "layoff": ["layoff", "job cut", "restructuring"]
        }

        text_lower = text.lower()

        for topic, keywords in keywords_map.items():
            if any(kw in text_lower for kw in keywords):
                topics.add(topic)

        return list(topics)


# Standalone test
if __name__ == "__main__":
    import sys
    from datetime import timedelta

    async def test_processor():
        """Test the news processor."""
        print("=" * 80)
        print("News Processing Pipeline Test")
        print("=" * 80)
        print()

        # Create mock article
        mock_article = NewsArticle(
            title="Apple Reports Record Q4 Earnings, Stock Surges",
            content="Apple Inc. reported record earnings for Q4 2024, beating analyst expectations. The company's revenue increased 12% year-over-year to $95 billion, driven by strong iPhone sales and services growth.",
            url="https://example.com/article",
            source="Mock News",
            source_category="financial",
            published_at=datetime.now(),
            tickers=["AAPL"],
            tags=["earnings"],
            author="Test Author"
        )

        processor = NewsProcessor()

        print("Processing single article...")
        result = await processor.process_article(mock_article)

        if result:
            print(f"\n✅ Processing successful!")
            print(f"   Sentiment: {result.sentiment_label} ({result.sentiment_score:.2f})")
            print(f"   Embedding dim: {len(result.embedding)}")
            print(f"   Embedding model: {result.embedding_model}")
            print(f"   Processed at: {result.processed_at}")

            if result.processing_errors:
                print(f"   Errors: {result.processing_errors}")
        else:
            print("❌ Processing failed")

        print("\n" + "=" * 80)
        print("Test completed!")
        print("=" * 80)

    asyncio.run(test_processor())
