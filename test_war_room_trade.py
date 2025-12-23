"""
Test War Room debate + trade execution (DRY RUN)

Phase 25.0: Real trading test
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.api.war_room_router import debate_and_execute_trade, DebateRequest
import json


async def test_aapl():
    """Test AAPL (non-semiconductor)"""
    print("=" * 60)
    print("TEST #1: AAPL (Non-Semiconductor Stock)")
    print("=" * 60)

    request = DebateRequest(ticker="AAPL")

    try:
        result = await debate_and_execute_trade(request, dry_run=True)

        print("\n✅ TEST PASSED")
        print("\n📊 Debate Result:")
        print(f"   Consensus: {result['debate']['consensus']['action']}")
        print(f"   Confidence: {result['debate']['consensus']['confidence']:.1%}")

        print("\n🎯 Agent Votes:")
        for vote in result['debate']['votes']:
            print(f"   - {vote['agent']}: {vote['action']} ({vote['confidence']:.0%})")

        print("\n💼 Execution Result:")
        print(f"   Status: {result['execution']['status']}")
        if 'order' in result['execution']:
            order = result['execution']['order']
            print(f"   Action: {order['action']}")
            print(f"   Quantity: {order['quantity']} shares")
            print(f"   Price: ${order['price']:.2f}")
            print(f"   Total: ${result['execution']['total_value']:.2f}")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_nvda():
    """Test NVDA (semiconductor - triggers ChipWarAgent)"""
    print("\n" + "=" * 60)
    print("TEST #2: NVDA (Semiconductor Stock)")
    print("=" * 60)

    request = DebateRequest(ticker="NVDA")

    try:
        result = await debate_and_execute_trade(request, dry_run=True)

        print("\n✅ TEST PASSED")
        print("\n📊 Debate Result:")
        print(f"   Consensus: {result['debate']['consensus']['action']}")
        print(f"   Confidence: {result['debate']['consensus']['confidence']:.1%}")

        print("\n🎯 Agent Votes:")
        for vote in result['debate']['votes']:
            print(f"   - {vote['agent']}: {vote['action']} ({vote['confidence']:.0%})")

        print("\n💼 Execution Result:")
        print(f"   Status: {result['execution']['status']}")
        if 'order' in result['execution']:
            order = result['execution']['order']
            print(f"   Action: {order['action']}")
            print(f"   Quantity: {order['quantity']} shares")
            print(f"   Price: ${order['price']:.2f}")
            print(f"   Total: ${result['execution']['total_value']:.2f}")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_googl():
    """Test GOOGL (semiconductor - TPU)"""
    print("\n" + "=" * 60)
    print("TEST #3: GOOGL (Semiconductor Stock - TPU)")
    print("=" * 60)

    request = DebateRequest(ticker="GOOGL")

    try:
        result = await debate_and_execute_trade(request, dry_run=True)

        print("\n✅ TEST PASSED")
        print("\n📊 Debate Result:")
        print(f"   Consensus: {result['debate']['consensus']['action']}")
        print(f"   Confidence: {result['debate']['consensus']['confidence']:.1%}")

        print("\n🎯 Agent Votes:")
        for vote in result['debate']['votes']:
            print(f"   - {vote['agent']}: {vote['action']} ({vote['confidence']:.0%})")

        print("\n💼 Execution Result:")
        print(f"   Status: {result['execution']['status']}")
        if 'order' in result['execution']:
            order = result['execution']['order']
            print(f"   Action: {order['action']}")
            print(f"   Quantity: {order['quantity']} shares")
            print(f"   Price: ${order['price']:.2f}")
            print(f"   Total: ${result['execution']['total_value']:.2f}")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    from dotenv import load_dotenv
    load_dotenv()

    print("\n🚀 War Room + Real Trading Test Suite")
    print("📅 Date: 2025-12-23")
    print("🎯 Phase: 25.0 (Real Trading Test)")
    print("🔧 Mode: DRY RUN (Simulation)\n")

    results = []

    # Test 1: AAPL
    results.append(("AAPL", await test_aapl()))

    # Test 2: NVDA
    results.append(("NVDA", await test_nvda()))

    # Test 3: GOOGL
    results.append(("GOOGL", await test_googl()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    for ticker, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {ticker}: {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\n   Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 All tests passed! Ready for REAL MODE.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Debug required.")


if __name__ == "__main__":
    asyncio.run(main())
