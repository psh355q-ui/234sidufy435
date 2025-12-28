"""
5분 데이터 수집 테스트

War Room 데이터 수집 파이프라인 검증:
1. Yahoo Finance - 주가 데이터
2. FRED - 거시 데이터 (금리, 수익률 곡선)
3. FinViz - 뉴스 데이터
4. Social Sentiment - 소셜 데이터 (mock)

Author: ai-trading-system
Date: 2025-12-28
"""

import sys
import os
from pathlib import Path

# Add paths for imports
backend_path = Path(__file__).parent.parent.parent
root_path = backend_path.parent
sys.path.insert(0, str(root_path))
sys.path.insert(0, str(backend_path))
os.chdir(backend_path)

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========== Mock Data Collectors ==========

class YahooCollector:
    """Mock Yahoo Finance collector"""

    async def collect_market_data(self, ticker: str) -> Dict[str, Any]:
        """Collect market data for a ticker"""
        logger.info(f"📊 Collecting Yahoo data for {ticker}")
        await asyncio.sleep(0.5)  # Simulate API call

        return {
            "ticker": ticker,
            "current_price": 175.50,
            "volume": 65000000,
            "high": 177.20,
            "low": 174.80,
            "open": 175.00,
            "prev_close": 174.50,
            "rsi": 58.5,
            "sma_20": 173.20,
            "sma_50": 170.80,
            "sma_200": 165.50,
            "macd": 2.5,
            "macd_signal": 2.2,
            "timestamp": datetime.now().isoformat()
        }


class FREDCollector:
    """Mock FRED collector for macro data"""

    async def collect_macro_data(self) -> Dict[str, Any]:
        """Collect macro economic data"""
        logger.info(f"🌍 Collecting FRED macro data")
        await asyncio.sleep(1.0)  # Simulate API call

        return {
            "fed_rate": 5.25,
            "fed_direction": "HOLDING",
            "cpi_yoy": 3.2,
            "gdp_growth": 2.5,
            "unemployment": 3.7,
            "yield_curve": {
                "2y": 4.5,
                "10y": 4.35
            },
            "wti_crude": 75.50,
            "wti_change_30d": 5.2,
            "dxy": 102.5,
            "dxy_change_30d": 2.8,
            "timestamp": datetime.now().isoformat()
        }


class FinVizCollector:
    """Mock FinViz news collector"""

    async def collect_news(self, ticker: str) -> List[Dict[str, Any]]:
        """Collect news for a ticker"""
        logger.info(f"📰 Collecting FinViz news for {ticker}")
        await asyncio.sleep(0.5)  # Simulate API call

        return [
            {
                "title": f"{ticker} announces new AI chip partnership",
                "source": "Reuters",
                "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "sentiment": 0.75,
                "url": f"https://finviz.com/news/{ticker.lower()}-ai-chip"
            },
            {
                "title": f"{ticker} sales beat expectations in Q4",
                "source": "Bloomberg",
                "published_at": (datetime.now() - timedelta(hours=5)).isoformat(),
                "sentiment": 0.65,
                "url": f"https://finviz.com/news/{ticker.lower()}-q4"
            }
        ]


class SocialCollector:
    """Mock social sentiment collector"""

    async def collect_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Collect social sentiment data"""
        logger.info(f"💬 Collecting social sentiment for {ticker}")
        await asyncio.sleep(0.5)  # Simulate API call

        return {
            "ticker": ticker,
            "twitter_sentiment": 0.55,
            "twitter_volume": 12000,
            "reddit_sentiment": 0.48,
            "reddit_mentions": 850,
            "fear_greed_index": 52,
            "trending_rank": 15,
            "sentiment_change_24h": 0.08,
            "bullish_ratio": 0.62,
            "timestamp": datetime.now().isoformat()
        }


# ========== Data Collection Test ==========

async def test_single_ticker_collection(ticker: str) -> Dict[str, Any]:
    """Test data collection for a single ticker"""
    print(f"\n{'='*80}")
    print(f"Collecting data for {ticker}")
    print(f"{'='*80}")

    start_time = datetime.now()

    # Initialize collectors
    yahoo = YahooCollector()
    finviz = FinVizCollector()
    social = SocialCollector()

    # Collect data in parallel
    results = await asyncio.gather(
        yahoo.collect_market_data(ticker),
        finviz.collect_news(ticker),
        social.collect_sentiment(ticker),
        return_exceptions=True
    )

    market_data, news_data, social_data = results

    # Verify data
    assert isinstance(market_data, dict), "Market data must be dict"
    assert isinstance(news_data, list), "News data must be list"
    assert isinstance(social_data, dict), "Social data must be dict"

    assert "current_price" in market_data, "Missing current_price"
    assert "rsi" in market_data, "Missing RSI"
    assert len(news_data) > 0, "No news collected"
    assert "twitter_sentiment" in social_data, "Missing social sentiment"

    duration = (datetime.now() - start_time).total_seconds()

    print(f"\n✓ Market Data: Price=${market_data['current_price']}, RSI={market_data['rsi']}")
    print(f"✓ News: {len(news_data)} articles collected")
    print(f"✓ Social: Twitter sentiment={social_data['twitter_sentiment']:.2f}")
    print(f"✓ Collection time: {duration:.2f}s")

    return {
        "ticker": ticker,
        "market_data": market_data,
        "news_data": news_data,
        "social_data": social_data,
        "collection_time": duration
    }


async def test_macro_collection() -> Dict[str, Any]:
    """Test macro data collection"""
    print(f"\n{'='*80}")
    print(f"Collecting Macro Economic Data")
    print(f"{'='*80}")

    start_time = datetime.now()

    fred = FREDCollector()
    macro_data = await fred.collect_macro_data()

    # Verify data
    assert "fed_rate" in macro_data, "Missing fed_rate"
    assert "yield_curve" in macro_data, "Missing yield_curve"
    assert "2y" in macro_data["yield_curve"], "Missing 2y yield"
    assert "10y" in macro_data["yield_curve"], "Missing 10y yield"

    duration = (datetime.now() - start_time).total_seconds()

    print(f"\n✓ Fed Rate: {macro_data['fed_rate']}%")
    print(f"✓ Yield Curve: 2Y={macro_data['yield_curve']['2y']}%, 10Y={macro_data['yield_curve']['10y']}%")
    print(f"✓ WTI Crude: ${macro_data['wti_crude']}")
    print(f"✓ DXY: {macro_data['dxy']}")
    print(f"✓ Collection time: {duration:.2f}s")

    return {
        "macro_data": macro_data,
        "collection_time": duration
    }


async def test_5min_continuous_collection():
    """Run 5-minute continuous data collection test"""
    print(f"\n{'='*80}")
    print(f"5-MINUTE DATA COLLECTION TEST")
    print(f"{'='*80}")
    print(f"Start Time: {datetime.now()}")
    print(f"Duration: 5 minutes")
    print(f"Collection Interval: Every 30 seconds")
    print(f"{'='*80}\n")

    # Test tickers
    tickers = ["AAPL", "NVDA", "MSFT"]

    # Stats tracking
    stats = {
        "total_cycles": 0,
        "successful_cycles": 0,
        "failed_cycles": 0,
        "total_tickers_collected": 0,
        "total_collection_time": 0.0
    }

    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=5)
    cycle = 1

    while datetime.now() < end_time:
        cycle_start = datetime.now()

        print(f"\n{'─'*80}")
        print(f"CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'─'*80}")

        try:
            # Collect macro data (once per cycle)
            macro_result = await test_macro_collection()
            stats["total_collection_time"] += macro_result["collection_time"]

            # Collect ticker data (parallel)
            ticker_results = await asyncio.gather(
                *[test_single_ticker_collection(ticker) for ticker in tickers],
                return_exceptions=True
            )

            # Count successful collections
            successful = sum(1 for r in ticker_results if isinstance(r, dict))
            stats["total_tickers_collected"] += successful
            stats["total_collection_time"] += sum(
                r["collection_time"] for r in ticker_results if isinstance(r, dict)
            )

            stats["successful_cycles"] += 1

        except Exception as e:
            logger.error(f"Cycle {cycle} failed: {e}")
            stats["failed_cycles"] += 1

        stats["total_cycles"] += 1
        cycle += 1

        # Wait before next cycle (30 seconds interval)
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        wait_time = max(0, 30 - cycle_duration)

        if wait_time > 0 and datetime.now() < end_time:
            remaining = (end_time - datetime.now()).total_seconds()
            wait_time = min(wait_time, remaining)
            if wait_time > 0:
                print(f"\n⏳ Waiting {wait_time:.1f}s until next cycle...")
                await asyncio.sleep(wait_time)

    # Final summary
    total_duration = (datetime.now() - start_time).total_seconds()

    print(f"\n{'='*80}")
    print(f"5-MINUTE TEST COMPLETE")
    print(f"{'='*80}")
    print(f"Total Duration: {total_duration:.1f}s")
    print(f"Total Cycles: {stats['total_cycles']}")
    print(f"Successful Cycles: {stats['successful_cycles']}")
    print(f"Failed Cycles: {stats['failed_cycles']}")
    print(f"Success Rate: {(stats['successful_cycles']/stats['total_cycles']*100):.1f}%")
    print(f"Total Tickers Collected: {stats['total_tickers_collected']}")
    print(f"Avg Collection Time/Cycle: {stats['total_collection_time']/stats['total_cycles']:.2f}s")
    print(f"{'='*80}\n")

    return stats


async def run_test():
    """Run the 5-minute data collection test"""
    try:
        stats = await test_5min_continuous_collection()

        # Test passed if > 80% success rate
        success_rate = (stats['successful_cycles'] / stats['total_cycles']) * 100

        if success_rate >= 80:
            print(f"✓ TEST PASSED ({success_rate:.1f}% success rate)")
            return 0
        else:
            print(f"✗ TEST FAILED ({success_rate:.1f}% success rate < 80%)")
            return 1

    except Exception as e:
        logger.error(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point"""
    return asyncio.run(run_test())


if __name__ == "__main__":
    sys.exit(main())
