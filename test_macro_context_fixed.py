#!/usr/bin/env python
"""
Test Macro Context Updater with proper environment loading
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / '.env', override=True)

# Verify API key is loaded
print("="*60)
print("Environment Check")
print("="*60)
print(f"ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY')[:20]}... (loaded)")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')[:40]}... (loaded)")
print()

from backend.automation.macro_context_updater import MacroContextUpdater

if __name__ == "__main__":
    print("="*60)
    print("Testing Macro Context Updater")
    print("="*60)

    updater = MacroContextUpdater()

    try:
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

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
