"""
Market Gap Analyzer
- Pre-market/Overnight Gap Analysis
- Uses KIS Broker for real-time data or yfinance as fallback
"""
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# KIS Broker integration
from backend.brokers.kis_broker import KISBroker, get_kis_broker

logger = logging.getLogger(__name__)

class MarketGapAnalyzer:
    def __init__(self, broker: KISBroker = None):
        self.broker = broker or get_kis_broker()
        self.watched_tickers = [
            "AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "AMD", "PLTR", "SOXL"
        ] # Default watchlist if none provided

    async def analyze_gaps(self, tickers: List[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze price gaps for listed tickers.
        Gap = (Current Price - Previous Close) / Previous Close * 100
        """
        target_tickers = tickers or self.watched_tickers
        results = []
        
        # 1. Try KIS Broker first (Real-time data)
        # Note: bulk fetch not always available in KIS virtual, so we might loop or use other method
        # For MVP, we stick to yfinance for batch processing speed, or use KIS if specific precision needed.
        # Let's use yfinance for batch GAP analysis as it's faster for many tickers in pre-market.
        
        try:
            # Helper to get batch data from yfinance
            # We need 'previousClose' and 'regularMarketPrice' (or 'preMarketPrice')
            
            logger.info(f"Analyzing gaps for {len(target_tickers)} tickers using yfinance...")
            
            # Fetch data in bulk
            tickers_str = " ".join(target_tickers)
            data = yf.Tickers(tickers_str)
            
            for ticker in target_tickers:
                try:
                    info = data.tickers[ticker].info
                    
                    # Logic: 
                    # If Pre-market: Gap = (Pre-Market Price - Previous Close) / Previous Close
                    # If Market Open: Gap = (Open - Previous Close) / Previous Close 
                    # For simplicity in 'Briefing', we calculate current deviation from Prev Close
                    
                    prev_close = info.get('previousClose')
                    current_price = info.get('currentPrice') or info.get('regularMarketOpen') # Fallback
                    
                    # Pre-market data might be in 'preMarketPrice' if available
                    # yfinance info sometimes has 'preMarketPrice'
                    pre_market = info.get('preMarketPrice')
                    
                    if pre_market:
                        current_price = pre_market
                        
                    if prev_close and current_price:
                        gap_pct = ((current_price - prev_close) / prev_close) * 100
                        
                        gap_type = "NEUTRAL"
                        if gap_pct > 2.0:
                            gap_type = "GAP_UP_STRONG"
                        elif gap_pct > 0.5:
                            gap_type = "GAP_UP"
                        elif gap_pct < -2.0:
                            gap_type = "GAP_DOWN_STRONG"
                        elif gap_pct < -0.5:
                            gap_type = "GAP_DOWN"
                            
                        results.append({
                            "ticker": ticker,
                            "prev_close": prev_close,
                            "current_price": current_price,
                            "gap_pct": round(gap_pct, 2),
                            "gap_type": gap_type,
                            "volume": info.get('volume', 0)
                        })
                except Exception as e:
                    logger.debug(f"Failed to fetch gap data for {ticker}: {e}")
                    
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            
        # Sort by absolute gap magnitude
        results.sort(key=lambda x: abs(x['gap_pct']), reverse=True)
        return results

    def get_market_summary(self, gap_results: List[Dict[str, Any]]) -> str:
        """Generate a text summary of the gap analysis"""
        if not gap_results:
            return "No gap data available."
            
        up_gaps = [r for r in gap_results if r['gap_pct'] > 0]
        down_gaps = [r for r in gap_results if r['gap_pct'] < 0]
        
        summary = f"**Market Gap Analysis**\n"
        summary += f"- Up Gaps: {len(up_gaps)} | Down Gaps: {len(down_gaps)}\n"
        
        if up_gaps:
            top_up = up_gaps[0]
            summary += f"- Top Gain: {top_up['ticker']} (+{top_up['gap_pct']}%)\n"
            
        if down_gaps:
            top_down = down_gaps[0] # Already sorted by abs, so first might be biggest drop? No, need to check sort
            # results are sorted by ABS(gap), so top_down is physically biggest drop
            summary += f"- Top Loss: {top_down['ticker']} ({top_down['gap_pct']}%)\n"
            
        return summary
