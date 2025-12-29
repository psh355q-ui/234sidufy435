#!/usr/bin/env python
"""
Test Macro Context Updater
"""
import sys
sys.path.insert(0, r'D:\code\ai-trading-system')

from backend.automation.macro_context_updater import MacroContextUpdater

if __name__ == "__main__":
    print("="*60)
    print("Testing Macro Context Updater")
    print("="*60)

    updater = MacroContextUpdater()
    snapshot = updater.update_daily_snapshot()

    print("\n" + "="*60)
    print("✅ Macro Context Snapshot Created")
    print("="*60)
    print(f"Date: {snapshot.snapshot_date}")
    print(f"Regime: {snapshot.regime}")
    print(f"Fed Stance: {snapshot.fed_stance}")
    print(f"VIX: {snapshot.vix_level} ({snapshot.vix_category})")
    print(f"Market Sentiment: {snapshot.market_sentiment}")
    print(f"S&P 500 Trend: {snapshot.sp500_trend}")
    print(f"Geopolitical Risk: {snapshot.geopolitical_risk}")
    print(f"Earnings Season: {snapshot.earnings_season}")
    print(f"\nNarrative: {snapshot.dominant_narrative}")
    print("="*60)
