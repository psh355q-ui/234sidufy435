"""
KIS Broker Adapter for OrderExecutor

Connects KISBroker to the BrokerAPI interface used by TWAP/VWAP executors.

Author: AI Trading System
Date: 2025-12-29
"""

import os
import logging
from typing import Optional
from datetime import datetime

import pandas as pd
import numpy as np

# Import OrderExecutor interfaces
from backend.execution.executors import BrokerAPI, Fill
from backend.brokers.kis_broker import KISBroker

logger = logging.getLogger(__name__)


class KISBrokerAdapter(BrokerAPI):
    """
    KIS Broker Adapter for OrderExecutor
    
    Implements BrokerAPI interface to connect KISBroker with
    TWAP/VWAP order execution algorithms.
    
    Usage:
        adapter = KISBrokerAdapter(account_no="12345678", is_virtual=True)
        executor = TWAPExecutor(adapter)
        fills = await executor.execute("AAPL", 100, duration_minutes=30)
    """
    
    def __init__(self, account_no: str, is_virtual: bool = True):
        """
        Initialize KIS Broker Adapter
        
        Args:
            account_no: KIS account number (8 digits or "XXXX-XX" format)
            is_virtual: True for paper trading, False for real trading
        """
        self.broker = KISBroker(account_no=account_no, is_virtual=is_virtual)
        self.is_virtual = is_virtual
        
        logger.info(f"KISBrokerAdapter initialized ({'Paper Trading' if is_virtual else 'Real Trading'})")
    
    async def place_order(
        self,
        ticker: str,
        quantity: float,
        order_type: str = "MKT",
        limit_price: Optional[float] = None
    ) -> Fill:
        """
        Place an order and return fill information
        
        Args:
            ticker: Stock symbol (e.g., "AAPL")
            quantity: Number of shares (positive=buy, negative=sell)
            order_type: "MKT" (market) or "LMT" (limit)
            limit_price: Price for limit orders
        
        Returns:
            Fill object with execution details
        """
        if quantity == 0:
            raise ValueError("Quantity cannot be zero")
        
        # Determine action
        action = "BUY" if quantity > 0 else "SELL"
        qty = int(abs(quantity))
        
        logger.info(f"Placing {action} order: {qty} {ticker} @ {order_type}")
        
        try:
            # Execute order via KIS Broker
            if action == "BUY":
                if order_type == "MKT":
                    result = self.broker.buy_market_order(ticker, qty)
                else:  # LMT
                    result = self.broker.buy_limit_order(ticker, qty, limit_price)
            else:  # SELL
                if order_type == "MKT":
                    result = self.broker.sell_market_order(ticker, qty)
                else:  # LMT
                    # TODO: Implement sell_limit_order in KISBroker
                    logger.warning("SELL limit order not implemented, using market order")
                    result = self.broker.sell_market_order(ticker, qty)
            
            if not result:
                raise RuntimeError(f"Order execution failed for {ticker}")
            
            # Get fill price (use current price if not available)
            fill_price = result.get("price", 0)
            if fill_price == 0:
                price_data = self.broker.get_price(ticker, "NASDAQ")
                fill_price = price_data.get("current_price", 0) if price_data else 0
            
            # Calculate commission (KIS: 0.015% for US stocks)
            commission = abs(quantity * fill_price) * 0.00015
            
            # Create Fill object
            fill = Fill(
                timestamp=datetime.now(),
                ticker=ticker,
                quantity=quantity,  # Keep sign
                fill_price=fill_price,
                commission=commission
            )
            
            logger.info(f"Order filled: {qty} {ticker} @ ${fill_price:.2f} (commission: ${commission:.2f})")
            
            return fill
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise
    
    async def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current market price for ticker
        
        Args:
            ticker: Stock symbol
        
        Returns:
            Current price or None if unavailable
        """
        try:
            price_data = self.broker.get_price(ticker, "NASDAQ")
            
            if price_data:
                return price_data.get("current_price")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get price for {ticker}: {e}")
            return None
    
    async def get_historical_volume_profile(
        self,
        ticker: str,
        days: int = 5
    ) -> pd.Series:
        """
        Get historical volume profile (minute-level)
        
        NOTE: KIS API doesn't provide minute-level volume data easily.
        This is a simplified implementation using typical market patterns.
        
        For production, consider using:
        - Yahoo Finance historical data
        - Alpha Vantage intraday data
        - Direct market data feed
        
        Args:
            ticker: Stock symbol
            days: Number of historical days to analyze
        
        Returns:
            pd.Series indexed by time of day (09:30 - 16:00)
        """
        logger.warning(
            f"Using simulated volume profile for {ticker}. "
            "Consider implementing real historical data source."
        )
        
        # Generate typical U-shaped intraday volume profile
        # High volume at open (9:30-10:00) and close (15:30-16:00)
        # Lower volume during midday
        
        times = pd.date_range("09:30", "16:00", freq="1min").time
        profile = np.ones(len(times))
        
        # Morning spike (first 30 minutes)
        profile[:30] = 5.0
        
        # Lunch dip (11:30-13:30)
        lunch_start = 120  # 11:30 = 120 minutes from 9:30
        lunch_end = 240    # 13:30 = 240 minutes from 9:30
        profile[lunch_start:lunch_end] = 0.5
        
        # Afternoon pickup (14:00-15:30)
        afternoon_start = 270  # 14:00
        profile[afternoon_start:] = 2.0
        
        # Closing spike (last 30 minutes)
        profile[-30:] = 7.0
        
        # Normalize to sum to 1.0
        profile = profile / profile.sum()
        
        return pd.Series(profile, index=times)
    
    def get_account_balance(self) -> Optional[dict]:
        """
        Get current account balance
        
        Returns:
            Account balance dictionary
        """
        try:
            return self.broker.get_account_balance()
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            return None
    
    def is_market_open(self, exchange: str = "NASDAQ") -> bool:
        """
        Check if market is currently open
        
        Args:
            exchange: Exchange code (NASDAQ, NYSE, etc.)
        
        Returns:
            True if market is open
        """
        return self.broker.is_market_open(exchange)
    
    def get_info(self) -> dict:
        """Get broker information"""
        info = self.broker.get_info()
        info["adapter"] = "KISBrokerAdapter"
        return info


# Convenience function for quick testing
async def test_adapter():
    """Test KISBrokerAdapter"""
    import os
    
    print("=" * 60)
    print("KISBrokerAdapter Test")
    print("=" * 60)
    
    # Get account from env
    account_no = os.getenv("KIS_ACCOUNT_NUMBER")
    if not account_no:
        print("❌ KIS_ACCOUNT_NUMBER not set")
        return
    
    is_virtual = os.getenv("KIS_IS_VIRTUAL", "true").lower() == "true"
    
    # Create adapter
    print(f"\n1. Creating adapter (Virtual: {is_virtual})...")
    adapter = KISBrokerAdapter(account_no=account_no, is_virtual=is_virtual)
    
    # Get info
    info = adapter.get_info()
    print(f"  Broker: {info.get('broker')}")
    print(f"  Mode: {info.get('mode')}")
    print(f"  Adapter: {info.get('adapter')}")
    
    # Get current price
    print(f"\n2. Testing get_current_price('AAPL')...")
    price = await adapter.get_current_price("AAPL")
    print(f"  Current Price: ${price:.2f}" if price else "  ❌ Failed")
    
    # Get volume profile
    print(f"\n3. Testing get_historical_volume_profile('AAPL')...")
    profile = await adapter.get_historical_volume_profile("AAPL", days=5)
    print(f"  Profile length: {len(profile)} time slots")
    print(f"  Peak volume times:")
    top_5 = profile.nlargest(5)
    for time, vol in top_5.items():
        print(f"    {time}: {vol:.4f}")
    
    # Get account balance
    print(f"\n4. Testing get_account_balance()...")
    balance = adapter.get_account_balance()
    if balance:
        print(f"  Total Value: ${balance.get('total_value', 0):,.2f}")
        print(f"  Cash: ${balance.get('cash', 0):,.2f}")
        print(f"  Positions: {len(balance.get('positions', []))}")
    else:
        print(f"  ❌ Failed")
    
    print(f"\n5. Testing place_order (SIMULATION)...")
    print(f"  ⚠️ Skipping actual order placement in test")
    print(f"  To test orders, use integration test suite")
    
    print("\n" + "=" * 60)
    print("✅ KISBrokerAdapter test complete")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_adapter())
