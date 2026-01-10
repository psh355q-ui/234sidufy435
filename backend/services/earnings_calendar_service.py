"""
Earnings Calendar Service
- Fetches upcoming earnings dates using yfinance
- Identifies high-impact earnings (Major Tech, S&P 500 leaders)
"""
import logging
from typing import List, Dict, Any
import yfinance as yf
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EarningsCalendarService:
    def __init__(self):
        # Major tickers to always track
        self.major_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", # Mag 7
            "AMD", "INTC", "QCOM", "AVGO", # Semis
            "JPM", "BAC", "WMT", "COST", "NFLX", "DIS" # Others
        ]

    async def get_upcoming_earnings(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Check earnings for major tickers within next N days.
        Note: yfinance earnings_dates is sometimes limited, but we try our best.
        Alternatively, could use an external API if yfinance fails.
        """
        results = []
        today = datetime.now()
        end_date = today + timedelta(days=days)
        
        logger.info(f"Checking earnings for {len(self.major_tickers)} major companies...")
        
        # Fetching one by one is slow, but 'earnings_dates' isn't batched in yf
        for ticker in self.major_tickers:
            try:
                t = yf.Ticker(ticker)
                
                # get_earnings_dates() returns a DataFrame with index as timestamp
                # Columns: 'EPS Estimate', 'Reported EPS', 'Surprise(%)'
                calendar = t.get_earnings_dates(limit=12) 
                
                if calendar is None or calendar.empty:
                    continue
                    
                # Filter for future dates within range
                # The index is the earnings date
                
                # Check next earnings date
                # We iterate through the index to find the next valid date
                
                next_date = None
                
                for date in calendar.index:
                    # date is a Timestamp
                    if date.replace(tzinfo=None) >= today.replace(tzinfo=None):
                         # Found a future date
                         # Check if it's strictly within our window?
                         # Actually calendar usually has past and future.
                         # We want the *next* one.
                         
                         # yfinance often puts the 'next' expected date in the index
                         # sometimes it's tentative
                         
                         diff = (date.replace(tzinfo=None) - today).days
                         if 0 <= diff <= days:
                             next_date = date
                             break
                
                if next_date:
                    row = calendar.loc[next_date]
                    est_eps = row.get('EPS Estimate', 'N/A')
                    
                    results.append({
                        "ticker": ticker,
                        "date": next_date.strftime("%Y-%m-%d"),
                        "days_until": (next_date.replace(tzinfo=None) - today).days,
                        "eps_estimate": str(est_eps)
                    })
                    
            except Exception as e:
                # logger.debug(f"Error checking earnings for {ticker}: {e}")
                pass
                
        # Sort by days until
        results.sort(key=lambda x: x['days_until'])
        return results
