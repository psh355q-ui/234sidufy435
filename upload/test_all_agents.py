"""
War Room All Agents Integration Test

Tests all 8 agents individually and as a complete War Room system:
1. Risk Agent (20%)
2. Trader Agent (15%)
3. Analyst Agent (15%)
4. ChipWar Agent (12%)
5. News Agent (10%)
6. Macro Agent (10%)
7. Institutional Agent (10%)
8. Sentiment Agent (8%)

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
from decimal import Decimal
from datetime import datetime, timedelta

# Import all agents
from ai.debate.risk_agent import RiskAgent
from ai.debate.trader_agent import TraderAgent
from ai.debate.analyst_agent import AnalystAgent
from ai.debate.chip_war_agent import ChipWarAgent
from ai.debate.news_agent import NewsAgent
from ai.debate.macro_agent import MacroAgent
from ai.debate.institutional_agent import InstitutionalAgent
from ai.debate.sentiment_agent import SentimentAgent


# ========== Mock Data ==========

def get_mock_market_data():
    """Mock market data for testing"""
    return {
        "current_price": 175.50,
        "volume": 65000000,
        "high": 177.20,
        "low": 174.80,
        "open": 175.00,
        "prev_close": 174.50,
        "market_cap": 2800000000000,
        "pe_ratio": 28.5,
        "dividend_yield": 0.52,
        "beta": 1.25,
        "avg_volume_30d": 55000000,
        "high_52w": 198.50,
        "low_52w": 142.30,
        "revenue_growth": 0.085,
        "profit_margin": 0.255,
        "rsi": 58.5,
        "sma_20": 173.20,
        "sma_50": 170.80,
        "sma_200": 165.50,
        "returns": [0.01, -0.015, 0.02, -0.01, 0.005, -0.008, 0.012, -0.018]
    }


def get_mock_macro_data():
    """Mock macro data for testing"""
    return {
        "fed_rate": 5.25,
        "fed_direction": "HOLDING",
        "cpi_yoy": 3.2,
        "gdp_growth": 2.5,
        "unemployment": 3.7,
        "yield_curve": -0.15,
        "wti_crude": 75.50,
        "wti_change_30d": 5.2,
        "dxy": 102.5,
        "dxy_change_30d": 2.8
    }


def get_mock_institutional_data():
    """Mock institutional data for testing"""
    return {
        "institutional_ownership": 0.645,
        "institutional_change_qoq": 0.028,
        "top_holders_count": 15,
        "insider_ownership": 0.058,
        "insider_transactions_3m": 8,
        "insider_buy_sell_ratio": 0.75
    }


def get_mock_sentiment_data():
    """Mock sentiment data for testing"""
    return {
        "twitter_sentiment": 0.55,
        "twitter_volume": 12000,
        "reddit_sentiment": 0.48,
        "reddit_mentions": 850,
        "fear_greed_index": 52,
        "trending_rank": 15,
        "sentiment_change_24h": 0.08,
        "bullish_ratio": 0.62
    }


def get_mock_news_data():
    """Mock news data for testing"""
    return [
        {
            "title": "Apple announces new AI chip partnership",
            "content": "Apple announced a major partnership with TSMC for next-generation AI chips...",
            "source": "Reuters",
            "published_at": datetime.now() - timedelta(hours=2),
            "sentiment": 0.75
        },
        {
            "title": "iPhone sales beat expectations in Q4",
            "content": "Strong iPhone 15 sales drove Apple's revenue growth in the fourth quarter...",
            "source": "Bloomberg",
            "published_at": datetime.now() - timedelta(hours=5),
            "sentiment": 0.65
        },
        {
            "title": "Concerns over Apple's China market exposure",
            "content": "Analysts express caution about Apple's heavy reliance on Chinese manufacturing...",
            "source": "CNBC",
            "published_at": datetime.now() - timedelta(hours=8),
            "sentiment": -0.45
        }
    ]


def get_mock_chipwar_data():
    """Mock ChipWar data for testing"""
    return {
        "us_export_controls": True,
        "china_restrictions": "MEDIUM",
        "taiwan_tensions": "LOW",
        "semiconductor_demand": "HIGH",
        "supply_chain_risk": "MEDIUM",
        "government_subsidies": "US_CHIPS_ACT",
        "competitor_moves": ["TSMC expanding US fabs", "Samsung investing in Texas"],
        "geopolitical_events": ["US-China tech dialogue scheduled"]
    }


# ========== Individual Agent Tests ==========

async def test_risk_agent():
    """Test Risk Agent (20% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Risk Agent (20%)")
    print("="*80)

    agent = RiskAgent()
    market_data = get_mock_market_data()

    result = await agent.analyze("AAPL", market_data)

    assert "action" in result, "Missing 'action' field"
    assert "confidence" in result, "Missing 'confidence' field"
    assert "reasoning" in result, "Missing 'reasoning' field"
    assert result["action"] in ["BUY", "SELL", "HOLD"], f"Invalid action: {result['action']}"
    assert 0.0 <= result["confidence"] <= 1.0, f"Invalid confidence: {result['confidence']}"

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning'][:100]}...")

    return result


async def test_trader_agent():
    """Test Trader Agent (15% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Trader Agent (15%)")
    print("="*80)

    agent = TraderAgent()
    market_data = get_mock_market_data()

    result = await agent.analyze("AAPL", market_data)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning'][:100]}...")

    return result


async def test_analyst_agent():
    """Test Analyst Agent (15% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Analyst Agent (15%)")
    print("="*80)

    agent = AnalystAgent()
    market_data = get_mock_market_data()

    result = await agent.analyze("AAPL", market_data)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning'][:100]}...")

    return result


async def test_chipwar_agent():
    """Test ChipWar Agent (12% voting weight)"""
    print("\n" + "="*80)
    print("TEST: ChipWar Agent (12%)")
    print("="*80)

    agent = ChipWarAgent()
    chipwar_data = get_mock_chipwar_data()

    result = await agent.analyze("AAPL", chipwar_data)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning'][:100]}...")

    return result


async def test_news_agent():
    """Test News Agent (10% voting weight)"""
    print("\n" + "="*80)
    print("TEST: News Agent (10%)")
    print("="*80)

    agent = NewsAgent()
    news_data = get_mock_news_data()

    result = await agent.analyze("AAPL", news_data)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning'][:100]}...")

    return result


async def test_macro_agent():
    """Test Macro Agent (10% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Macro Agent (10%)")
    print("="*80)

    agent = MacroAgent()
    macro_data = get_mock_macro_data()

    result = await agent.analyze("AAPL", macro_data)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning'][:100]}...")

    return result


async def test_institutional_agent():
    """Test Institutional Agent (10% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Institutional Agent (10%)")
    print("="*80)

    agent = InstitutionalAgent()
    inst_data = get_mock_institutional_data()

    result = await agent.analyze("AAPL", inst_data)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning'][:100]}...")

    return result


async def test_sentiment_agent():
    """Test Sentiment Agent (8% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Sentiment Agent (8%)")
    print("="*80)

    agent = SentimentAgent()
    sentiment_data = get_mock_sentiment_data()

    result = await agent.analyze("AAPL", sentiment_data)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning'][:100]}...")

    return result


# ========== War Room Integration Test ==========

async def test_war_room_voting():
    """Test War Room 8-agent voting system"""
    print("\n" + "="*80)
    print("TEST: War Room 8-Agent Voting System")
    print("="*80)

    # Voting weights (should total 100%)
    weights = {
        "Risk": 20,
        "Trader": 15,
        "Analyst": 15,
        "ChipWar": 12,
        "News": 10,
        "Macro": 10,
        "Institutional": 10,
        "Sentiment": 8
    }

    # Verify weights sum to 100
    total_weight = sum(weights.values())
    assert total_weight == 100, f"Weights must sum to 100%, got {total_weight}%"
    print(f"✓ Voting weights sum to {total_weight}%")

    # Collect all agent votes
    print("\nCollecting agent votes...")

    results = {
        "Risk": await test_risk_agent(),
        "Trader": await test_trader_agent(),
        "Analyst": await test_analyst_agent(),
        "ChipWar": await test_chipwar_agent(),
        "News": await test_news_agent(),
        "Macro": await test_macro_agent(),
        "Institutional": await test_institutional_agent(),
        "Sentiment": await test_sentiment_agent()
    }

    # Calculate weighted votes
    print("\n" + "="*80)
    print("Weighted Voting Results")
    print("="*80)

    vote_scores = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}

    for agent_name, result in results.items():
        action = result["action"]
        confidence = result["confidence"]
        weight = weights[agent_name]

        weighted_score = (weight / 100.0) * confidence
        vote_scores[action] += weighted_score

        print(f"{agent_name:15} | {action:4} | Conf: {confidence:.2f} | Weight: {weight:2}% | Score: {weighted_score:.4f}")

    # Determine final decision
    print("\n" + "="*80)
    print("Final War Room Decision")
    print("="*80)

    final_action = max(vote_scores, key=vote_scores.get)
    final_confidence = vote_scores[final_action]

    print(f"BUY Score:  {vote_scores['BUY']:.4f}")
    print(f"SELL Score: {vote_scores['SELL']:.4f}")
    print(f"HOLD Score: {vote_scores['HOLD']:.4f}")
    print(f"\n✓ Final Decision: {final_action} (Confidence: {final_confidence:.4f})")

    return {
        "final_action": final_action,
        "final_confidence": final_confidence,
        "vote_scores": vote_scores,
        "individual_results": results
    }


# ========== Main Test Runner ==========

async def run_all_tests():
    """Run all agent tests"""
    print("="*80)
    print("War Room All Agents Integration Test")
    print("="*80)

    tests_passed = 0
    tests_failed = 0

    try:
        # Test individual agents
        print("\n### PHASE 1: Individual Agent Tests ###")
        await test_risk_agent()
        tests_passed += 1

        await test_trader_agent()
        tests_passed += 1

        await test_analyst_agent()
        tests_passed += 1

        await test_chipwar_agent()
        tests_passed += 1

        await test_news_agent()
        tests_passed += 1

        await test_macro_agent()
        tests_passed += 1

        await test_institutional_agent()
        tests_passed += 1

        await test_sentiment_agent()
        tests_passed += 1

        # Test War Room integration
        print("\n### PHASE 2: War Room Integration Test ###")
        await test_war_room_voting()
        tests_passed += 1

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        tests_failed += 1

    # Summary
    print("\n" + "="*80)
    print(f"Test Summary: {tests_passed} passed, {tests_failed} failed")
    print("="*80)

    if tests_failed == 0:
        print("\n✓ All War Room agents are working correctly!")
        return 0
    else:
        print(f"\n✗ {tests_failed} tests failed")
        return 1


def main():
    """Main entry point"""
    return asyncio.run(run_all_tests())


if __name__ == "__main__":
    sys.exit(main())
