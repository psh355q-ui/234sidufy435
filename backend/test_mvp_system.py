"""
MVP System Test Script

Phase: MVP Consolidation
Date: 2025-12-31

Purpose:
    MVP 시스템 통합 테스트
    - War Room MVP 심의 테스트
    - Execution Router 테스트
    - Order Validator 테스트
    - Shadow Trading 테스트

Usage:
    python backend/test_mvp_system.py
"""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_war_room_mvp():
    """Test War Room MVP deliberation"""
    print_section("TEST 1: War Room MVP Deliberation")

    try:
        from ai.mvp import WarRoomMVP

        # Initialize War Room
        war_room = WarRoomMVP()
        print("✅ War Room MVP initialized")

        # Get War Room info
        info = war_room.get_war_room_info()
        print(f"✅ Agent Structure: {info['agent_structure']}")
        print(f"✅ Expected Cost Reduction: {info['improvement_vs_legacy']['expected_cost_reduction']}")
        print(f"✅ Expected Speed Improvement: {info['improvement_vs_legacy']['expected_speed_improvement']}")

        # Test data
        market_data = {
            'price_data': {
                'current_price': 150.25,
                'open': 148.50,
                'high': 151.00,
                'low': 147.80,
                'volume': 45000000,
                'high_52w': 180.00,
                'low_52w': 120.00,
                'volatility': 0.25
            },
            'technical_data': {
                'rsi': 62.5,
                'macd': {'value': 1.2, 'signal': 0.8},
                'moving_averages': {'ma50': 145.00, 'ma200': 140.00}
            },
            'market_conditions': {
                'vix': 18.5,
                'market_sentiment': 0.6,
                'is_market_open': True
            }
        }

        portfolio_state = {
            'total_value': 100000,
            'available_cash': 50000,
            'current_positions': [],
            'total_risk': 0.02,
            'position_count': 3
        }

        additional_data = {
            'news_articles': [
                {
                    'title': 'Apple announces new product line',
                    'source': 'Reuters',
                    'published': '2025-12-30',
                    'summary': 'New iPhone features AI capabilities'
                }
            ],
            'macro_indicators': {
                'interest_rate': 5.25,
                'inflation_rate': 3.1,
                'gdp_growth': 2.5,
                'fed_policy': 'hawkish'
            }
        }

        print("\n📊 Running deliberation...")
        result = war_room.deliberate(
            symbol='AAPL',
            action_context='new_position',
            market_data=market_data,
            portfolio_state=portfolio_state,
            additional_data=additional_data
        )

        print(f"\n✅ Deliberation Complete!")
        print(f"   Final Decision: {result['final_decision']}")
        print(f"   Recommended Action: {result['recommended_action']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Position Size: ${result.get('position_size_usd', 0):,.0f}")
        print(f"   Can Execute: {result.get('can_execute', False)}")

        return True

    except Exception as e:
        print(f"❌ War Room MVP Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_execution_router():
    """Test Execution Router"""
    print_section("TEST 2: Execution Router (Fast Track vs Deep Dive)")

    try:
        from execution import ExecutionRouter

        router = ExecutionRouter()
        print("✅ Execution Router initialized")

        # Test 1: Stop Loss Hit (Fast Track)
        print("\n🔴 Test 1: Stop Loss Hit (should be Fast Track)")
        result1 = router.route(
            action='sell',
            symbol='AAPL',
            current_state={
                'position_exists': True,
                'current_price': 148.0,
                'stop_loss_price': 150.0,  # Stop loss hit!
                'daily_pnl_pct': -0.03
            }
        )
        print(f"   Mode: {result1['execution_mode']}")
        print(f"   Reasoning: {result1['reasoning']}")
        print(f"   Urgency: {result1['urgency']}")
        print(f"   Bypass AI: {result1['bypass_ai']}")
        assert result1['execution_mode'] == 'fast_track', "Should be Fast Track!"
        print("   ✅ PASS")

        # Test 2: New Position (Deep Dive)
        print("\n🟢 Test 2: New Position (should be Deep Dive)")
        result2 = router.route(
            action='buy',
            symbol='NVDA',
            current_state={
                'position_exists': False,
                'current_price': 500.0,
                'daily_pnl_pct': 0.01
            }
        )
        print(f"   Mode: {result2['execution_mode']}")
        print(f"   Reasoning: {result2['reasoning']}")
        print(f"   Bypass AI: {result2['bypass_ai']}")
        assert result2['execution_mode'] == 'deep_dive', "Should be Deep Dive!"
        print("   ✅ PASS")

        # Test 3: Extreme Volatility (Fast Track)
        print("\n🔴 Test 3: Extreme Volatility (should be Fast Track)")
        result3 = router.route(
            action='sell',
            symbol='SPY',
            current_state={
                'position_exists': True,
                'current_price': 450.0,
                'daily_pnl_pct': -0.02
            },
            market_conditions={
                'vix': 45.0,  # Extreme!
                'market_status': 'volatile'
            }
        )
        print(f"   Mode: {result3['execution_mode']}")
        print(f"   Reasoning: {result3['reasoning']}")
        print(f"   Urgency: {result3['urgency']}")
        assert result3['execution_mode'] == 'fast_track', "Should be Fast Track!"
        print("   ✅ PASS")

        print("\n✅ All Execution Router tests passed!")
        return True

    except Exception as e:
        print(f"❌ Execution Router Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_order_validator():
    """Test Order Validator"""
    print_section("TEST 3: Order Validator (Hard Rules)")

    try:
        from execution import OrderValidator

        validator = OrderValidator()
        print("✅ Order Validator initialized")

        portfolio = {
            'total_value': 100000,
            'available_cash': 50000,
            'total_risk': 0.02,
            'position_count': 5
        }

        # Test 1: Valid Order
        print("\n🟢 Test 1: Valid Buy Order (should approve)")
        order1 = {
            'symbol': 'AAPL',
            'action': 'buy',
            'quantity': 100,
            'price': 150.0,
            'order_value': 15000.0,
            'position_size_pct': 0.15,  # 15%
            'stop_loss_pct': 0.02,  # 2%
            'timestamp': datetime.utcnow().isoformat()
        }
        result1 = validator.validate(order1, portfolio, {'is_market_open': True})
        print(f"   Result: {result1['result']}")
        print(f"   Can Execute: {result1['can_execute']}")
        assert result1['can_execute'] == True, "Should approve valid order!"
        print("   ✅ PASS")

        # Test 2: Position Size Too Large
        print("\n🔴 Test 2: Position Size Too Large (should reject)")
        order2 = {
            'symbol': 'NVDA',
            'action': 'buy',
            'quantity': 200,
            'price': 500.0,
            'order_value': 100000.0,
            'position_size_pct': 0.35,  # 35% - VIOLATION!
            'stop_loss_pct': 0.02,
            'timestamp': datetime.utcnow().isoformat()
        }
        result2 = validator.validate(order2, portfolio, {'is_market_open': True})
        print(f"   Result: {result2['result']}")
        print(f"   Violations: {result2['violations']}")
        print(f"   Can Execute: {result2['can_execute']}")
        assert result2['can_execute'] == False, "Should reject oversized position!"
        print("   ✅ PASS")

        # Test 3: No Stop Loss
        print("\n🔴 Test 3: No Stop Loss (should reject)")
        order3 = {
            'symbol': 'TSLA',
            'action': 'buy',
            'quantity': 50,
            'price': 200.0,
            'order_value': 10000.0,
            'position_size_pct': 0.10,
            'stop_loss_pct': 0.0,  # VIOLATION!
            'timestamp': datetime.utcnow().isoformat()
        }
        result3 = validator.validate(order3, portfolio, {'is_market_open': True})
        print(f"   Result: {result3['result']}")
        print(f"   Violations: {result3['violations']}")
        assert result3['can_execute'] == False, "Should reject order without stop loss!"
        print("   ✅ PASS")

        print("\n✅ All Order Validator tests passed!")
        return True

    except Exception as e:
        print(f"❌ Order Validator Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_shadow_trading():
    """Test Shadow Trading"""
    print_section("TEST 4: Shadow Trading System")

    try:
        from execution.shadow_trading_mvp import ShadowTradingMVP

        # Initialize
        shadow = ShadowTradingMVP(initial_capital=100000)
        print("✅ Shadow Trading initialized")

        # Start
        start_result = shadow.start(reason="MVP validation test")
        print(f"✅ Shadow Trading started: {start_result['message']}")

        # Execute buy
        print("\n📈 Executing Shadow BUY...")
        buy_result = shadow.execute_trade(
            symbol='AAPL',
            action='buy',
            quantity=100,
            price=150.0,
            stop_loss_pct=0.02
        )
        print(f"   {buy_result['message']}")
        print(f"   Available Cash: ${buy_result['available_cash']:,.0f}")
        assert buy_result['success'] == True, "Buy should succeed!"

        # Update positions (simulate price increase)
        print("\n📊 Updating positions (price +3.3%)...")
        update = shadow.update_positions({'AAPL': 155.0})
        print(f"   Total Equity: ${update['total_equity']:,.0f}")
        print(f"   Positions Value: ${update['positions_value']:,.0f}")

        # Execute sell
        print("\n📉 Executing Shadow SELL...")
        sell_result = shadow.execute_trade(
            symbol='AAPL',
            action='sell',
            quantity=100,
            price=155.0
        )
        print(f"   {sell_result['message']}")
        print(f"   PnL: ${sell_result['pnl']:,.0f} ({sell_result['pnl_pct']:.2f}%)")
        assert sell_result['success'] == True, "Sell should succeed!"
        assert sell_result['pnl'] > 0, "Should be profitable!"

        # Check performance
        print("\n📊 Performance Metrics:")
        perf = shadow.get_performance()
        print(f"   Total Trades: {perf['total_trades']}")
        print(f"   Win Rate: {perf['win_rate']*100:.1f}%")
        print(f"   Profit Factor: {perf['profit_factor']:.2f}")
        print(f"   Total PnL: ${perf['total_pnl']:,.0f} ({perf['total_pnl_pct']:.2f}%)")

        # Check success criteria
        check = shadow.check_success_criteria()
        print(f"\n📋 Success Criteria Check:")
        print(f"   {check['recommendation']}")

        print("\n✅ All Shadow Trading tests passed!")
        return True

    except Exception as e:
        print(f"❌ Shadow Trading Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print_section("MVP SYSTEM INTEGRATION TEST")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Purpose: Validate MVP system implementation")

    results = []

    # Test 1: War Room MVP
    results.append(("War Room MVP", test_war_room_mvp()))

    # Test 2: Execution Router
    results.append(("Execution Router", test_execution_router()))

    # Test 3: Order Validator
    results.append(("Order Validator", test_order_validator()))

    # Test 4: Shadow Trading
    results.append(("Shadow Trading", test_shadow_trading()))

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
        print("🎉 ALL TESTS PASSED! MVP System is ready for Shadow Trading validation.")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED. Please review and fix issues before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
