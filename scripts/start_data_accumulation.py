"""
Start Data Accumulation

Simple script to start the data accumulation orchestrator

Usage:
    python scripts/start_data_accumulation.py --days 14 --debates 100

Options:
    --days: Target duration (default: 14)
    --debates: Target number of debates (default: 100)
    --interval: News check interval in minutes (default: 5)
    --test: Run a quick 5-minute test

Author: ai-trading-system
Date: 2025-12-27
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.orchestration.data_accumulation_orchestrator import DataAccumulationOrchestrator


async def run_test_mode():
    """Run quick 5-minute test"""
    print("🧪 TEST MODE - Running 5-minute test\n")

    orchestrator = DataAccumulationOrchestrator(
        news_check_interval_minutes=1,  # Check every 1 minute
        war_room_batch_size=3,  # Process 3 articles max
        enable_rss=True,
        enable_finviz=True
    )

    # Run for 5 minutes or 5 debates
    await orchestrator.start_accumulation(
        duration_days=0.003,  # ~5 minutes
        target_debates=5
    )


async def run_production_mode(days: int, debates: int, interval: int):
    """Run production data accumulation"""
    print(f"🚀 PRODUCTION MODE - {days} days, {debates} target debates\n")

    orchestrator = DataAccumulationOrchestrator(
        news_check_interval_minutes=interval,
        war_room_batch_size=5,
        enable_rss=True,
        enable_finviz=True,
        enable_constitutional_logging=True
    )

    await orchestrator.start_accumulation(
        duration_days=days,
        target_debates=debates
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Start Data Accumulation for AI Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 14-day accumulation with 100 debate target
  python scripts/start_data_accumulation.py --days 14 --debates 100

  # Quick 5-minute test
  python scripts/start_data_accumulation.py --test

  # Custom settings
  python scripts/start_data_accumulation.py --days 7 --debates 50 --interval 10
        """
    )

    parser.add_argument("--days", type=int, default=14, help="Target duration in days (default: 14)")
    parser.add_argument("--debates", type=int, default=100, help="Target number of debates (default: 100)")
    parser.add_argument("--interval", type=int, default=5, help="News check interval in minutes (default: 5)")
    parser.add_argument("--test", action="store_true", help="Run 5-minute test mode")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("logs/data_accumulation.log"),
            logging.StreamHandler()
        ]
    )

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Print banner
    print("=" * 80)
    print("🎯 AI Trading System - Data Accumulation")
    print("=" * 80)
    print()

    # Run
    if args.test:
        asyncio.run(run_test_mode())
    else:
        asyncio.run(run_production_mode(args.days, args.debates, args.interval))


if __name__ == "__main__":
    main()
