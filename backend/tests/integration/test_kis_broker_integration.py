"""
KIS Broker Authentication Test

Phase 1: Environment Setup and Verification
Tests KIS API credential configuration and broker connectivity

Author: AI Trading System
Date: 2025-12-29
"""

import os
import sys
import logging

# Load .env file
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parents[3] / '.env'
load_dotenv(env_path)
print(f"✅ Loaded environment variables from: {env_path}")

# Fix import path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, backend_dir)

from brokers.kis_broker import KISBroker, KIS_AVAILABLE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_kis_configuration():
    """Test 1: KIS API Configuration Check"""
    print("\n" + "=" * 60)
    print("Test 1: KIS API Configuration")
    print("=" * 60)
    
    # Check environment variables
    kis_app_key = os.getenv("KIS_APP_KEY")
    kis_app_secret = os.getenv("KIS_APP_SECRET")
    kis_account_no = os.getenv("KIS_ACCOUNT_NUMBER")
    kis_is_virtual = os.getenv("KIS_IS_VIRTUAL", "true")
    
    results = {
        "KIS_APP_KEY": "✅ SET" if kis_app_key else "❌ NOT SET",
        "KIS_APP_SECRET": "✅ SET" if kis_app_secret else "❌ NOT SET",
        "KIS_ACCOUNT_NUMBER": f"✅ {kis_account_no}" if kis_account_no else "❌ NOT SET",
        "KIS_IS_VIRTUAL": f"✅ {kis_is_virtual}",
        "KIS_AVAILABLE": "✅ YES" if KIS_AVAILABLE else "❌ NO"
    }
    
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    # Check if all required vars are set
    all_set = all([kis_app_key, kis_app_secret, kis_account_no])
    
    if all_set:
        print("\n✅ All required environment variables are set")
        return True, kis_account_no, kis_is_virtual == "true"
    else:
        print("\n❌ Missing required environment variables")
        return False, None, True


def test_kis_authentication(account_no: str, is_virtual: bool):
    """Test 2: KIS Broker Authentication"""
    print("\n" + "=" * 60)
    print("Test 2: KIS Broker Authentication")
    print("=" * 60)
    
    try:
        print(f"  Initializing KIS Broker...")
        print(f"    Account: {account_no}")
        print(f"    Mode: {'Virtual (Paper Trading)' if is_virtual else 'Real Trading'}")
        
        broker = KISBroker(
            account_no=account_no,
            is_virtual=is_virtual
        )
        
        # Get broker info
        info = broker.get_info()
        print(f"\n  Broker Information:")
        for key, value in info.items():
            print(f"    {key}: {value}")
        
        print("\n✅ KIS Broker authentication successful")
        return True, broker
        
    except Exception as e:
        print(f"\n❌ KIS Broker authentication failed: {e}")
        logger.error(f"Authentication error: {e}", exc_info=True)
        return False, None


def test_price_query(broker: KISBroker):
    """Test 3: Price Query Test"""
    print("\n" + "=" * 60)
    print("Test 3: Price Query Test")
    print("=" * 60)
    
    test_ticker = "AAPL"
    
    try:
        print(f"  Querying price for {test_ticker}...")
        
        price_data = broker.get_price(test_ticker, "NASDAQ")
        
        if price_data:
            print(f"\n  ✅ Price data retrieved:")
            print(f"    Symbol: {price_data.get('symbol')}")
            print(f"    Name: {price_data.get('name')}")
            print(f"    Current Price: ${price_data.get('current_price'):.2f}")
            print(f"    Change: {price_data.get('change'):+.2f} ({price_data.get('change_rate'):+.2f}%)")
            print(f"    Volume: {price_data.get('volume'):,}")
            return True
        else:
            print(f"  ❌ Failed to retrieve price data")
            return False
            
    except Exception as e:
        print(f"  ❌ Price query failed: {e}")
        logger.error(f"Price query error: {e}", exc_info=True)
        return False


def test_account_balance(broker: KISBroker):
    """Test 4: Account Balance Query"""
    print("\n" + "=" * 60)
    print("Test 4: Account Balance Query")
    print("=" * 60)
    
    try:
        print(f"  Querying account balance...")
        
        balance = broker.get_account_balance()
        
        if balance:
            print(f"\n  ✅ Account balance retrieved:")
            print(f"    Total Value: ${balance.get('total_value', 0):,.2f}")
            print(f"    Cash: ${balance.get('cash', 0):,.2f}")
            print(f"    Positions: {len(balance.get('positions', []))}")
            
            # Show positions if any
            positions = balance.get('positions', [])
            if positions:
                print(f"\n  Current Positions:")
                for pos in positions:
                    print(f"    - {pos.get('symbol')}: {pos.get('quantity')} shares @ ${pos.get('current_price'):.2f}")
                    print(f"      Market Value: ${pos.get('market_value', 0):,.2f}")
                    print(f"      P&L: ${pos.get('profit_loss', 0):+,.2f}")
            else:
                print(f"\n  No open positions")
            
            return True
        else:
            print(f"  ❌ Failed to retrieve account balance")
            return False
            
    except Exception as e:
        print(f"  ❌ Account balance query failed: {e}")
        logger.error(f"Balance query error: {e}", exc_info=True)
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("KIS Broker Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Configuration
    config_ok, account_no, is_virtual = test_kis_configuration()
    
    if not config_ok:
        print("\n⚠️  Please set KIS API environment variables:")
        print("  $env:KIS_APP_KEY='your-app-key'")
        print("  $env:KIS_APP_SECRET='your-app-secret'")
        print("  $env:KIS_ACCOUNT_NUMBER='your-account-number'")
        print("  $env:KIS_IS_VIRTUAL='true'  # or 'false' for real trading")
        sys.exit(1)
    
    # Test 2: Authentication
    auth_ok, broker = test_kis_authentication(account_no, is_virtual)
    
    if not auth_ok:
        print("\n❌ Authentication failed - cannot proceed with further tests")
        sys.exit(1)
    
    # Test 3: Price Query
    price_ok = test_price_query(broker)
    
    # Test 4: Account Balance
    balance_ok = test_account_balance(broker)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    results = [
        ("Configuration Check", config_ok),
        ("Authentication", auth_ok),
        ("Price Query", price_ok),
        ("Account Balance", balance_ok)
    ]
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! KIS Broker is ready for trading.")
        print(f"\n📊 Trading Mode: {'Paper Trading (Safe)' if is_virtual else 'REAL TRADING (Caution!)'}")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
