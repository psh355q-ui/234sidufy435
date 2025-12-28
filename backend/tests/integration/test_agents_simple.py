"""
War Room Agents Integration Test (Simplified)

Tests agents that don't require database access:
1. Risk Agent (20%)
2. Trader Agent (15%)
3. Analyst Agent (15%)
4. ChipWar Agent (12%)
5. Macro Agent (10%)
6. Sentiment Agent (8%)

TOTAL: 90% (without News 10% and Institutional 10%)

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

# Import agents (no DB-dependent agents)
from ai.debate.risk_agent import RiskAgent
from ai.debate.trader_agent import TraderAgent
from ai.debate.analyst_agent import AnalystAgent
from ai.debate.chip_war_agent import ChipWarAgent
from ai.debate.macro_agent import MacroAgent
from ai.debate.sentiment_agent import SentimentAgent


# ========== Individual Agent Tests ==========

async def test_risk_agent():
    """Test Risk Agent (20% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Risk Agent (20%)")
    print("="*80)

    agent = RiskAgent()

    # Mock context with risk_data
    context = {
        "risk_data": {
            "volatility": 0.25,
            "beta": 1.2,
            "max_drawdown": -0.08,
            "correlation_spy": 0.85,
            "position_size": 0.05,
            "returns": [0.01, -0.02, 0.015, -0.01, 0.008]
        }
    }

    result = await agent.analyze("AAPL", context)

    assert "action" in result, "Missing 'action' field"
    assert "confidence" in result, "Missing 'confidence' field"
    assert "reasoning" in result, "Missing 'reasoning' field"
    assert result["action"] in ["BUY", "SELL", "HOLD", "REDUCE", "INCREASE", "DCA"], f"Invalid action: {result['action']}"
    assert 0.0 <= result["confidence"] <= 1.0, f"Invalid confidence: {result['confidence']}"

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Vote Weight: {agent.vote_weight*100:.0f}%")
    print(f"✓ Reasoning: {result['reasoning'][:80]}...")

    return result


async def test_trader_agent():
    """Test Trader Agent (15% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Trader Agent (15%)")
    print("="*80)

    agent = TraderAgent()

    # Mock context with market_data
    context = {
        "market_data": {
            "current_price": 175.50,
            "volume": 65000000,
            "rsi": 58.5,
            "sma_20": 173.20,
            "sma_50": 170.80,
            "sma_200": 165.50,
            "macd": 2.5,
            "macd_signal": 2.2,
            "bollinger_upper": 180.0,
            "bollinger_lower": 170.0
        }
    }

    result = await agent.analyze("AAPL", context)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD", "REDUCE", "INCREASE", "DCA"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Vote Weight: {agent.vote_weight*100:.0f}%")
    print(f"✓ Reasoning: {result['reasoning'][:80]}...")

    return result


async def test_analyst_agent():
    """Test Analyst Agent (15% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Analyst Agent (15%)")
    print("="*80)

    agent = AnalystAgent()

    # Mock context with fundamental_data
    context = {
        "fundamental_data": {
            "ticker": "AAPL",
            "pe_ratio": 24.2,
            "revenue_growth": 0.225,
            "profit_margin": 0.283,
            "roe": 0.45,
            "debt_to_equity": 1.5,
            "current_ratio": 1.2,
            "free_cash_flow": 95000000000
        }
    }

    result = await agent.analyze("AAPL", context)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD", "REDUCE", "INCREASE", "DCA"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Vote Weight: {agent.vote_weight*100:.0f}%")
    print(f"✓ Reasoning: {result['reasoning'][:80]}...")

    return result


async def test_chipwar_agent():
    """Test ChipWar Agent (12% voting weight)"""
    print("\n" + "="*80)
    print("TEST: ChipWar Agent (12%)")
    print("="*80)

    try:
        agent = ChipWarAgent(enable_self_learning=False)  # Disable self-learning for testing

        # Test with chip-related ticker
        result = await agent.analyze("NVDA", {})

        assert "action" in result, f"Missing 'action' field in result: {result}"
        assert "confidence" in result, f"Missing 'confidence' field in result: {result}"
        assert "reasoning" in result, f"Missing 'reasoning' field in result: {result}"
        assert result["action"] in ["BUY", "SELL", "HOLD", "MAINTAIN"], f"Invalid action: {result['action']}"
        assert 0.0 <= result["confidence"] <= 1.0, f"Invalid confidence: {result['confidence']}"

        # Normalize MAINTAIN to HOLD for voting
        if result["action"] == "MAINTAIN":
            result["action"] = "HOLD"

        print(f"✓ Action: {result['action']}")
        print(f"✓ Confidence: {result['confidence']:.2f}")
        print(f"✓ Vote Weight: {agent.vote_weight*100:.0f}%")
        print(f"✓ Reasoning: {result['reasoning'][:80]}...")

        return result
    except Exception as e:
        print(f"✗ ChipWar Agent Error: {e}")
        import traceback
        traceback.print_exc()
        raise


async def test_macro_agent():
    """Test Macro Agent (10% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Macro Agent (10%)")
    print("="*80)

    agent = MacroAgent()

    # Mock context with macro_data
    context = {
        "macro_data": {
            "fed_rate": 5.25,
            "fed_direction": "HOLDING",
            "cpi_yoy": 3.2,
            "gdp_growth": 2.5,
            "unemployment": 3.7,
            "yield_curve": {  # Must be dict with 2y and 10y keys
                "2y": 4.5,
                "10y": 4.35  # Inverted: 2y > 10y
            },
            "wti_crude": 75.50,
            "wti_change_30d": 5.2,
            "dxy": 102.5,
            "dxy_change_30d": 2.8
        }
    }

    result = await agent.analyze("AAPL", context)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD", "REDUCE", "INCREASE", "DCA"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Vote Weight: {agent.vote_weight*100:.0f}%")
    print(f"✓ Reasoning: {result['reasoning'][:80]}...")

    return result


async def test_sentiment_agent():
    """Test Sentiment Agent (8% voting weight)"""
    print("\n" + "="*80)
    print("TEST: Sentiment Agent (8%)")
    print("="*80)

    agent = SentimentAgent()

    # Mock context with social_data
    context = {
        "social_data": {
            "twitter_sentiment": 0.55,
            "twitter_volume": 12000,
            "reddit_sentiment": 0.48,
            "reddit_mentions": 850,
            "fear_greed_index": 52,
            "trending_rank": 15,
            "sentiment_change_24h": 0.08,
            "bullish_ratio": 0.62
        }
    }

    result = await agent.analyze("AAPL", context)

    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["action"] in ["BUY", "SELL", "HOLD", "REDUCE", "INCREASE", "DCA"]
    assert 0.0 <= result["confidence"] <= 1.0

    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Vote Weight: {agent.vote_weight*100:.0f}%")
    print(f"✓ Reasoning: {result['reasoning'][:80]}...")

    return result


# ========== Voting System Test ==========

async def test_voting_system():
    """Test 6-agent voting system (80% total) with extended actions"""
    print("\n" + "="*80)
    print("TEST: 6-Agent Voting System (80%) - Extended Actions")
    print("="*80)

    # Voting weights (should total 80%)
    weights = {
        "Risk": 20,
        "Trader": 15,
        "Analyst": 15,
        "ChipWar": 12,
        "Macro": 10,
        "Sentiment": 8
    }

    # Verify weights sum to 80 (6 agents out of 8)
    total_weight = sum(weights.values())
    assert total_weight == 80, f"Weights must sum to 80%, got {total_weight}%"
    print(f"✓ Voting weights sum to {total_weight}%")
    print("  (Note: News 10% and Institutional 10% excluded - require DB)")
    print("  Supported Actions: BUY, SELL, HOLD, MAINTAIN, REDUCE, INCREASE, DCA")

    # Collect all agent votes
    print("\nCollecting agent votes...")

    results = {
        "Risk": await test_risk_agent(),
        "Trader": await test_trader_agent(),
        "Analyst": await test_analyst_agent(),
        "ChipWar": await test_chipwar_agent(),
        "Macro": await test_macro_agent(),
        "Sentiment": await test_sentiment_agent()
    }

    # Calculate weighted votes
    print("\n" + "="*80)
    print("Weighted Voting Results")
    print("="*80)

    vote_scores = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0, "REDUCE": 0.0, "INCREASE": 0.0, "DCA": 0.0}

    for agent_name, result in results.items():
        action = result["action"]
        confidence = result["confidence"]
        weight = weights[agent_name]

        weighted_score = (weight / 100.0) * confidence
        vote_scores[action] += weighted_score

        print(f"{agent_name:15} | {action:4} | Conf: {confidence:.2f} | Weight: {weight:2}% | Score: {weighted_score:.4f}")

    # Determine final decision
    print("\n" + "="*80)
    print("Final Voting Decision (6 Agents)")
    print("="*80)

    final_action = max(vote_scores, key=vote_scores.get)
    final_confidence = vote_scores[final_action]

    print(f"BUY Score:     {vote_scores['BUY']:.4f}")
    print(f"SELL Score:    {vote_scores['SELL']:.4f}")
    print(f"HOLD Score:    {vote_scores['HOLD']:.4f}")
    print(f"REDUCE Score:  {vote_scores['REDUCE']:.4f}")
    print(f"INCREASE Score:{vote_scores['INCREASE']:.4f}")
    print(f"DCA Score:     {vote_scores['DCA']:.4f}")
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
    print("War Room Agents Integration Test (6 Agents - No DB)")
    print("="*80)

    tests_passed = 0
    tests_failed = 0

    try:
        # Test voting system (includes all individual tests)
        await test_voting_system()
        tests_passed += 7  # 6 individual + 1 voting system

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
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
        print("\n✓ All 6 War Room agents are working correctly!")
        print("\nNote: News Agent (10%) and Institutional Agent (10%) require DB and are tested separately.")
        return 0
    else:
        print(f"\n✗ {tests_failed} tests failed")
        return 1


def main():
    """Main entry point"""
    return asyncio.run(run_all_tests())


if __name__ == "__main__":
    sys.exit(main())
