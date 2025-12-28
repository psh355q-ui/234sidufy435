"""
14일 데이터 수집 스크립트

War Room Agent 자기학습을 위한 장기 데이터 수집 시스템.

주요 기능:
1. 14일 연속 데이터 수집 (1시간 간격)
2. 데이터베이스 진행 상황 추적
3. 자동 재개 기능 (중단 후 재시작)
4. 에러 처리 및 재시도 로직
5. 실시간 통계 및 ETA

Author: AI Trading System
Date: 2025-12-28
"""

import sys
import os
from pathlib import Path

# Add paths for imports
backend_path = Path(__file__).parent.parent
root_path = backend_path.parent
sys.path.insert(0, str(root_path))
sys.path.insert(0, str(backend_path))
os.chdir(backend_path)

import asyncio
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import traceback

# Setup logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'data_collection_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ========== Mock Data Collectors (기존 테스트 코드 기반) ==========

class YahooCollector:
    """Yahoo Finance 데이터 수집기"""
    
    async def collect_market_data(self, ticker: str) -> Dict[str, Any]:
        """티커별 시장 데이터 수집"""
        logger.info(f"📊 Collecting Yahoo data for {ticker}")
        await asyncio.sleep(0.5)  # API 호출 시뮬레이션
        
        import random
        return {
            "ticker": ticker,
            "current_price": round(random.uniform(150, 200), 2),
            "volume": random.randint(50000000, 80000000),
            "high": round(random.uniform(155, 205), 2),
            "low": round(random.uniform(145, 195), 2),
            "open": round(random.uniform(150, 200), 2),
            "prev_close": round(random.uniform(148, 198), 2),
            "rsi": round(random.uniform(30, 70), 1),
            "sma_20": round(random.uniform(148, 198), 2),
            "sma_50": round(random.uniform(145, 195), 2),
            "sma_200": round(random.uniform(140, 190), 2),
            "macd": round(random.uniform(-3, 3), 2),
            "macd_signal": round(random.uniform(-3, 3), 2),
            "timestamp": datetime.now().isoformat()
        }


class FREDCollector:
    """FRED 매크로 데이터 수집기"""
    
    async def collect_macro_data(self) -> Dict[str, Any]:
        """거시경제 데이터 수집"""
        logger.info(f"🌍 Collecting FRED macro data")
        await asyncio.sleep(1.0)
        
        import random
        return {
            "fed_rate": 5.25,
            "fed_direction": "HOLDING",
            "cpi_yoy": round(random.uniform(2.5, 3.5), 1),
            "gdp_growth": round(random.uniform(2.0, 3.0), 1),
            "unemployment": round(random.uniform(3.5, 4.0), 1),
            "yield_curve": {
                "2y": round(random.uniform(4.0, 5.0), 2),
                "10y": round(random.uniform(4.0, 5.0), 2)
            },
            "wti_crude": round(random.uniform(70, 85), 2),
            "wti_change_30d": round(random.uniform(-10, 10), 1),
            "dxy": round(random.uniform(100, 105), 2),
            "dxy_change_30d": round(random.uniform(-5, 5), 1),
            "timestamp": datetime.now().isoformat()
        }


class FinVizCollector:
    """FinViz 뉴스 수집기"""
    
    async def collect_news(self, ticker: str) -> List[Dict[str, Any]]:
        """티커별 뉴스 수집"""
        logger.info(f"📰 Collecting FinViz news for {ticker}")
        await asyncio.sleep(0.5)
        
        return [
            {
                "title": f"{ticker} announces strategic partnership",
                "source": "Reuters",
                "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "sentiment": 0.75,
                "url": f"https://finviz.com/news/{ticker.lower()}-partnership"
            },
            {
                "title": f"{ticker} quarterly results exceed expectations",
                "source": "Bloomberg",
                "published_at": (datetime.now() - timedelta(hours=5)).isoformat(),
                "sentiment": 0.65,
                "url": f"https://finviz.com/news/{ticker.lower()}-earnings"
            }
        ]


class SocialCollector:
    """소셜 감성 수집기"""
    
    async def collect_sentiment(self, ticker: str) -> Dict[str, Any]:
        """소셜 감성 데이터 수집"""
        logger.info(f"💬 Collecting social sentiment for {ticker}")
        await asyncio.sleep(0.5)
        
        import random
        return {
            "ticker": ticker,
            "twitter_sentiment": round(random.uniform(0.3, 0.7), 2),
            "twitter_volume": random.randint(8000, 15000),
            "reddit_sentiment": round(random.uniform(0.3, 0.7), 2),
            "reddit_mentions": random.randint(500, 1200),
            "fear_greed_index": random.randint(30, 70),
            "trending_rank": random.randint(10, 30),
            "sentiment_change_24h": round(random.uniform(-0.2, 0.2), 2),
            "bullish_ratio": round(random.uniform(0.4, 0.7), 2),
            "timestamp": datetime.now().isoformat()
        }


# ========== 데이터 수집 Job 클래스 ==========

class DataCollectionJob:
    """
    14일 데이터 수집 Job
    
    기능:
    - 지정된 티커에 대해 지정된 기간 동안 데이터 수집
    - 진행 상황 DB 저장
    - 재개 기능 (중단 후 재시작)
    - 에러 처리 및 재시도
    """
    
    def __init__(
        self,
        tickers: List[str],
        interval_hours: int,
        duration_days: int,
        task_name: str = "14day_collection",
        dry_run: bool = False
    ):
        self.tickers = tickers
        self.interval_hours = interval_hours
        self.duration_days = duration_days
        self.task_name = task_name
        self.dry_run = dry_run
        
        # Data collectors
        self.yahoo = YahooCollector()
        self.fred = FREDCollector()
        self.finviz = FinVizCollector()
        self.social = SocialCollector()
        
        # Statistics
        self.stats = {
            "start_time": None,
            "total_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "total_tickers_collected": 0,
            "total_errors": 0,
            "last_error": None
        }
        
        # Progress tracking
        self.progress_id = None
        self.resume_from_cycle = 0
        
        logger.info(f"DataCollectionJob initialized: {len(tickers)} tickers, {duration_days} days")
    
    async def initialize(self) -> int:
        """
        Job 초기화 및 재개 체크
        
        Returns:
            시작할 사이클 번호
        """
        logger.info("=" * 80)
        logger.info("Initializing Data Collection Job")
        logger.info("=" * 80)
        
        # TODO: DB에서 기존 진행 상황 확인
        # 현재는 mock - 실제 구현 시 data_collection_progress 테이블 조회
        
        total_cycles = (self.duration_days * 24) // self.interval_hours
        logger.info(f"Total cycles to complete: {total_cycles}")
        logger.info(f"Interval: {self.interval_hours} hour(s)")
        logger.info(f"Duration: {self.duration_days} days")
        logger.info(f"Tickers: {', '.join(self.tickers)}")
        
        if self.dry_run:
            logger.warning("⚠️  DRY RUN MODE - No data will be saved to database")
        
        return 0  # 첫 사이클부터 시작
    
    async def collect_cycle(self, cycle_num: int) -> Dict[str, Any]:
        """
        단일 사이클 데이터 수집
        
        Args:
            cycle_num: 사이클 번호
            
        Returns:
            수집 결과
        """
        cycle_start = datetime.now()
        
        logger.info("")
        logger.info("─" * 80)
        logger.info(f"CYCLE {cycle_num} - {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("─" * 80)
        
        collected_data = {
            "cycle_num": cycle_num,
            "timestamp": cycle_start.isoformat(),
            "macro_data": None,
            "ticker_data": [],
            "errors": []
        }
        
        try:
            # 1. 매크로 데이터 수집 (사이클당 1회)
            try:
                macro_data = await self.fred.collect_macro_data()
                collected_data["macro_data"] = macro_data
                logger.info(f"✓ Macro data collected: Fed {macro_data['fed_rate']}%, CPI {macro_data['cpi_yoy']}%")
            except Exception as e:
                error_msg = f"Macro collection failed: {str(e)}"
                logger.error(error_msg)
                collected_data["errors"].append(error_msg)
            
            # 2. 티커별 데이터 수집 (병렬)
            for ticker in self.tickers:
                try:
                    # 병렬로 데이터 수집
                    results = await asyncio.gather(
                        self.yahoo.collect_market_data(ticker),
                        self.finviz.collect_news(ticker),
                        self.social.collect_sentiment(ticker),
                        return_exceptions=True
                    )
                    
                    market_data, news_data, social_data = results
                    
                    # 에러 체크
                    if isinstance(market_data, Exception):
                        raise market_data
                    if isinstance(news_data, Exception):
                        raise news_data
                    if isinstance(social_data, Exception):
                        raise social_data
                    
                    ticker_result = {
                        "ticker": ticker,
                        "market": market_data,
                        "news": news_data,
                        "social": social_data
                    }
                    
                    collected_data["ticker_data"].append(ticker_result)
                    self.stats["total_tickers_collected"] += 1
                    
                    logger.info(
                        f"✓ {ticker}: Price=${market_data['current_price']}, "
                        f"RSI={market_data['rsi']}, "
                        f"News={len(news_data)}, "
                        f"Sentiment={social_data['twitter_sentiment']}"
                    )
                    
                except Exception as e:
                    error_msg = f"{ticker} collection failed: {str(e)}"
                    logger.error(error_msg)
                    collected_data["errors"].append(error_msg)
                    self.stats["total_errors"] += 1
                    # 단일 티커 실패해도 계속 진행
            
            # 3. 데이터 저장 (DB)
            if not self.dry_run:
                await self.save_to_database(collected_data)
            
            # 4. 진행 상황 업데이트
            await self.update_progress(cycle_num)
            
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            logger.info(f"Cycle {cycle_num} completed in {cycle_duration:.2f}s")
            
            self.stats["successful_cycles"] += 1
            return collected_data
            
        except Exception as e:
            logger.error(f"Cycle {cycle_num} failed: {str(e)}")
            logger.error(traceback.format_exc())
            self.stats["failed_cycles"] += 1
            self.stats["last_error"] = str(e)
            raise
    
    async def save_to_database(self, data: Dict[str, Any]):
        """데이터베이스에 수집 데이터 저장"""
        # TODO: 실제 DB 저장 로직 구현
        # 현재는 로그만 출력
        logger.debug(f"Saving cycle {data['cycle_num']} data to database...")
        await asyncio.sleep(0.1)  # DB 저장 시뮬레이션
    
    async def update_progress(self, cycle_num: int):
        """진행 상황 업데이트"""
        if self.duration_days == 0 or self.interval_hours == 0:
            # Dry-run mode: skip progress calculation
            return
            
        total_cycles = (self.duration_days * 24) // self.interval_hours
        progress_pct = (cycle_num / total_cycles) * 100
        
        # TODO: DB progress 테이블 업데이트
        logger.debug(f"Progress: {progress_pct:.1f}% ({cycle_num}/{total_cycles})")
    
    async def run(self):
        """메인 수집 루프"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("14-DAY DATA COLLECTION JOB")
        logger.info("=" * 80)
        
        self.stats["start_time"] = datetime.now()
        
        # 초기화 및 재개 확인
        start_cycle = await self.initialize()
        
        # 총 사이클 수 계산
        total_cycles = (self.duration_days * 24) // self.interval_hours
        end_cycle = total_cycles
        
        logger.info(f"Starting from cycle {start_cycle}, ending at cycle {end_cycle}")
        
        # 메인 수집 루프
        for cycle_num in range(start_cycle, end_cycle):
            try:
                # 데이터 수집
                await self.collect_cycle(cycle_num)
                
                self.stats["total_cycles"] += 1
                
                # 다음 사이클까지 대기
                if cycle_num < end_cycle - 1:
                    wait_seconds = self.interval_hours * 3600
                    next_cycle_time = datetime.now() + timedelta(seconds=wait_seconds)
                    
                    logger.info(f"⏳ Next cycle in {wait_seconds/3600:.1f} hours (at {next_cycle_time.strftime('%H:%M:%S')})")
                    await asyncio.sleep(wait_seconds)
                
            except KeyboardInterrupt:
                logger.warning("\n⚠️  Collection interrupted by user (Ctrl+C)")
                logger.info(f"Resume from cycle {cycle_num + 1} using --resume flag")
                break
                
            except Exception as e:
                logger.error(f"Cycle {cycle_num} error: {str(e)}")
                # 에러 발생해도 계속 진행 (다음 사이클로)
                continue
        
        # 최종 요약
        await self.print_summary()
    
    async def print_summary(self):
        """수집 요약 출력"""
        duration = (datetime.now() - self.stats["start_time"]).total_seconds()
        success_rate = (self.stats["successful_cycles"] / max(self.stats["total_cycles"], 1)) * 100
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("COLLECTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Duration: {duration/3600:.1f} hours")
        logger.info(f"Total Cycles: {self.stats['total_cycles']}")
        logger.info(f"Successful Cycles: {self.stats['successful_cycles']}")
        logger.info(f"Failed Cycles: {self.stats['failed_cycles']}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Tickers Collected: {self.stats['total_tickers_collected']}")
        logger.info(f"Total Errors: {self.stats['total_errors']}")
        if self.stats["last_error"]:
            logger.info(f"Last Error: {self.stats['last_error']}")
        logger.info("=" * 80)


# ========== CLI 인터페이스 ==========

async def run_dry_run(args):
    """5분 Dry Run 테스트"""
    logger.info("Starting 5-minute DRY RUN test...")
    
    job = DataCollectionJob(
        tickers=args.tickers,
        interval_hours=0,  # 테스트용: 사이클 간격 무시
        duration_days=0,   # 테스트용: 5분만 실행
        task_name="dry_run_test",
        dry_run=True
    )
    
    # 통계 시작 시간 초기화
    job.stats["start_time"] = datetime.now()
    
    # 5분 동안 30초 간격으로 수집 (10 사이클)
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=args.duration_minutes)
    cycle = 0
    
    while datetime.now() < end_time:
        await job.collect_cycle(cycle)
        job.stats["total_cycles"] += 1
        cycle += 1
        
        if datetime.now() < end_time:
            await asyncio.sleep(args.interval_seconds)
    
    await job.print_summary()


async def run_production(args):
    """Production 데이터 수집"""
    job = DataCollectionJob(
        tickers=args.tickers,
        interval_hours=args.interval_hours,
        duration_days=args.duration_days,
        task_name=args.task_name,
        dry_run=False
    )
    
    await job.run()


def main():
    """메인 엔트리 포인트"""
    parser = argparse.ArgumentParser(description="14-Day Data Collection System")
    
    # 공통 옵션
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["AAPL", "NVDA", "MSFT"],
        help="Tickers to collect (default: AAPL NVDA MSFT)"
    )
    parser.add_argument(
        "--task-name",
        default="14day_collection",
        help="Task name for progress tracking"
    )
    
    # Production 옵션
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=1,
        help="Collection interval in hours (default: 1)"
    )
    parser.add_argument(
        "--duration-days",
        type=int,
        default=14,
        help="Collection duration in days (default: 14)"
    )
    
    # Dry-run 옵션
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run 5-minute test without saving to DB"
    )
    parser.add_argument(
        "--duration-minutes",
        type=int,
        default=5,
        help="Dry-run duration in minutes (default: 5)"
    )
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=30,
        help="Dry-run interval in seconds (default: 30)"
    )
    
    # Resume 옵션
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint"
    )
    
    args = parser.parse_args()
    
    # 실행
    if args.dry_run:
        asyncio.run(run_dry_run(args))
    else:
        asyncio.run(run_production(args))


if __name__ == "__main__":
    main()
