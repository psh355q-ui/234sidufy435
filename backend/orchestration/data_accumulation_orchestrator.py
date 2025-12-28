"""
Data Accumulation Orchestrator

Coordinates automated data collection for War Room validation:
- News collection (RSS + Finviz)
- War Room debate analysis
- Constitutional validation logging
- Data quality metrics

Usage:
    orchestrator = DataAccumulationOrchestrator()
    await orchestrator.start_accumulation(duration_days=14)

Target:
- 100+ analysis records
- 15+ days continuous data
- Multiple tickers
- Full Constitutional validation logs

Author: ai-trading-system
Date: 2025-12-27
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

from backend.news.rss_crawler_with_db import RSSCrawlerWithDB
from backend.data.collectors.finviz_collector import FinvizCollector
from backend.ai.debate.constitutional_debate_engine import ConstitutionalDebateEngine
from backend.database.repository import (
    NewsRepository,
    AnalysisRepository,
    get_sync_session
)
from backend.schemas.base_schema import MarketContext
from backend.data.collectors.api_clients.yahoo_client import YahooFinanceClient

logger = logging.getLogger(__name__)


class AccumulationPhase(Enum):
    """Data accumulation phases"""
    INITIALIZATION = "initialization"
    NEWS_COLLECTION = "news_collection"
    WAR_ROOM_ANALYSIS = "war_room_analysis"
    VALIDATION_LOGGING = "validation_logging"
    METRICS_COLLECTION = "metrics_collection"
    COMPLETED = "completed"


@dataclass
class AccumulationStats:
    """Data accumulation statistics"""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    # News collection stats
    news_articles_collected: int = 0
    news_sources: set = field(default_factory=set)

    # War Room stats
    debates_conducted: int = 0
    tickers_analyzed: set = field(default_factory=set)
    signal_distribution: Dict[str, int] = field(default_factory=lambda: {"BUY": 0, "SELL": 0, "HOLD": 0})

    # Constitutional stats
    constitutional_validations: int = 0
    constitutional_violations: int = 0
    violation_types: Dict[str, int] = field(default_factory=dict)

    # Data quality stats
    avg_confidence: float = 0.0
    confidence_samples: List[float] = field(default_factory=list)

    # Errors
    errors: List[Dict] = field(default_factory=list)

    def record_confidence(self, confidence: float):
        """Record confidence score for averaging"""
        self.confidence_samples.append(confidence)
        self.avg_confidence = sum(self.confidence_samples) / len(self.confidence_samples)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "duration_hours": (self.end_time - self.start_time).total_seconds() / 3600 if self.end_time else 0,
            "news_articles": self.news_articles_collected,
            "news_sources": len(self.news_sources),
            "debates": self.debates_conducted,
            "tickers": len(self.tickers_analyzed),
            "signals": self.signal_distribution,
            "constitutional_validations": self.constitutional_validations,
            "constitutional_violations": self.constitutional_violations,
            "violation_rate": f"{(self.constitutional_violations / max(1, self.constitutional_validations)) * 100:.1f}%",
            "avg_confidence": f"{self.avg_confidence:.2%}",
            "errors": len(self.errors)
        }


class DataAccumulationOrchestrator:
    """
    Data Accumulation Orchestrator

    Coordinates all data collection systems for War Room validation:

    Pipeline:
    1. News Collection (RSS + Finviz) → Every 5 minutes
    2. War Room Analysis → Triggered by news
    3. Constitutional Validation → Every debate
    4. Metrics Collection → Continuous

    Data Storage:
    - news_articles table (via NewsRepository)
    - analysis_results table (via AnalysisRepository)
    - constitutional_validation_logs table (custom)
    - war_room_debates table (custom)
    """

    def __init__(
        self,
        news_check_interval_minutes: int = 5,
        war_room_batch_size: int = 5,
        enable_rss: bool = True,
        enable_finviz: bool = True,
        enable_constitutional_logging: bool = True
    ):
        """
        Initialize orchestrator

        Args:
            news_check_interval_minutes: News collection interval (default: 5 min)
            war_room_batch_size: Max articles per War Room batch (default: 5)
            enable_rss: Enable RSS crawler
            enable_finviz: Enable Finviz collector
            enable_constitutional_logging: Enable constitutional validation logging
        """
        self.news_check_interval = news_check_interval_minutes * 60  # Convert to seconds
        self.war_room_batch_size = war_room_batch_size
        self.enable_rss = enable_rss
        self.enable_finviz = enable_finviz
        self.enable_constitutional_logging = enable_constitutional_logging

        # Components
        self.rss_crawler = RSSCrawlerWithDB(enable_alerts=False, enable_metrics=True) if enable_rss else None
        self.finviz_collector = FinvizCollector() if enable_finviz else None
        self.debate_engine = None  # Initialized with DB session
        self.yahoo_client = YahooFinanceClient()

        # Stats
        self.stats = AccumulationStats()

        # State
        self.is_running = False
        self.current_phase = AccumulationPhase.INITIALIZATION

        logger.info("🎯 Data Accumulation Orchestrator initialized")
        logger.info(f"   News interval: {news_check_interval_minutes} min")
        logger.info(f"   War Room batch: {war_room_batch_size}")
        logger.info(f"   RSS: {'ENABLED' if enable_rss else 'DISABLED'}")
        logger.info(f"   Finviz: {'ENABLED' if enable_finviz else 'DISABLED'}")

    async def start_accumulation(
        self,
        duration_days: int = 14,
        target_debates: int = 100
    ):
        """
        Start data accumulation

        Args:
            duration_days: Target duration (default: 14 days)
            target_debates: Target number of debates (default: 100)
        """
        self.is_running = True
        self.stats.start_time = datetime.now()
        target_end_time = self.stats.start_time + timedelta(days=duration_days)

        logger.info("\n" + "="*80)
        logger.info("🚀 DATA ACCUMULATION STARTED")
        logger.info("="*80)
        logger.info(f"Start time: {self.stats.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Target end: {target_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duration: {duration_days} days")
        logger.info(f"Target debates: {target_debates}")
        logger.info("="*80 + "\n")

        cycle_count = 0

        try:
            while self.is_running:
                cycle_count += 1
                current_time = datetime.now()

                # Check termination conditions
                if current_time >= target_end_time:
                    logger.info(f"✅ Duration target reached ({duration_days} days)")
                    break

                if self.stats.debates_conducted >= target_debates:
                    logger.info(f"✅ Debate target reached ({target_debates} debates)")
                    break

                logger.info(f"\n{'='*80}")
                logger.info(f"CYCLE #{cycle_count} - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*80}")

                # Run accumulation cycle
                await self._run_accumulation_cycle()

                # Progress report
                self._print_progress_report(target_debates)

                # Wait for next cycle
                logger.info(f"\n⏳ Waiting {self.news_check_interval // 60} minutes until next cycle...")
                await asyncio.sleep(self.news_check_interval)

        except KeyboardInterrupt:
            logger.info("\n\n⚠️ Accumulation stopped by user")

        except Exception as e:
            logger.error(f"\n❌ Accumulation error: {e}")
            self.stats.errors.append({
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "phase": self.current_phase.value
            })

        finally:
            self.is_running = False
            self.stats.end_time = datetime.now()
            self._print_final_report()

    async def _run_accumulation_cycle(self):
        """Run single accumulation cycle"""

        # Phase 1: News Collection
        self.current_phase = AccumulationPhase.NEWS_COLLECTION
        logger.info("\n[PHASE 1] News Collection")
        logger.info("-" * 40)

        new_articles = await self._collect_news()

        if not new_articles:
            logger.info("   No new articles found")
            return

        # Phase 2: War Room Analysis
        self.current_phase = AccumulationPhase.WAR_ROOM_ANALYSIS
        logger.info("\n[PHASE 2] War Room Analysis")
        logger.info("-" * 40)

        debate_results = await self._run_war_room_debates(new_articles)

        # Phase 3: Constitutional Validation Logging
        if self.enable_constitutional_logging and debate_results:
            self.current_phase = AccumulationPhase.VALIDATION_LOGGING
            logger.info("\n[PHASE 3] Constitutional Validation Logging")
            logger.info("-" * 40)

            await self._log_constitutional_validations(debate_results)

        # Phase 4: Metrics Collection
        self.current_phase = AccumulationPhase.METRICS_COLLECTION
        logger.info("\n[PHASE 4] Metrics Collection")
        logger.info("-" * 40)

        self._collect_metrics(debate_results)

    async def _collect_news(self) -> List[Dict]:
        """
        Collect news from all sources

        Returns:
            List of new articles
        """
        all_articles = []

        # RSS Crawler
        if self.enable_rss and self.rss_crawler:
            try:
                logger.info("   📰 RSS Crawler...")
                rss_results = await self.rss_crawler.run_single_cycle()

                if rss_results:
                    rss_count = len(rss_results)
                    all_articles.extend(rss_results)
                    self.stats.news_articles_collected += rss_count
                    self.stats.news_sources.add("RSS")
                    logger.info(f"      ✅ {rss_count} articles from RSS")

            except Exception as e:
                logger.error(f"      ❌ RSS error: {e}")
                self.stats.errors.append({
                    "timestamp": datetime.now().isoformat(),
                    "source": "RSS",
                    "error": str(e)
                })

        # Finviz Collector
        if self.enable_finviz and self.finviz_collector:
            try:
                logger.info("   📊 Finviz Collector...")
                finviz_stats = await self.finviz_collector.run_once()

                if finviz_stats['new'] > 0:
                    self.stats.news_articles_collected += finviz_stats['new']
                    self.stats.news_sources.add("Finviz")
                    logger.info(f"      ✅ {finviz_stats['new']} articles from Finviz")

            except Exception as e:
                logger.error(f"      ❌ Finviz error: {e}")
                self.stats.errors.append({
                    "timestamp": datetime.now().isoformat(),
                    "source": "Finviz",
                    "error": str(e)
                })

        logger.info(f"\n   Total new articles: {len(all_articles)}")
        return all_articles

    async def _run_war_room_debates(self, articles: List[Dict]) -> List[Dict]:
        """
        Run War Room debates on collected articles

        Args:
            articles: List of article data

        Returns:
            List of debate results
        """
        if not articles:
            return []

        # Limit batch size
        batch = articles[:self.war_room_batch_size]
        logger.info(f"   Processing {len(batch)} articles (max {self.war_room_batch_size})")

        debate_results = []

        with get_sync_session() as session:
            # Initialize debate engine with session
            if not self.debate_engine:
                self.debate_engine = ConstitutionalDebateEngine(
                    db_session=session,
                    strict_mode=False  # Don't throw on violations, just log
                )

            for i, article in enumerate(batch, 1):
                try:
                    logger.info(f"\n   [{i}/{len(batch)}] Analyzing: {article.get('db_article', {}).get('title', 'Unknown')[:50]}...")

                    # Prepare market context
                    market_context = await self._build_market_context(article)

                    # Run debate + constitutional validation
                    debate_result, is_constitutional, violations = self.debate_engine.debate_and_validate(
                        news_item=self._convert_article_to_news_item(article),
                        market_context=market_context
                    )

                    # Record stats
                    self.stats.debates_conducted += 1
                    ticker = debate_result.final_signal.ticker
                    self.stats.tickers_analyzed.add(ticker)
                    self.stats.signal_distribution[debate_result.final_signal.action.value] += 1
                    self.stats.record_confidence(debate_result.consensus_confidence)

                    # Constitutional stats
                    self.stats.constitutional_validations += 1
                    if not is_constitutional:
                        self.stats.constitutional_violations += 1
                        for violation in violations:
                            self.stats.violation_types[violation] = self.stats.violation_types.get(violation, 0) + 1

                    debate_results.append({
                        "article": article,
                        "debate_result": debate_result,
                        "is_constitutional": is_constitutional,
                        "violations": violations,
                        "timestamp": datetime.now()
                    })

                    logger.info(f"      ✅ Signal: {debate_result.final_signal.action.value} {ticker}")
                    logger.info(f"      📊 Confidence: {debate_result.consensus_confidence:.1%}")
                    logger.info(f"      🏛️ Constitutional: {'✅ PASS' if is_constitutional else '❌ FAIL'}")

                    if violations:
                        logger.warning(f"      ⚠️ Violations: {', '.join(violations[:3])}")

                except Exception as e:
                    logger.error(f"      ❌ Debate error: {e}")
                    self.stats.errors.append({
                        "timestamp": datetime.now().isoformat(),
                        "article_id": article.get('db_article', {}).get('id'),
                        "error": str(e)
                    })
                    continue

        logger.info(f"\n   Debates completed: {len(debate_results)}")
        return debate_results

    async def _build_market_context(self, article: Dict) -> MarketContext:
        """
        Build market context from article

        Args:
            article: Article data

        Returns:
            MarketContext
        """
        # Extract ticker from article signals if available
        ticker = "SPY"  # Default to SPY

        if 'db_signals' in article and article['db_signals']:
            ticker = article['db_signals'][0].ticker or ticker

        # Fetch current market data (simple version)
        try:
            # Note: This is a simplified version
            # In production, you'd fetch real-time data from YahooFinanceClient
            return MarketContext(
                ticker=ticker,
                current_price=None,  # Will be fetched by debate engine if needed
                market_data={},
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.warning(f"Error building market context: {e}")
            return MarketContext(
                ticker=ticker,
                current_price=None,
                market_data={},
                timestamp=datetime.now()
            )

    def _convert_article_to_news_item(self, article: Dict) -> Dict:
        """Convert article format to news_item format"""
        db_article = article.get('db_article')

        if not db_article:
            return {}

        return {
            "title": db_article.title,
            "content": db_article.content or db_article.summary,
            "source": db_article.source,
            "published_at": db_article.published_date,
            "url": db_article.url
        }

    async def _log_constitutional_validations(self, debate_results: List[Dict]):
        """
        Log constitutional validation results to database

        Args:
            debate_results: List of debate results with validation data
        """
        # Import repository
        from backend.database.schemas.constitutional_validation_schema import (
            ConstitutionalValidationRepository
        )

        # Dual logging: Database + File
        log_file = "logs/constitutional_validations.jsonl"
        db_count = 0
        file_count = 0

        try:
            import os
            os.makedirs("logs", exist_ok=True)

            # 1. Log to database
            with get_sync_session() as session:
                repo = ConstitutionalValidationRepository(session)

                for result in debate_results:
                    try:
                        # Parse violations into structured format
                        violation_list = []
                        for vio_str in result.get("violations", []):
                            # Simple parsing (can be enhanced)
                            violation_list.append({
                                "article_number": "Unknown",
                                "article_title": vio_str,
                                "violation_type": "general",
                                "severity": "MODERATE",
                                "description": vio_str,
                                "expected_value": None,
                                "actual_value": None,
                                "was_auto_fixed": False,
                                "fix_description": None
                            })

                        # Get article ID if available
                        article_id = None
                        if "article" in result and "db_article" in result["article"]:
                            article_id = result["article"]["db_article"].id

                        # Create validation record
                        repo.create_validation(
                            ticker=result["debate_result"].final_signal.ticker,
                            action=result["debate_result"].final_signal.action.value,
                            confidence=result["debate_result"].consensus_confidence,
                            is_constitutional=result["is_constitutional"],
                            violations=violation_list if violation_list else None,
                            article_id=article_id,
                            debate_duration_ms=result["debate_result"].debate_duration_ms,
                            model_votes={
                                str(model): signal.action.value
                                for model, signal in result["debate_result"].model_votes.items()
                            }
                        )

                        db_count += 1

                    except Exception as e:
                        logger.error(f"   ❌ DB logging error for single record: {e}")
                        continue

            logger.info(f"   ✅ Logged {db_count} validations to database")

            # 2. Log to file (backup)
            with open(log_file, "a") as f:
                for result in debate_results:
                    log_entry = {
                        "timestamp": result["timestamp"].isoformat(),
                        "ticker": result["debate_result"].final_signal.ticker,
                        "action": result["debate_result"].final_signal.action.value,
                        "confidence": result["debate_result"].consensus_confidence,
                        "is_constitutional": result["is_constitutional"],
                        "violations": result["violations"]
                    }
                    f.write(json.dumps(log_entry) + "\n")
                    file_count += 1

            logger.info(f"   ✅ Logged {file_count} validations to {log_file}")

        except Exception as e:
            logger.error(f"   ❌ Logging error: {e}")

    def _collect_metrics(self, debate_results: List[Dict]):
        """
        Collect and log metrics

        Args:
            debate_results: List of debate results
        """
        if not debate_results:
            return

        # Calculate cycle metrics
        avg_confidence = sum(r["debate_result"].consensus_confidence for r in debate_results) / len(debate_results)
        constitutional_rate = sum(1 for r in debate_results if r["is_constitutional"]) / len(debate_results)

        logger.info(f"   📊 Avg Confidence: {avg_confidence:.1%}")
        logger.info(f"   🏛️ Constitutional Rate: {constitutional_rate:.1%}")

    def _print_progress_report(self, target_debates: int):
        """Print progress report"""
        logger.info(f"\n{'='*80}")
        logger.info("PROGRESS REPORT")
        logger.info(f"{'='*80}")
        logger.info(f"⏱️  Running time: {(datetime.now() - self.stats.start_time).total_seconds() / 3600:.1f} hours")
        logger.info(f"📰 News articles: {self.stats.news_articles_collected} from {len(self.stats.news_sources)} sources")
        logger.info(f"🎭 Debates: {self.stats.debates_conducted}/{target_debates} ({self.stats.debates_conducted/target_debates*100:.1f}%)")
        logger.info(f"📈 Tickers: {len(self.stats.tickers_analyzed)}")
        logger.info(f"📊 Signals: BUY={self.stats.signal_distribution['BUY']}, SELL={self.stats.signal_distribution['SELL']}, HOLD={self.stats.signal_distribution['HOLD']}")
        logger.info(f"🏛️ Constitutional: {self.stats.constitutional_validations} validations, {self.stats.constitutional_violations} violations ({self.stats.constitutional_violations/max(1,self.stats.constitutional_validations)*100:.1f}%)")
        logger.info(f"💯 Avg Confidence: {self.stats.avg_confidence:.1%}")
        logger.info(f"❌ Errors: {len(self.stats.errors)}")
        logger.info(f"{'='*80}\n")

    def _print_final_report(self):
        """Print final accumulation report"""
        duration_hours = (self.stats.end_time - self.stats.start_time).total_seconds() / 3600

        logger.info("\n" + "="*80)
        logger.info("🎯 DATA ACCUMULATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Start: {self.stats.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"End:   {self.stats.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duration: {duration_hours:.1f} hours ({duration_hours/24:.1f} days)")
        logger.info("")
        logger.info("📰 NEWS COLLECTION")
        logger.info(f"   Total articles: {self.stats.news_articles_collected}")
        logger.info(f"   Sources: {', '.join(self.stats.news_sources)}")
        logger.info("")
        logger.info("🎭 WAR ROOM DEBATES")
        logger.info(f"   Total debates: {self.stats.debates_conducted}")
        logger.info(f"   Unique tickers: {len(self.stats.tickers_analyzed)}")
        logger.info(f"   Tickers: {', '.join(sorted(list(self.stats.tickers_analyzed))[:10])}...")
        logger.info("")
        logger.info("📊 SIGNAL DISTRIBUTION")
        logger.info(f"   BUY:  {self.stats.signal_distribution['BUY']}")
        logger.info(f"   SELL: {self.stats.signal_distribution['SELL']}")
        logger.info(f"   HOLD: {self.stats.signal_distribution['HOLD']}")
        logger.info("")
        logger.info("🏛️ CONSTITUTIONAL VALIDATION")
        logger.info(f"   Total validations: {self.stats.constitutional_validations}")
        logger.info(f"   Violations: {self.stats.constitutional_violations} ({self.stats.constitutional_violations/max(1,self.stats.constitutional_validations)*100:.1f}%)")

        if self.stats.violation_types:
            logger.info("   Top violations:")
            for violation, count in sorted(self.stats.violation_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                logger.info(f"      - {violation}: {count}")

        logger.info("")
        logger.info("💯 QUALITY METRICS")
        logger.info(f"   Avg confidence: {self.stats.avg_confidence:.1%}")
        logger.info(f"   Confidence samples: {len(self.stats.confidence_samples)}")
        logger.info("")
        logger.info(f"❌ ERRORS: {len(self.stats.errors)}")

        if self.stats.errors:
            logger.info("   Recent errors:")
            for error in self.stats.errors[-5:]:
                logger.info(f"      - {error['timestamp']}: {error.get('error', 'Unknown')[:50]}")

        logger.info("="*80)

        # Save final stats to file
        stats_file = f"logs/accumulation_stats_{self.stats.end_time.strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import os
            os.makedirs("logs", exist_ok=True)

            with open(stats_file, "w") as f:
                json.dump(self.stats.to_dict(), f, indent=2)

            logger.info(f"\n✅ Stats saved to {stats_file}")
        except Exception as e:
            logger.error(f"❌ Error saving stats: {e}")


# =============================================================================
# CLI Entry Point
# =============================================================================

async def main():
    """Main entry point for data accumulation"""
    import argparse

    parser = argparse.ArgumentParser(description="Data Accumulation Orchestrator")
    parser.add_argument("--days", type=int, default=14, help="Target duration in days (default: 14)")
    parser.add_argument("--debates", type=int, default=100, help="Target number of debates (default: 100)")
    parser.add_argument("--interval", type=int, default=5, help="News check interval in minutes (default: 5)")
    parser.add_argument("--batch-size", type=int, default=5, help="War Room batch size (default: 5)")
    parser.add_argument("--no-rss", action="store_true", help="Disable RSS crawler")
    parser.add_argument("--no-finviz", action="store_true", help="Disable Finviz collector")

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = DataAccumulationOrchestrator(
        news_check_interval_minutes=args.interval,
        war_room_batch_size=args.batch_size,
        enable_rss=not args.no_rss,
        enable_finviz=not args.no_finviz
    )

    # Start accumulation
    await orchestrator.start_accumulation(
        duration_days=args.days,
        target_debates=args.debates
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    asyncio.run(main())
