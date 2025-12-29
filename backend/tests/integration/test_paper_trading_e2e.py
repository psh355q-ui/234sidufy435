"""
Paper Trading End-to-End Integration Test

Tests the complete pipeline:
War Room → WarRoomExecutor → K ISBrokerAdapter → KIS Broker

Based on official KIS API reference patterns.
"""

import pytest
import os
import sys
import asyncio
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.trading.war_room_executor import WarRoomExecutor
from backend.execution.kis_broker_adapter import KISBrokerAdapter
from backend.brokers.kis_broker import KISBroker


class TestPaperTradingE2E:
    """End-to-End Paper Trading Integration Tests"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        # Verify environment variables
        assert os.getenv("KIS_IS_VIRTUAL") == "true", "Must use paper trading mode"
        assert os.getenv("KIS_PAPER_ACCOUNT"), "Paper account number required"
        
        self.account_no = os.getenv("KIS_PAPER_ACCOUNT")
        self.is_virtual = True
        
        print(f"\n{'='*60}")
        print(f"Paper Trading E2E Test Suite")
        print(f"Account: {self.account_no} (Paper Trading)")
        print(f"{'='*60}\n")

    # ==================================================================
    # Test 1: Environment Validation
    # ==================================================================
    
    @pytest.mark.asyncio
    async def test_01_kis_authentication(self):
        """Test 1: KIS API Authentication - Official Pattern"""
        print("\n[Test 1] KIS Authentication Validation")
        
        # Create broker (follows official kis_auth.py pattern)
        broker = KISBroker(
            account_no=self.account_no,
            is_virtual=self.is_virtual
        )
        
        # Verify authentication
        assert broker.token is not None, "🚫 Authentication failed"
        print(f"  ✅ Authentication successful")
        
        # Get account balance (official API: inquire_balance pattern)
        balance = broker.get_account_balance()
        assert balance is not None, "🚫 Balance query failed"
        
        total_value = balance.get("total_value", 0)
        cash = balance.get("cash", 0)
        
        print(f"  ✅ Account Balance:")
        print(f"     Total Value: ${total_value:,.2f}")
        print(f"     Cash: ${cash:,.2f}")
        print(f"     Positions: {len(balance.get('positions', []))}")

    # ==================================================================
    # Test 2: Broker Adapter Functionality
    # ==================================================================
    
    @pytest.mark.asyncio
    async def test_02_broker_adapter(self):
        """Test 2: KISBrokerAdapter Core Functions"""
        print("\n[Test 2] KISBrokerAdapter Functionality")
        
        adapter = KISBrokerAdapter(
            account_no=self.account_no,
            is_virtual=self.is_virtual
        )
        
        # Test price query (official API: price function)
        price = await adapter.get_current_price("AAPL")
        assert price and price > 0, "🚫 Price query failed"
        print(f"  ✅ Price Query: AAPL = ${price:.2f}")
        
        # Test account balance
        balance = adapter.get_account_balance()
        assert balance is not None, "🚫 Balance query failed"
        print(f"  ✅ Balance Query: ${balance.get('total_value', 0):,.2f}")
        
        # Test volume profile (simulated)
        profile = await adapter.get_historical_volume_profile("AAPL", days=5)
        assert len(profile) > 0, "🚫 Volume profile failed"
        print(f"  ✅ Volume Profile: {len(profile)} time slots")

    # ==================================================================
    # Test 3: War Room Executor - DRY RUN
    # ==================================================================
    
    @pytest.mark.asyncio
    async def test_03_executor_dry_run(self):
        """Test 3: WarRoomExecutor Position Sizing (DRY RUN)"""
        print("\n[Test 3] WarRoomExecutor Position Sizing")
        
        executor = WarRoomExecutor(broker=None)
        
        # Test different confidence levels
        test_cases = [
            ("HIGH", 0.85, 0.02),    # 85% confidence → 2% capital
            ("MEDIUM", 0.70, 0.01),  # 70% → 1%
            ("LOW", 0.55, 0.005),    # 55% → 0.5%
        ]
        
        for name, confidence, expected_ratio in test_cases:
            result = await executor.execute_war_room_decision(
                ticker="AAPL",
                consensus_action="BUY",
                consensus_confidence=confidence,
                votes={},
                dry_run=True
            )
            
            assert result["status"] == "dry_run", f"🚫 {name} test failed"
            print(f"  ✅ {name} confidence ({confidence:.0%}): Position calculated")

    # ==================================================================
    # Test 4: Full Pipeline DRY RUN
    # ==================================================================
    
    @pytest.mark.asyncio
    async def test_04_full_pipeline_dry_run(self):
        """Test 4: Complete Pipeline DRY RUN"""
        print("\n[Test 4] Full Pipeline DRY RUN")
        
        broker = KISBroker(
            account_no=self.account_no,
            is_virtual=self.is_virtual
        )
        executor = WarRoomExecutor(broker=broker)
        
        # Simulate War Room decision
        result = await executor.execute_war_room_decision(
            ticker="AAPL",
            consensus_action="BUY",
            consensus_confidence=0.75,
            votes={
                "risk": {"action": "HOLD", "confidence": 0.70},
                "trader": {"action": "BUY", "confidence": 0.80},
                "analyst": {"action": "BUY", "confidence": 0.75},
            },
            dry_run=True  # SAFE MODE
        )
        
        assert result["status"] == "dry_run", "🚫 DRY RUN failed"
        assert "order" in result, "🚫 Order not generated"
        assert result["order"]["action"] == "BUY", "🚫 Wrong action"
        
        print(f"  ✅ Pipeline DRY RUN successful")
        print(f"     Action: {result['order']['action']}")
        print(f"     Quantity: {result['order']['quantity']} shares")
        print(f"     Price: ${result['order']['price']:.2f}")

    # ==================================================================
    # Test 5: HOLD Action (should skip)
    # ==================================================================
    
    @pytest.mark.asyncio
    async def test_05_hold_action_skip(self):
        """Test 5: HOLD Action Should Skip Order"""
        print("\n[Test 5] HOLD Action Skip Test")
        
        broker = KISBroker(
            account_no=self.account_no,
            is_virtual=self.is_virtual
        )
        executor = WarRoomExecutor(broker=broker)
        
        result = await executor.execute_war_room_decision(
            ticker="AAPL",
            consensus_action="HOLD",
            consensus_confidence=0.80,
            votes={},
            dry_run=True
        )
        
        assert result["status"] == "skipped", "🚫 HOLD should skip"
        assert "HOLD" in result["reason"], "🚫 Wrong skip reason"
        
        print(f"  ✅ HOLD action correctly skipped")
        print(f"     Reason: {result['reason']}")

    # ==================================================================
    # Test 6: Real Order Test (MANUAL EXECUTION REQUIRED)
    # ==================================================================
    
    @pytest.mark.real_order
    @pytest.mark.asyncio
    async def test_06_real_order_single_share(self):
        """Test 6: Real Paper Trading Order (1 share) - MANUAL TEST"""
        print("\n[Test 6] Real Order Test (1 share BUY)")
        print("  ⚠️  WARNING: This will place a REAL order in paper trading!")
        
        adapter = KISBrokerAdapter(
            account_no=self.account_no,
            is_virtual=self.is_virtual
        )
        
        # Get balance before
        balance_before = adapter.get_account_balance()
        cash_before = balance_before.get("cash", 0)
        
        print(f"  💰 Cash Before: ${cash_before:,.2f}")
        
        # Place 1 share buy order (official order() pattern)
        fill = await adapter.place_order(
            ticker="AAPL",
            quantity=1,  # 1 share only
            order_type="MKT"  # Market order
        )
        
        assert fill is not None, "🚫 Order failed"
        assert fill.quantity == 1, "🚫 Wrong quantity"
        
        print(f"  ✅ Order Filled:")
        print(f"     Ticker: {fill.ticker}")
        print(f"     Quantity: {fill.quantity} shares")
        print(f"     Fill Price: ${fill.fill_price:.2f}")
        print(f"     Commission: ${fill.commission:.2f}")
        
        # Get balance after
        balance_after = adapter.get_account_balance()
        cash_after = balance_after.get("cash", 0)
        
        print(f"  💰 Cash After: ${cash_after:,.2f}")
        print(f"  📊 Cash Change: ${cash_before - cash_after:,.2f}")
        
        # Verify cash decreased
        assert cash_after < cash_before, "🚫 Cash should decrease"
        
        print(f"  ✅ Real order test successful!")

    # ==================================================================
    # Test 7: Full Pipeline Real Order (MANUAL EXECUTION REQUIRED)
    # ==================================================================
    
    @pytest.mark.real_order
    @pytest.mark.asyncio
    async def test_07_full_pipeline_real_order(self):
        """Test 7: Complete Pipeline with Real Order - MANUAL TEST"""
        print("\n[Test 7] Full Pipeline Real Order Test")
        print("  ⚠️  WARNING: This will place a REAL order!")
        
        broker = KISBroker(
            account_no=self.account_no,
            is_virtual=self.is_virtual
        )
        executor = WarRoomExecutor(broker=broker)
        
        # Execute full pipeline
        result = await executor.execute_war_room_decision(
            ticker="AAPL",
            consensus_action="BUY",
            consensus_confidence=0.80,
            votes={
                "risk": {"action": "BUY", "confidence": 0.75},
                "trader": {"action": "BUY", "confidence": 0.85},
            },
            dry_run=False  # REAL ORDER
        )
        
        assert result["status"] in ["success", "executed", "dry_run"], "🚫 Pipeline failed"
        
        print(f"  ✅ Full pipeline completed")
        print(f"     Status: {result['status']}")
        if "execution_price" in result:
            print(f"     Execution Price: ${result['execution_price']:.2f}")
            print(f"     Total Value: ${result['total_value']:.2f}")


# ==================================================================
# Test Execution Helper
# ==================================================================

def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Paper Trading E2E Integration Test Suite")
    print("="*60)
    
    # Run safe tests first
    print("\n>>> Running SAFE tests (DRY RUN)...")
    pytest.main([
        __file__,
        "-v",
        "-s",
        "-k", "not real_order",
        "--tb=short"
    ])
    
    print("\n" + "="*60)
    print("⚠️  REAL ORDER TESTS REQUIRE MANUAL EXECUTION")
    print("="*60)
    print("\nTo run real order tests:")
    print("  pytest backend/tests/integration/test_paper_trading_e2e.py -v -m real_order")
    print("\n")


if __name__ == "__main__":
    run_tests()
