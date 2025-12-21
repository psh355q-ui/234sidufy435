"""
Seed Test Signals for Signal Consolidation Dashboard

Creates test signals from all 4 sources:
- war_room
- deep_reasoning
- manual_analysis
- news_analysis

Author: AI Trading System  
Date: 2025-12-21
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.models import TradingSignal
from backend.database.repository import get_sync_session


def create_test_signals():
    """Create test signals from multiple sources"""
    db = get_sync_session()
    
    try:
        now = datetime.now()
        
        # 1. War Room signals (highest priority)
        war_room_signals = [
            TradingSignal(
                ticker="TSLA",
                action="BUY",
                signal_type="CONSENSUS",
                confidence=0.82,
                reasoning="War Room Consensus: 7 agents vote BUY with high confidence. Risk Agent approved.",
                source="war_room",
                generated_at=now - timedelta(hours=2)
            ),
            TradingSignal(
                ticker="AAPL",
                action="HOLD",
                signal_type="CONSENSUS",
                confidence=0.65,
                reasoning="War Room Consensus: Mixed signals, PM recommends HOLD for now.",
                source="war_room",
                generated_at=now - timedelta(hours=5)
            )
        ]
        
        # 2. Deep Reasoning signals (high priority)
        deep_reasoning_signals = [
            TradingSignal(
                ticker="NVDA",
                action="BUY",
                signal_type="DEEP_ANALYSIS",
                confidence=0.91,
                reasoning="Deep Reasoning: Strong AI chip demand, expanding data center market. Multi-step analysis confirms uptrend.",
                source="deep_reasoning",
                generated_at=now - timedelta(hours=1)
            ),
            TradingSignal(
                ticker="MSFT",
                action="BUY",
                signal_type="DEEP_ANALYSIS",
                confidence=0.78,
                reasoning="Deep Reasoning: Azure growth acceleration, AI integration driving revenue. Positive outlook.",
                source="deep_reasoning",
                generated_at=now - timedelta(hours=4)
            )
        ]
        
        # 3. Manual Analysis signals (medium priority)
        manual_analysis_signals = [
            TradingSignal(
                ticker="GOOGL",
                action="SELL",
                signal_type="MANUAL",
                confidence=0.73,
                reasoning="Manual Analysis: Antitrust concerns, ad revenue decline. Analyst recommends reducing position.",
                source="manual_analysis",
                generated_at=now - timedelta(hours=3)
            ),
            TradingSignal(
                ticker="TSLA",
                action="HOLD",
                signal_type="MANUAL",
                confidence=0.68,
                reasoning="Manual Analysis: Production numbers stable but demand uncertainty. Wait for Q4 earnings.",
                source="manual_analysis",
                generated_at=now - timedelta(hours=1, minutes=30)
            )
        ]
        
        # 4. News Analysis signals (low priority)
        news_analysis_signals = [
            TradingSignal(
                ticker="AAPL",
                action="BUY",
                signal_type="NEWS_DRIVEN",
                confidence=0.75,
                reasoning="News Analysis: iPhone 15 Pro Max strong demand in China. Positive earnings preview.",
                source="news_analysis",
                generated_at=now - timedelta(minutes=45)
            ),
            TradingSignal(
                ticker="META",
                action="BUY",
                signal_type="NEWS_DRIVEN",
                confidence=0.81,
                reasoning="News Analysis: Q3 ad revenue beat estimates, Reality Labs improving. Multiple analyst upgrades.",
                source="news_analysis",
                generated_at=now - timedelta(hours=6)
            )
        ]
        
        # Combine all signals
        all_signals = (
            war_room_signals +
            deep_reasoning_signals +
            manual_analysis_signals +
            news_analysis_signals
        )
        
        # Add to database
        for signal in all_signals:
            db.add(signal)
        
        db.commit()
        
        print(f"✅ Created {len(all_signals)} test signals:")
        print(f"   - War Room: {len(war_room_signals)}")
        print(f"   - Deep Reasoning: {len(deep_reasoning_signals)}")
        print(f"   - Manual Analysis: {len(manual_analysis_signals)}")
        print(f"   - News Analysis: {len(news_analysis_signals)}")
        print(f"\n🎯 Signal Consolidation Dashboard ready to test!")
        
    except Exception as e:
        print(f"❌ Failed to create test signals: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    create_test_signals()
