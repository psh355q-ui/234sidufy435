#!/usr/bin/env python
"""
Test KIS API Connection
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / '.env', override=True)

print("="*60)
print("KIS API Connection Test")
print("="*60)

# Check environment variables
kis_is_virtual = os.getenv('KIS_IS_VIRTUAL', 'true').lower() == 'true'
kis_env = os.getenv('KIS_ENV', 'production')
paper_trading = os.getenv('FEATURE_PAPER_TRADING', 'true').lower() == 'true'

print(f"KIS_ENV: {kis_env}")
print(f"KIS_IS_VIRTUAL: {kis_is_virtual}")
print(f"FEATURE_PAPER_TRADING: {paper_trading}")
print(f"Account: {os.getenv('KIS_PAPER_ACCOUNT' if kis_is_virtual else 'KIS_ACCOUNT_NUMBER')}")
print()

# Test broker initialization
try:
    from backend.brokers.kis_broker import KISBroker

    account = os.getenv('KIS_PAPER_ACCOUNT') if kis_is_virtual else os.getenv('KIS_ACCOUNT_NUMBER')

    print(f"Initializing KIS Broker (Virtual: {kis_is_virtual})...")
    broker = KISBroker(
        account_no=account,
        product_code="01",
        is_virtual=kis_is_virtual
    )

    print("✅ KIS Broker initialized successfully!")
    print()

    # Test market data
    print("Testing market data retrieval...")
    try:
        price_data = broker.get_price("AAPL", "NASDAQ")
        if price_data:
            print(f"✅ AAPL Price: {price_data}")
        else:
            print("⚠️ No price data returned (market may be closed)")
    except Exception as e:
        print(f"❌ Price retrieval failed: {e}")

    print()

    # Test account balance
    print("Testing account balance retrieval...")
    try:
        balance = broker.get_account_balance()
        if balance:
            print(f"✅ Account Balance: {balance}")
        else:
            print("⚠️ No balance data returned")
    except Exception as e:
        print(f"❌ Balance retrieval failed: {e}")

except ImportError as e:
    print(f"❌ KIS Broker import failed: {e}")
    print("\nThis is expected if kis_client.py requires kis_devlp.yaml")
    print("We need to modify kis_client.py to use .env instead")
except Exception as e:
    print(f"❌ KIS Broker initialization failed: {e}")
    import traceback
    traceback.print_exc()

print("="*60)
