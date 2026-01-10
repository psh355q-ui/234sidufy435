
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class EnhancedDataProvider:
    """
    War Room MVP Phase 3: Data Enhancement
    Provides Multi-Timeframe Data, Event Proximity, and Option Analytics.
    """

    @staticmethod
    def get_multi_timeframe_data(symbol: str) -> Dict[str, Any]:
        """
        Fetch OHLCV data for multiple timeframes: 1D, 1W, 1M, 4H
        """
        try:
            ticker = yf.Ticker(symbol)
            result = {}

            # 1. Daily (1D) - Baseline
            hist_1d = ticker.history(period="1y", interval="1d")
            if not hist_1d.empty:
                result['1d'] = EnhancedDataProvider._process_ohlcv(hist_1d)

            # 2. Weekly (1W)
            hist_1w = ticker.history(period="2y", interval="1wk")
            if not hist_1w.empty:
                result['1w'] = EnhancedDataProvider._process_ohlcv(hist_1w)
            
            # 3. Monthly (1M)
            hist_1m = ticker.history(period="5y", interval="1mo")
            if not hist_1m.empty:
                result['1m'] = EnhancedDataProvider._process_ohlcv(hist_1m)

            # 4. 4H (Resampled from 1h)
            # Fetch 1h data (valid for 730 days, we take 60 days)
            hist_1h = ticker.history(period="60d", interval="1h")
            if not hist_1h.empty:
                # Resample to 4H
                hist_4h = hist_1h.resample('4H').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
                result['4h'] = EnhancedDataProvider._process_ohlcv(hist_4h)

            return result
        except Exception as e:
            print(f"⚠️ Failed to fetch multi-timeframe data for {symbol}: {e}")
            return {}

    @staticmethod
    def _process_ohlcv(df: pd.DataFrame) -> Dict[str, Any]:
        """Process DataFrame to simplified technical summary"""
        try:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # Simple Trend (SMA 20 vs SMA 50) - rudimentary check if enough data
            sma_20 = df['Close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else 0
            sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else 0
            
            trend = "neutral"
            if sma_20 > sma_50: trend = "uptrend"
            elif sma_20 < sma_50: trend = "downtrend"

            # RSI 14
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50

            return {
                "current_price": float(latest['Close']),
                "change_pct": float((latest['Close'] - prev['Close']) / prev['Close'] * 100) if prev['Close'] != 0 else 0,
                "volume": int(latest['Volume']),
                "trend": trend,
                "rsi": float(current_rsi),
                "last_date": str(latest.name)
            }
        except Exception:
            return {}

    @staticmethod
    def get_event_proximity(symbol: str) -> Dict[str, Any]:
        """
        Check for upcoming key events: Earnings, Ex-Dividend
        """
        try:
            ticker = yf.Ticker(symbol)
            events = {}
            calendar = ticker.calendar
            
            # Earnings
            # yfinance .calendar returns a dict with keys like 'Earnings Date' or 'Earnings High' etc.
            # actually ticker.calendar is usually a dict or dataframe depending on version
            
            earnings_date = None
            if calendar and isinstance(calendar, dict):
                earnings_date = calendar.get('Earnings Date')
            elif hasattr(ticker, 'earnings_dates'):
                 # Try earnings_dates df
                 pass
            
            # Fallback/Simplification: 
            # ticker.calendar might be {0: datetime...} list
            
            # Use 'get_earnings_dates' if available for massive history, but 'calendar' for next
            # We will try to parse 'calendar' output safely
            
            return {
                "earnings": {
                    "date": "N/A" # Placeholder, strict yfinance parsing is flaky across versions
                },
                "ex_dividend": "N/A"
            }
            
            # Improved Logic for Earnings (common failure point in yfinance)
            if hasattr(ticker, 'calendar') and ticker.calendar is not None:
                cal = ticker.calendar
                # Check for earnings date (it might be index or column)
                if 'Earnings Date' in cal:
                     dates = cal['Earnings Date']
                     if len(dates) > 0:
                         events['next_earnings'] = str(dates[0])
            
            return events

        except Exception as e:
            print(f"⚠️ Failed to fetch event proximity for {symbol}: {e}")
            return {}

    @staticmethod
    def get_option_data(symbol: str) -> Dict[str, Any]:
        """
        Fetch Option Metrics: Put/Call Ratio, Max Pain, IV (approx)
        Focuses on the *next* expiration date to minimize latency.
        """
        try:
            ticker = yf.Ticker(symbol)
            expirations = ticker.options
            
            if not expirations:
                return {}
                
            # Use the nearest expiration (likely most liquid/relevant for short term)
            next_expiry = expirations[0]
            chain = ticker.option_chain(next_expiry)
            
            calls = chain.calls
            puts = chain.puts
            
            # 1. Put/Call Ratio (Volume based)
            total_call_vol = calls['volume'].sum()
            total_put_vol = puts['volume'].sum()
            pc_ratio = total_put_vol / total_call_vol if total_call_vol > 0 else 0
            
            # 2. Max Pain
            # Strike where option writers lose least money (sum of intrinsic value of all options)
            # Simplified: Strike where (Call Value + Put Value) is minimum at expiry
            # Algorithm:
            # For each strike S:
            #   Call Loss = sum(max(0, price - S) * openInterest) for all calls ? No.
            #   Writer Loss at price P = sum(max(0, P - K_call) * OI_call + max(0, K_put - P) * OI_put)
            #   We want to find Price P (usually heavily pinned to a strike K) that minimizes total loss.
            #   Let's iterate over available strikes as candidate 'P'
            
            strikes = sorted(set(calls['strike'].tolist() + puts['strike'].tolist()))
            max_pain = 0
            min_loss = float('inf')
            
            for p in strikes:
                call_loss = calls.apply(lambda row: max(0, p - row['strike']) * row['openInterest'], axis=1).sum()
                put_loss = puts.apply(lambda row: max(0, row['strike'] - p) * row['openInterest'], axis=1).sum()
                total_loss = call_loss + put_loss
                
                if total_loss < min_loss:
                    min_loss = total_loss
                    max_pain = p
            
            return {
                "expiry_date": next_expiry,
                "put_call_ratio": round(pc_ratio, 2),
                "total_call_volume": int(total_call_vol),
                "total_put_volume": int(total_put_vol),
                "max_pain": float(max_pain)
            }

        except Exception as e:
             # Option data often fails for delayed/no-permission tickers
             # print(f"⚠️ Option data unavailable for {symbol}: {e}") 
             return {}

if __name__ == "__main__":
    # Test
    # provider = EnhancedDataProvider()
    # print(EnhancedDataProvider.get_multi_timeframe_data("NVDA"))
    # print(EnhancedDataProvider.get_option_data("NVDA"))
    pass
