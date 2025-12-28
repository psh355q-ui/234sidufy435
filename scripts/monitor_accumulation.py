"""
Data Accumulation Monitor

Real-time monitoring dashboard for data accumulation progress

Usage:
    python scripts/monitor_accumulation.py

Shows:
- Real-time progress
- Collection stats
- Debate stats
- Constitutional validation stats
- Error tracking

Author: ai-trading-system
Date: 2025-12-27
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.repository import (
    NewsRepository,
    AnalysisRepository,
    get_sync_session
)


class AccumulationMonitor:
    """Real-time accumulation monitor"""

    def __init__(self):
        self.start_time = None
        self.logs_dir = Path("logs")
        self.validation_log = self.logs_dir / "constitutional_validations.jsonl"

    def get_latest_stats_file(self) -> Optional[Path]:
        """Get latest stats file"""
        if not self.logs_dir.exists():
            return None

        stats_files = list(self.logs_dir.glob("accumulation_stats_*.json"))
        if not stats_files:
            return None

        return max(stats_files, key=lambda p: p.stat().st_mtime)

    def load_stats(self) -> Dict:
        """Load latest stats"""
        stats_file = self.get_latest_stats_file()

        if stats_file and stats_file.exists():
            with open(stats_file, "r") as f:
                return json.load(f)

        return {}

    def get_db_stats(self) -> Dict:
        """Get stats from database"""
        try:
            with get_sync_session() as session:
                news_repo = NewsRepository(session)
                analysis_repo = AnalysisRepository(session)

                # Get counts (simplified)
                # Note: These methods might not exist in actual repository
                # You'd need to add them or use raw queries

                # For now, return mock data
                return {
                    "total_articles": 0,
                    "total_analyses": 0,
                    "articles_today": 0
                }

        except Exception as e:
            return {"error": str(e)}

    def get_constitutional_stats(self) -> Dict:
        """Get constitutional validation stats"""
        if not self.validation_log.exists():
            return {
                "total": 0,
                "violations": 0,
                "pass_rate": 0.0
            }

        total = 0
        violations = 0

        try:
            with open(self.validation_log, "r") as f:
                for line in f:
                    entry = json.loads(line.strip())
                    total += 1
                    if not entry.get("is_constitutional", True):
                        violations += 1

            pass_rate = ((total - violations) / total * 100) if total > 0 else 0.0

            return {
                "total": total,
                "violations": violations,
                "pass_rate": pass_rate
            }

        except Exception as e:
            return {"error": str(e)}

    def print_dashboard(self):
        """Print monitoring dashboard"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print("=" * 80)
        print("🎯 DATA ACCUMULATION MONITOR")
        print("=" * 80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Load stats
        stats = self.load_stats()
        db_stats = self.get_db_stats()
        const_stats = self.get_constitutional_stats()

        # File-based stats (from orchestrator)
        if stats:
            print("📊 ACCUMULATION STATS (Last Session)")
            print("-" * 80)
            print(f"Duration:        {stats.get('duration_hours', 0):.1f} hours")
            print(f"News articles:   {stats.get('news_articles', 0)}")
            print(f"News sources:    {stats.get('news_sources', 0)}")
            print(f"Debates:         {stats.get('debates', 0)}")
            print(f"Unique tickers:  {stats.get('tickers', 0)}")
            print()

            signals = stats.get('signals', {})
            print(f"Signal Distribution:")
            print(f"  BUY:  {signals.get('BUY', 0)}")
            print(f"  SELL: {signals.get('SELL', 0)}")
            print(f"  HOLD: {signals.get('HOLD', 0)}")
            print()

            print(f"Avg Confidence:  {stats.get('avg_confidence', '0.0%')}")
            print(f"Errors:          {stats.get('errors', 0)}")
            print()

        # Constitutional validation stats
        print("🏛️ CONSTITUTIONAL VALIDATION")
        print("-" * 80)

        if "error" not in const_stats:
            print(f"Total validations: {const_stats['total']}")
            print(f"Violations:        {const_stats['violations']}")
            print(f"Pass rate:         {const_stats['pass_rate']:.1f}%")
        else:
            print(f"Error: {const_stats['error']}")

        print()

        # Database stats
        print("💾 DATABASE")
        print("-" * 80)

        if "error" not in db_stats:
            print(f"Total articles:    {db_stats.get('total_articles', 0)}")
            print(f"Total analyses:    {db_stats.get('total_analyses', 0)}")
            print(f"Articles today:    {db_stats.get('articles_today', 0)}")
        else:
            print(f"Error: {db_stats['error']}")

        print()

        # Recent logs
        print("📋 RECENT VALIDATIONS")
        print("-" * 80)

        if self.validation_log.exists():
            try:
                with open(self.validation_log, "r") as f:
                    lines = f.readlines()[-5:]  # Last 5

                for line in lines:
                    entry = json.loads(line.strip())
                    timestamp = entry.get("timestamp", "")[:19]  # Trim microseconds
                    ticker = entry.get("ticker", "???")
                    action = entry.get("action", "???")
                    conf = entry.get("confidence", 0.0)
                    is_const = entry.get("is_constitutional", True)

                    status = "✅ PASS" if is_const else "❌ FAIL"

                    print(f"{timestamp} | {ticker:6} | {action:4} | {conf:.0%} | {status}")

            except Exception as e:
                print(f"Error reading logs: {e}")
        else:
            print("No validation logs yet")

        print()
        print("=" * 80)
        print("Press Ctrl+C to exit")

    def run(self, refresh_seconds: int = 5):
        """Run monitoring dashboard"""
        print("Starting monitor...")
        time.sleep(1)

        try:
            while True:
                self.print_dashboard()
                time.sleep(refresh_seconds)

        except KeyboardInterrupt:
            print("\n\nMonitor stopped")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Data Accumulation Monitor")
    parser.add_argument("--refresh", type=int, default=5, help="Refresh interval in seconds (default: 5)")

    args = parser.parse_args()

    monitor = AccumulationMonitor()
    monitor.run(refresh_seconds=args.refresh)


if __name__ == "__main__":
    main()
