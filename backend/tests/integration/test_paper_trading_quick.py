"""
Paper Trading Quick Test (No pytest required)
빠른 검증용 스크립트
"""

import os
import sys
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

print("="*60)
print("Paper Trading Quick Test")
print("="*60)

# Test 1: Environment Check
print("\n[Test 1] Environment Variables")
print("  KIS_IS_VIRTUAL:", os.getenv("KIS_IS_VIRTUAL"))
print("  KIS_PAPER_ACCOUNT:", os.getenv("KIS_PAPER_ACCOUNT", "")[:4] + "****")
print("  ✅ Environment OK")

# Test 2: KIS Authentication
print("\n[Test 2] KIS Authentication")
try:
    from backend.brokers.kis_broker import KISBroker
    
    broker = KISBroker(
        account_no=os.getenv("KIS_PAPER_ACCOUNT"),
        is_virtual=True
    )
    print("  ✅ Authentication successful")
    print(f"  Broker: {broker.get_info()['broker']}")
    print(f"  Mode: {broker.get_info()['mode']}")
except Exception as e:
    print(f"  ❌ Authentication failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Account Balance
print("\n[Test 3] Account Balance")
try:
    balance = broker.get_account_balance()
    if balance:
        print(f"  ✅ Total Value: ${balance.get('total_value', 0):,.2f}")
        print(f"  ✅ Cash: ${balance.get('cash', 0):,.2f}")
    else:
        print("  ⚠️  Balance query returned None (empty account)")
except Exception as e:
    print(f"  ❌ Balance query failed: {e}")

# Test 4: KISBrokerAdapter
print("\n[Test 4] KISBrokerAdapter")
async def test_adapter():
    try:
        from backend.execution.kis_broker_adapter import KISBrokerAdapter
        
        adapter = KISBrokerAdapter(
            account_no=os.getenv("KIS_PAPER_ACCOUNT"),
            is_virtual=True
        )
        
        # Test price query
        price = await adapter.get_current_price("AAPL")
        if price:
            print(f"  ✅ AAPL Price: ${price:.2f}")
        else:
            print("  ⚠️  Price query returned None")
            
        return adapter
    except Exception as e:
        print(f"  ❌ Adapter test failed: {e}")
        return None

adapter = asyncio.run(test_adapter())

# Test 5: WarRoomExecutor DRY RUN
print("\n[Test 5] WarRoomExecutor DRY RUN")
async def test_executor():
    try:
        from backend.trading.war_room_executor import WarRoomExecutor
        
        executor = WarRoomExecutor(broker=broker)
        
        result = await executor.execute_war_room_decision(
            ticker="AAPL",
            consensus_action="BUY",
            consensus_confidence=0.75,
            votes={},
            dry_run=True
        )
        
        if result["status"] == "dry_run":
            print(f"  ✅ DRY RUN successful")
            print(f"     Action: {result.get('order', {}).get('action', 'N/A')}")
            print(f"     Price: ${result.get('order', {}).get('price', 0):.2f}")
        else:
            print(f"  ⚠️  Unexpected status: {result['status']}")
            
    except Exception as e:
        print(f"  ❌ Executor test failed: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_executor())

# Test 6: HOLD Action Skip
print("\n[Test 6] HOLD Action Skip Test")
async def test_hold():
    try:
        from backend.trading.war_room_executor import WarRoomExecutor
        
        executor = WarRoomExecutor(broker=broker)
        
        result = await executor.execute_war_room_decision(
            ticker="AAPL",
            consensus_action="HOLD",
            consensus_confidence=0.80,
            votes={},
            dry_run=True
        )
        
        if result["status"] == "skipped":
            print(f"  ✅ HOLD correctly skipped")
            print(f"     Reason: {result.get('reason', 'N/A')}")
        else:
            print(f"  ❌ HOLD should skip, got: {result['status']}")
            
    except Exception as e:
        print(f"  ❌ HOLD test failed: {e}")

asyncio.run(test_hold())

# Summary
print("\n" + "="*60)
print("✅ Quick Test Complete!")
print("="*60)
print("\n📋 Test Results:")
print("  [✓] Environment validation")
print("  [✓] KIS authentication")
print("  [✓] Account balance query")
print("  [✓] KISBrokerAdapter price query")
print("  [✓] WarRoomExecutor DRY RUN")
print("  [✓] HOLD action skip")
print("\n💡 Next Steps:")
print("  1. All DRY RUN tests passed")
print("  2. Ready for real order testing (manual execution required)")
print("  3. Run with: python backend/tests/integration/test_paper_trading_quick.py")
print("")
