#!/usr/bin/env python
"""
Test Signal Generation and Paper Trading Order Execution
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / '.env', override=True)

print("="*80)
print(f"Signal Generation & Paper Trading - {datetime.now().strftime('%H:%M:%S')}")
print("="*80)
print()

# Based on our news interpretations:
# NVDA: BEARISH (72%) - Should SELL/SHORT
# AAPL: BEARISH (72%) - Should SELL/SHORT
# MSFT: BULLISH (75%) - Should BUY

signals = [
    {
        "ticker": "MSFT",
        "action": "BUY",
        "confidence": 75,
        "reasoning": "Microsoft AI services gaining enterprise traction. Bullish news interpretation with 75% confidence.",
        "quantity": 2  # Buy 2 shares for testing
    },
    {
        "ticker": "NVDA",
        "action": "SELL",  # In paper trading, we'll skip if no position
        "confidence": 72,
        "reasoning": "AI chip competition intensifying. Bearish news interpretation with 72% confidence.",
        "quantity": 1
    }
]

print("[1/3] Generating Trading Signals...")
print("-"*80)

from backend.database.repository import get_sync_session
from backend.database.models import TradingSignal

session = get_sync_session()

saved_signals = []
for signal in signals:
    try:
        # Create signal in database
        db_signal = TradingSignal(
            ticker=signal['ticker'],
            action=signal['action'],
            signal_type='NEWS_BASED',
            confidence=signal['confidence'] / 100.0,
            reasoning=signal['reasoning'],
            shares=signal['quantity'],
            source='manual_test'
        )

        session.add(db_signal)
        session.flush()  # Get ID without committing

        saved_signals.append(db_signal)
        print(f"✅ Signal generated: {signal['action']} {signal['quantity']} {signal['ticker']} (ID: {db_signal.id})")

    except Exception as e:
        print(f"❌ Failed to create signal for {signal['ticker']}: {e}")

session.commit()
print(f"\n✅ Total signals created: {len(saved_signals)}")
print()

# Step 2: Execute Orders via KIS Broker
print("[2/3] Executing Paper Trading Orders...")
print("-"*80)

from backend.brokers.kis_broker import KISBroker

broker = KISBroker(
    account_no=os.getenv('KIS_PAPER_ACCOUNT'),
    product_code='01',
    is_virtual=True
)

print()
for signal in saved_signals:
    try:
        # Get current price
        price_data = broker.get_price(signal.ticker, 'NASDAQ')
        if not price_data:
            print(f"⚠️ {signal.ticker}: Price not available, skipping order")
            continue

        current_price = price_data['current_price']
        print(f"\n{signal.ticker} - Current Price: ${current_price:.2f}")

        if signal.action == 'BUY':
            print(f"   Placing BUY order: {signal.shares} shares @ market price")

            # Execute market buy order
            result = broker.buy_market_order(
                symbol=signal.ticker,
                quantity=signal.shares,
                exchange='NASDAQ'
            )

            if result and result.get('success'):
                print(f"   ✅ BUY order executed successfully!")
                print(f"      Order ID: {result.get('order_id', 'N/A')}")
                print(f"      Estimated cost: ${current_price * signal.shares:.2f}")

                # Update signal with execution details
                signal.entry_price = current_price
                signal.alert_sent = True
            else:
                print(f"   ❌ BUY order failed: {result.get('message', 'Unknown error')}")

        elif signal.action == 'SELL':
            print(f"   ⚠️ SELL order skipped (no existing position in paper account)")
            # In real scenario, we'd check positions first

    except Exception as e:
        print(f"   ❌ Order execution failed: {e}")
        import traceback
        traceback.print_exc()

session.commit()
session.close()

print()

# Step 3: Verify Account Status
print("[3/3] Verifying Account Status...")
print("-"*80)

try:
    balance = broker.get_account_balance()

    print(f"\n   Account Balance: ${balance.get('cash', 0):,.2f}")
    print(f"   Total Value: ${balance.get('total_value', 0):,.2f}")
    print(f"   Daily P&L: ${balance.get('daily_pnl', 0):+,.2f}")

    positions = balance.get('positions', [])
    if positions:
        print(f"\n   Current Positions ({len(positions)}):")
        for pos in positions:
            print(f"      {pos.get('symbol', 'N/A'):6s}: {pos.get('quantity', 0)} shares @ ${pos.get('avg_price', 0):.2f}")
    else:
        print(f"\n   No positions (new paper trading account)")

except Exception as e:
    print(f"❌ Failed to fetch account status: {e}")

print()
print("="*80)
print("Signal Generation & Trading Complete")
print("="*80)
print()
print("Summary:")
print(f"  - Signals Generated: {len(saved_signals)}")
print(f"  - Orders Attempted: {len([s for s in saved_signals if s.action == 'BUY'])}")
print(f"  - Paper Trading Mode: ACTIVE")
print()
print("Next Steps:")
print("  1. Monitor position performance")
print("  2. Set up Price Tracking Verifier")
print("  3. Calculate actual vs predicted outcomes")
print("="*80)
