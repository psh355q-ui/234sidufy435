"""
MVP System Standalone Test

Direct import test without going through ai/__init__.py
"""

import os
import sys
from datetime import datetime

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_war_room_mvp_standalone():
    """Test War Room MVP with direct imports"""
    print_section("TEST: War Room MVP (Standalone)")

    try:
        # Direct imports
        from ai.mvp.war_room_mvp import WarRoomMVP

        # Initialize War Room
        war_room = WarRoomMVP()
        print("✅ War Room MVP initialized")

        # Get info
        info = war_room.get_war_room_info()
        print(f"✅ Version: {info['version']}")
        print(f"✅ Agent Structure: {info['agent_structure']}")

        for agent in info['agents']:
            print(f"   - {agent['name']}: {agent['focus']}")

        print(f"\n✅ Improvement vs Legacy:")
        print(f"   - Agent Count: {info['improvement_vs_legacy']['agent_count_reduction']}")
        print(f"   - Cost: {info['improvement_vs_legacy']['expected_cost_reduction']}")
        print(f"   - Speed: {info['improvement_vs_legacy']['expected_speed_improvement']}")

        return True

    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_agents():
    """Test individual MVP agents"""
    print_section("TEST: Individual MVP Agents")

    try:
        from ai.mvp.trader_agent_mvp import TraderAgentMVP
        from ai.mvp.risk_agent_mvp import RiskAgentMVP
        from ai.mvp.analyst_agent_mvp import AnalystAgentMVP
        from ai.mvp.pm_agent_mvp import PMAgentMVP

        # Test Trader Agent
        print("Testing Trader Agent MVP...")
        trader = TraderAgentMVP()
        trader_info = trader.get_agent_info()
        print(f"✅ Trader Agent: {trader_info['name']} (Weight: {trader_info['weight']*100}%)")

        # Test Risk Agent
        print("\nTesting Risk Agent MVP...")
        risk = RiskAgentMVP()
        risk_info = risk.get_agent_info()
        print(f"✅ Risk Agent: {risk_info['name']} (Weight: {risk_info['weight']*100}%)")
        print(f"   Hard Rules: {risk_info['hard_rules']}")

        # Test Analyst Agent
        print("\nTesting Analyst Agent MVP...")
        analyst = AnalystAgentMVP()
        analyst_info = analyst.get_agent_info()
        print(f"✅ Analyst Agent: {analyst_info['name']} (Weight: {analyst_info['weight']*100}%)")

        # Test PM Agent
        print("\nTesting PM Agent MVP...")
        pm = PMAgentMVP()
        pm_info = pm.get_agent_info()
        print(f"✅ PM Agent: {pm_info['name']}")
        print(f"   Silence Threshold: {pm_info['silence_threshold']*100}%")

        return True

    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_execution_layer():
    """Test Execution Layer"""
    print_section("TEST: Execution Layer")

    try:
        from execution.execution_router import ExecutionRouter
        from execution.order_validator import OrderValidator
        from execution.shadow_trading_mvp import ShadowTradingMVP

        # Test Router
        print("Testing Execution Router...")
        router = ExecutionRouter()
        router_info = router.get_router_info()
        print(f"✅ Execution Router: {router_info['name']}")
        print(f"   Fast Track: {router_info['estimated_time']['fast_track']}")
        print(f"   Deep Dive: {router_info['estimated_time']['deep_dive']}")

        # Test Validator
        print("\nTesting Order Validator...")
        validator = OrderValidator()
        validator_info = validator.get_validator_info()
        print(f"✅ Order Validator: {validator_info['name']}")
        print(f"   Hard Rules Count: {len(validator_info['hard_rules'])}")

        # Test Shadow Trading
        print("\nTesting Shadow Trading...")
        shadow = ShadowTradingMVP(initial_capital=100000)
        shadow_info = shadow.get_shadow_info()
        print(f"✅ Shadow Trading: Initial Capital ${shadow_info['initial_capital']:,.0f}")
        print(f"   Status: {shadow_info['status']}")

        return True

    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all standalone tests"""
    print_section("MVP SYSTEM STANDALONE TEST")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Test 1: War Room MVP
    results.append(("War Room MVP Info", test_war_room_mvp_standalone()))

    # Test 2: Individual Agents
    results.append(("Individual MVP Agents", test_individual_agents()))

    # Test 3: Execution Layer
    results.append(("Execution Layer", test_execution_layer()))

    # Summary
    print_section("TEST SUMMARY")

    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    failed_tests = total_tests - passed_tests

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n{'='*80}")
    print(f"Total: {total_tests} tests")
    print(f"Passed: {passed_tests} tests")
    print(f"Failed: {failed_tests} tests")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.0f}%")
    print(f"{'='*80}\n")

    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED! MVP System components are functional.")
        print("\n📌 Note: Full War Room deliberation test requires Gemini API key.")
        print("   Set GEMINI_API_KEY environment variable to test AI agents.")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED. Please review and fix issues.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
