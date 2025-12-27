"""
REAL MODE Test Script

Test War Room debate with KIS order execution

Phase 26: REAL MODE Integration
Date: 2025-12-23

Usage:
    python test_real_mode.py AAPL --execute  # Execute actual trade
    python test_real_mode.py NVDA            # Debate only (no trade)
"""

import asyncio
import sys
import os
import requests
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:8001"


def test_debate_only(ticker: str):
    """Test War Room debate without trade execution"""
    print("=" * 80)
    print(f"🏛️ War Room Debate Test (NO TRADE): {ticker}")
    print("=" * 80)

    url = f"{BACKEND_URL}/api/war-room/debate"
    payload = {"ticker": ticker}

    print(f"\n📤 POST {url}")
    print(f"   Payload: {payload}")
    print(f"   execute_trade=False (default)\n")

    try:
        response = requests.post(url, json=payload, params={"execute_trade": False})
        response.raise_for_status()

        result = response.json()

        print("✅ Debate completed successfully!\n")
        print("=" * 80)
        print("📊 Debate Results")
        print("=" * 80)

        print(f"\n🎯 Session ID: {result['session_id']}")
        print(f"🎫 Ticker: {result['ticker']}")
        print(f"📊 Signal ID: {result.get('signal_id', 'None')}")
        print(f"⚖️  Constitutional Valid: {result.get('constitutional_valid', True)}")

        print(f"\n🤝 Consensus:")
        consensus = result["consensus"]
        print(f"   Action: {consensus['action']}")
        print(f"   Confidence: {consensus['confidence']:.1%}")
        print(f"   Summary: {consensus.get('summary', 'N/A')}")

        print(f"\n🗳️  Agent Votes ({len(result['votes'])} agents):")
        for vote in result["votes"]:
            print(f"   - {vote['agent']:15} {vote['action']:4} ({vote['confidence']:.0%})")

        print(f"\n💼 Trade Execution:")
        if result.get("order_id"):
            print(f"   ✅ Order ID: {result['order_id']}")
        else:
            print(f"   ⏸️  No trade executed (execute_trade=False)")

        print("\n" + "=" * 80)

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        return None


def test_debate_with_trade(ticker: str):
    """Test War Room debate WITH KIS trade execution"""
    print("=" * 80)
    print(f"🚀 REAL MODE Test: {ticker}")
    print("=" * 80)
    print("⚠️  WARNING: This will execute REAL trade on KIS!")
    print("   Account: KIS_ACCOUNT_NUMBER from .env")
    print("   Mode: KIS_IS_VIRTUAL from .env")
    print("=" * 80)

    confirm = input("\n⚠️  Continue with REAL trade? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Trade cancelled by user")
        return None

    url = f"{BACKEND_URL}/api/war-room/debate"
    payload = {"ticker": ticker}

    print(f"\n📤 POST {url}")
    print(f"   Payload: {payload}")
    print(f"   execute_trade=True ⚠️\n")

    try:
        response = requests.post(url, json=payload, params={"execute_trade": True})
        response.raise_for_status()

        result = response.json()

        print("✅ Debate + Trade completed successfully!\n")
        print("=" * 80)
        print("📊 Debate Results")
        print("=" * 80)

        print(f"\n🎯 Session ID: {result['session_id']}")
        print(f"🎫 Ticker: {result['ticker']}")
        print(f"📊 Signal ID: {result.get('signal_id', 'None')}")
        print(f"⚖️  Constitutional Valid: {result.get('constitutional_valid', True)}")

        print(f"\n🤝 Consensus:")
        consensus = result["consensus"]
        print(f"   Action: {consensus['action']}")
        print(f"   Confidence: {consensus['confidence']:.1%}")
        print(f"   Summary: {consensus.get('summary', 'N/A')}")

        print(f"\n🗳️  Agent Votes ({len(result['votes'])} agents):")
        for vote in result["votes"]:
            print(f"   - {vote['agent']:15} {vote['action']:4} ({vote['confidence']:.0%})")

        print(f"\n💼 Trade Execution:")
        if result.get("order_id"):
            print(f"   ✅ Order executed!")
            print(f"   📋 Order ID: {result['order_id']}")
            print(f"   🎯 Action: {consensus['action']}")
            print(f"   📈 Confidence: {consensus['confidence']:.1%}")
        else:
            action = consensus['action']
            if action == "HOLD":
                print(f"   ⏸️  No trade (HOLD consensus)")
            elif consensus['confidence'] < 0.7:
                print(f"   ⏸️  No trade (confidence {consensus['confidence']:.1%} < 70%)")
            else:
                print(f"   ⚠️  Order execution failed or skipped")

        print("\n" + "=" * 80)

        # Check database
        print("\n📊 Checking database...")
        check_database(result['session_id'])

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        return None


def check_database(session_id: int):
    """Check database for saved session and order"""
    import psycopg2
    from dotenv import load_dotenv

    load_dotenv()

    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "ai_trading"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD")
        )

        cursor = conn.cursor()

        # Check debate session
        cursor.execute("""
            SELECT
                id, ticker, consensus_action, consensus_confidence,
                signal_id, created_at
            FROM ai_debate_sessions
            WHERE id = %s
        """, (session_id,))

        session = cursor.fetchone()
        if session:
            print(f"   ✅ Session #{session[0]} saved to DB")
            print(f"      Ticker: {session[1]}")
            print(f"      Action: {session[2]} ({session[3]:.1%})")
            print(f"      Signal ID: {session[4]}")

        # Check orders
        cursor.execute("""
            SELECT
                id, ticker, action, quantity, price, order_type,
                status, broker, order_id, created_at
            FROM orders
            WHERE signal_id IN (
                SELECT signal_id FROM ai_debate_sessions WHERE id = %s
            )
            ORDER BY created_at DESC
            LIMIT 1
        """, (session_id,))

        order = cursor.fetchone()
        if order:
            print(f"   ✅ Order #{order[0]} saved to DB")
            print(f"      {order[2]} {order[3]} shares of {order[1]} @ ${order[4]:.2f}")
            print(f"      Status: {order[6]}")
            print(f"      Broker: {order[7]}")
            print(f"      Order ID: {order[8]}")
        else:
            print(f"   ⏸️  No order found for this session")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"   ⚠️  Database check failed: {e}")


def main():
    """Main test runner"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_real_mode.py TICKER          # Debate only")
        print("  python test_real_mode.py TICKER --execute  # Debate + Trade")
        print("\nExamples:")
        print("  python test_real_mode.py AAPL")
        print("  python test_real_mode.py NVDA --execute")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    execute_trade = "--execute" in sys.argv

    print(f"\n{'='*80}")
    print(f"AI Trading System - REAL MODE Test")
    print(f"{'='*80}")
    print(f"Ticker: {ticker}")
    print(f"Execute Trade: {'YES ⚠️' if execute_trade else 'NO'}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    if execute_trade:
        result = test_debate_with_trade(ticker)
    else:
        result = test_debate_only(ticker)

    if result:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
