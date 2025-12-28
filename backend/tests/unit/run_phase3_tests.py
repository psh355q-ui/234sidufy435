"""
Phase 3 Agent Improvements - Unit Tests

Tests for:
- Sentiment Agent (Fear & Greed, social sentiment)
- Risk Agent (VaR calculation)
- Analyst Agent (peer comparison)

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

os.environ["TESTING"] = "true"

import asyncio
from ai.debate.sentiment_agent import SentimentAgent
from ai.debate.risk_agent import RiskAgent
from ai.debate.analyst_agent import AnalystAgent


# ========== Sentiment Agent Tests ==========

def test_sentiment_fear_greed_extreme_fear():
    """Test Extreme Fear (< 25) triggers CONTRARIAN_BUY"""
    print("\n=== Test: Sentiment - Extreme Fear ===")
    agent = SentimentAgent()
    result = agent._analyze_fear_greed(index=18)

    assert result["level"] == "EXTREME_FEAR"
    assert result["signal"] == "CONTRARIAN_BUY"
    print(f"✓ Fear & Greed: {result['level']} → {result['signal']}")
    print(f"✓ Reasoning: {result['reasoning']}")


def test_sentiment_fear_greed_extreme_greed():
    """Test Extreme Greed (> 75) triggers CONTRARIAN_SELL"""
    print("\n=== Test: Sentiment - Extreme Greed ===")
    agent = SentimentAgent()
    result = agent._analyze_fear_greed(index=88)

    assert result["level"] == "EXTREME_GREED"
    assert result["signal"] == "CONTRARIAN_SELL"
    print(f"✓ Fear & Greed: {result['level']} → {result['signal']}")


def test_sentiment_fear_greed_neutral():
    """Test Neutral (45-55) has NEUTRAL signal"""
    print("\n=== Test: Sentiment - Neutral ===")
    agent = SentimentAgent()
    result = agent._analyze_fear_greed(index=52)

    assert result["level"] == "NEUTRAL"
    assert result["signal"] == "NEUTRAL"
    print(f"✓ Fear & Greed: {result['level']}")


async def test_sentiment_integration_buy():
    """Test Sentiment Agent BUY signal (positive sentiment + high volume)"""
    print("\n=== Test: Sentiment Integration - BUY Signal ===")
    agent = SentimentAgent()

    social_data = {
        "twitter_sentiment": 0.70,  # Strong positive
        "twitter_volume": 15000,    # High volume
        "reddit_sentiment": 0.60,
        "reddit_mentions": 900,
        "fear_greed_index": 52,
        "trending_rank": 12,
        "sentiment_change_24h": 0.15,
        "bullish_ratio": 0.72
    }

    result = await agent._analyze_with_real_data("AAPL", social_data)

    assert result["action"] == "BUY"
    assert result["confidence"] >= 0.70
    assert "긍정" in result["reasoning"]
    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning']}")


async def test_sentiment_integration_contrarian_buy():
    """Test Sentiment Agent CONTRARIAN_BUY (Extreme Fear + positive sentiment)"""
    print("\n=== Test: Sentiment Integration - Contrarian BUY ===")
    agent = SentimentAgent()

    social_data = {
        "twitter_sentiment": 0.45,
        "twitter_volume": 12000,
        "reddit_sentiment": 0.30,
        "reddit_mentions": 800,
        "fear_greed_index": 18,  # EXTREME_FEAR
        "trending_rank": 25,
        "sentiment_change_24h": 0.10,
        "bullish_ratio": 0.55
    }

    result = await agent._analyze_with_real_data("AAPL", social_data)

    assert result["action"] == "BUY"
    assert "Extreme Fear" in result["reasoning"]
    print(f"✓ Action: {result['action']} (Contrarian)")
    print(f"✓ Reasoning: {result['reasoning']}")


async def test_sentiment_integration_sell():
    """Test Sentiment Agent SELL signal (negative sentiment + extreme greed)"""
    print("\n=== Test: Sentiment Integration - SELL Signal ===")
    agent = SentimentAgent()

    social_data = {
        "twitter_sentiment": -0.55,  # Strong negative
        "twitter_volume": 18000,
        "reddit_sentiment": -0.48,
        "reddit_mentions": 1200,
        "fear_greed_index": 88,  # EXTREME_GREED
        "trending_rank": 5,
        "sentiment_change_24h": -0.20,
        "bullish_ratio": 0.30
    }

    result = await agent._analyze_with_real_data("GME", social_data)

    assert result["action"] == "SELL"
    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")


# ========== Risk Agent VaR Tests ==========

def test_risk_var_calculation():
    """Test VaR calculation with sample returns"""
    print("\n=== Test: Risk - VaR Calculation ===")
    agent = RiskAgent()

    # Sample returns (daily) - moderate volatility
    returns = [
        0.01, -0.015, 0.02, -0.01, 0.005,
        -0.008, 0.012, -0.018, 0.015, -0.012,
        0.008, -0.01, 0.018, -0.015, 0.01,
        -0.005, 0.012, -0.02, 0.01, -0.008,
        0.015, -0.01, 0.005, -0.012, 0.018,
        -0.01, 0.008, -0.015, 0.012, -0.01,
        0.005, -0.018, 0.015, -0.008, 0.01
    ]

    result = agent._calculate_var(returns, confidence_level=0.95)

    assert "var_1day" in result
    assert "cvar" in result
    assert result["var_1day"] < 0  # Should be negative (loss)
    assert result["var_1day"] > -0.05  # Should be > -5% for moderate volatility
    print(f"✓ VaR (1-day, 95%): {result['var_1day']*100:.2f}%")
    print(f"✓ CVaR: {result['cvar']*100:.2f}%")
    print(f"✓ Interpretation: {result['interpretation']}")


def test_risk_var_high_volatility():
    """Test VaR with high volatility returns (should trigger SELL)"""
    print("\n=== Test: Risk - High Volatility VaR ===")
    agent = RiskAgent()

    # High volatility returns
    returns = [
        -0.08, -0.06, -0.05, -0.03, -0.02,
        0.01, 0.02, -0.07, -0.04, -0.03,
        0.02, -0.05, -0.06, 0.01, -0.04,
        -0.05, 0.02, -0.08, -0.03, -0.02,
        0.01, -0.05, -0.04, -0.06, -0.03,
        -0.02, 0.01, -0.07, -0.05, -0.04,
        -0.03, -0.06, 0.02, -0.05, -0.08
    ]

    result = agent._calculate_var(returns, confidence_level=0.95)

    assert result["var_1day"] < -0.05  # Should be < -5% (high risk)
    print(f"✓ VaR (1-day): {result['var_1day']*100:.2f}% (HIGH RISK)")
    print(f"✓ CVaR: {result['cvar']*100:.2f}%")


def test_risk_var_low_volatility():
    """Test VaR with low volatility returns"""
    print("\n=== Test: Risk - Low Volatility VaR ===")
    agent = RiskAgent()

    # Low volatility returns
    returns = [
        0.01, -0.01, 0.02, -0.015, 0.008,
        -0.012, 0.015, -0.01, 0.012, -0.008,
        0.01, -0.015, 0.018, -0.012, 0.01,
        -0.008, 0.012, -0.01, 0.015, -0.012,
        0.008, -0.01, 0.012, -0.015, 0.01,
        -0.012, 0.015, -0.01, 0.008, -0.012,
        0.01, -0.01, 0.012, -0.015, 0.01
    ]

    result = agent._calculate_var(returns, confidence_level=0.95)

    assert result["var_1day"] > -0.02  # Should be > -2% (low risk)
    print(f"✓ VaR (1-day): {result['var_1day']*100:.2f}% (LOW RISK)")


# ========== Analyst Agent Peer Comparison Tests ==========

def test_analyst_peer_comparison_leader():
    """Test peer comparison - Sector LEADER (AAPL in Technology)"""
    print("\n=== Test: Analyst - Peer Comparison LEADER ===")
    agent = AnalystAgent()

    fundamental_data = {
        "ticker": "AAPL",
        "pe_ratio": 24.2,       # Below sector avg (28.5)
        "revenue_growth": 0.225,  # Above sector avg (15%)
        "profit_margin": 0.283    # Above sector avg (25%)
    }

    result = agent._compare_with_peers("AAPL", fundamental_data)

    assert result["competitive_position"] == "LEADER"
    assert result["competitive_score"] >= 2
    assert result["sector"] == "Technology"
    print(f"✓ Sector: {result['sector']}")
    print(f"✓ Position: {result['competitive_position']}")
    print(f"✓ Score: {result['competitive_score']}")
    print(f"✓ Reasoning: {result['reasoning']}")


def test_analyst_peer_comparison_lagging():
    """Test peer comparison - Sector LAGGING (F in Automotive)"""
    print("\n=== Test: Analyst - Peer Comparison LAGGING ===")
    agent = AnalystAgent()

    fundamental_data = {
        "ticker": "F",
        "pe_ratio": 15.5,      # Above sector avg
        "revenue_growth": 0.02,   # Below sector avg
        "profit_margin": 0.03     # Below sector avg
    }

    result = agent._compare_with_peers("F", fundamental_data)

    assert result["competitive_position"] == "LAGGING"
    assert result["competitive_score"] < 0
    print(f"✓ Sector: {result['sector']}")
    print(f"✓ Position: {result['competitive_position']}")
    print(f"✓ Score: {result['competitive_score']}")


def test_analyst_peer_comparison_competitive():
    """Test peer comparison - Sector COMPETITIVE (average performance)"""
    print("\n=== Test: Analyst - Peer Comparison COMPETITIVE ===")
    agent = AnalystAgent()

    fundamental_data = {
        "ticker": "MSFT",
        "pe_ratio": 28.0,      # Near sector avg
        "revenue_growth": 0.16,   # Slightly above avg
        "profit_margin": 0.25     # At sector avg
    }

    result = agent._compare_with_peers("MSFT", fundamental_data)

    assert result["competitive_position"] == "COMPETITIVE"
    assert -2 < result["competitive_score"] < 2
    print(f"✓ Position: {result['competitive_position']}")
    print(f"✓ Score: {result['competitive_score']}")


async def run_async_tests():
    """Run async tests"""
    # Sentiment Agent tests
    await test_sentiment_integration_buy()
    await test_sentiment_integration_contrarian_buy()
    await test_sentiment_integration_sell()


def main():
    """Run all Phase 3 tests"""
    print("=" * 80)
    print("Phase 3 Agent Improvements - Unit Tests")
    print("=" * 80)

    tests_passed = 0
    tests_failed = 0

    # Synchronous tests
    sync_tests = [
        # Sentiment Agent
        test_sentiment_fear_greed_extreme_fear,
        test_sentiment_fear_greed_extreme_greed,
        test_sentiment_fear_greed_neutral,

        # Risk Agent
        test_risk_var_calculation,
        test_risk_var_high_volatility,
        test_risk_var_low_volatility,

        # Analyst Agent
        test_analyst_peer_comparison_leader,
        test_analyst_peer_comparison_lagging,
        test_analyst_peer_comparison_competitive,
    ]

    for test in sync_tests:
        try:
            test()
            tests_passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            tests_failed += 1
        except Exception as e:
            print(f"✗ Test error: {test.__name__}")
            print(f"  Error: {e}")
            tests_failed += 1

    # Async tests
    try:
        asyncio.run(run_async_tests())
        tests_passed += 3  # 3 async tests
    except AssertionError as e:
        print(f"✗ Async test failed")
        print(f"  Error: {e}")
        tests_failed += 3
    except Exception as e:
        print(f"✗ Async test error")
        print(f"  Error: {e}")
        tests_failed += 3

    # Summary
    print("\n" + "=" * 80)
    print(f"Test Summary: {tests_passed} passed, {tests_failed} failed")
    print("=" * 80)

    if tests_failed == 0:
        print("\n✓ All Phase 3 tests passed!")
        return 0
    else:
        print(f"\n✗ {tests_failed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
