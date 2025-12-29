"""
Test script for Telegram Alert System
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.services.alert_manager import alert_manager


async def test_all_alerts():
    """Test all alert types"""
    print("="*60)
    print("Telegram Alert System Test")
    print("="*60)
    
    # Test 1: Simple message
    print("\n[Test 1] Simple INFO message")
    await alert_manager.send_alert(
        alert_type="TEST",
        message="Testing Telegram Alert System",
        priority="INFO"
    )
    await asyncio.sleep(2)
    
    # Test 2: Trading Alert (HIGH)
    print("\n[Test 2] Trading Alert (HIGH)")
    await alert_manager.trading_alert(
        ticker="AAPL",
        action="BUY",
        quantity=10,
        price=195.50,
        alert_type="ORDER_FILLED"
    )
    await asyncio.sleep(2)
    
    # Test 3: Circuit Breaker (CRITICAL)
    print("\n[Test 3] Circuit Breaker Alert (CRITICAL)")
    await alert_manager.circuit_breaker_alert(
        reason="Daily loss limit exceeded",
        daily_pnl=-5000,
        threshold=-5000
    )
    await asyncio.sleep(2)
    
    # Test 4: War Room Decision (MEDIUM)
    print("\n[Test 4] War Room Decision (MEDIUM)")
    await alert_manager.war_room_decision(
        ticker="NVDA",
        action="BUY",
        confidence=0.75,
        num_votes=6
    )
    await asyncio.sleep(2)
    
    # Test 5: Daily Summary (MEDIUM)
    print("\n[Test 5] Daily Summary (MEDIUM)")
    await alert_manager.daily_summary(
        total_pnl=1234.56,
        win_rate=75.5,
        num_trades=12
    )
    await asyncio.sleep(2)
    
    # Test 6: Agent Weight Adjustment (MEDIUM)
    print("\n[Test 6] Agent Weight Adjustment (MEDIUM)")
    await alert_manager.agent_weight_adjusted(
        agent_name="Risk Agent",
        old_weight=0.20,
        new_weight=0.25,
        reason="Improved accuracy (72% → 78%)"
    )
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    print("\nCheck your Telegram to see the alerts!")


if __name__ == "__main__":
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    asyncio.run(test_all_alerts())
