"""
KIS Broker Quick Test

Tests KIS API connectivity with current environment
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Import KIS modules (relative from backend/)
import trading.kis_client as kc
import trading.overseas_stock as osf
from brokers.kis_broker import KISBroker

print("=" * 60)
print("KIS Broker Quick Test")
print("=" * 60)

# Check environment
print("\n1. Environment Variables:")
print(f"  KIS_APP_KEY: {'✅ SET' if os.getenv('KIS_APP_KEY') else '❌ NOT SET'}")
print(f"  KIS_APP_SECRET: {'✅ SET' if os.getenv('KIS_APP_SECRET') else '❌ NOT SET'}")
print(f"  KIS_ACCOUNT_NUMBER: {os.getenv('KIS_ACCOUNT_NUMBER', '❌ NOT SET')}")
print(f"  KIS_IS_VIRTUAL: {os.getenv('KIS_IS_VIRTUAL', 'true')}")

# Check account number
account_no = os.getenv('KIS_ACCOUNT_NUMBER')
if not account_no:
    print("\n❌ KIS_ACCOUNT_NUMBER not set")
    sys.exit(1)

is_virtual = os.getenv('KIS_IS_VIRTUAL', 'true').lower() == 'true'

# Test authentication
print("\n2. Testing KIS Broker Authentication...")
try:
    broker = KISBroker(account_no=account_no, is_virtual=is_virtual)
    print(f"  ✅ Authentication successful")
    print(f"  Mode: {'Paper Trading' if is_virtual else 'Real Trading'}")
except Exception as e:
    print(f"  ❌ Authentication failed: {e}")
    sys.exit(1)

# Test price query
print("\n3. Testing Price Query (AAPL)...")
try:
    price = broker.get_price("AAPL", "NASDAQ")
    if price:
        print(f"  ✅ Price: ${price['current_price']:.2f}")
        print(f"  Change: {price['change']:+.2f} ({price['change_rate']:+.2f}%)")
    else:
        print(f"  ❌ Failed to get price")
except Exception as e:
    print(f"  ❌ Price query failed: {e}")

# Test account balance
print("\n4. Testing Account Balance...")
try:
    balance = broker.get_account_balance()
    if balance:
        print(f"  ✅ Total Value: ${balance.get('total_value', 0):,.2f}")
        print(f"  Cash: ${balance.get('cash', 0):,.2f}")
        print(f"  Positions: {len(balance.get('positions', []))}")
        
        positions = balance.get('positions', [])
        if positions:
            print(f"\n  Current Positions:")
            for pos in positions[:5]:  # Show first 5
                print(f"    - {pos['symbol']}: {pos['quantity']} shares @ ${pos['current_price']:.2f}")
    else:
        print(f"  ❌ Failed to get balance")
except Exception as e:
    print(f"  ❌ Balance query failed: {e}")

print("\n" + "=" * 60)
print("✅ KIS Broker test complete!")
print("=" * 60)
