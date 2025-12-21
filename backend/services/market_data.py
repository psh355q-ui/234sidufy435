"""
Market Data Service

Provides real-time market data including VIX
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def get_vix_realtime() -> float:
    """
    Get real-time VIX (Volatility Index)
    
    Returns:
        VIX value (float)
    """
    try:
        import yfinance as yf
        vix = yf.Ticker("^VIX")
        data = vix.history(period="1d")
        
        if not data.empty:
            vix_value = float(data['Close'].iloc[-1])
            logger.info(f"VIX fetched: {vix_value:.2f}")
            return vix_value
        else:
            logger.warning("VIX data empty, using fallback")
            return 18.0
            
    except Exception as e:
        logger.error(f"VIX fetch failed: {e}")
        return 18.0  # Conservative fallback


async def get_sp500_daily_change() -> float:
    """
    Get S&P 500 daily change percentage
    
    Returns:
        Daily change in percentage
    """
    try:
        import yfinance as yf
        sp500 = yf.Ticker("^GSPC")
        data = sp500.history(period="2d")
        
        if len(data) >= 2:
            current = float(data['Close'].iloc[-1])
            previous = float(data['Close'].iloc[-2])
            change_pct = ((current - previous) / previous) * 100
            logger.info(f"S&P 500 daily change: {change_pct:.2f}%")
            return change_pct
        else:
            return 0.0
            
    except Exception as e:
        logger.error(f"S&P 500 fetch failed: {e}")
        return 0.0
