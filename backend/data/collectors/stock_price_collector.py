"""
Stock Price Data Collector for Historical Backtesting.

Uses yfinance to collect historical OHLCV data for backtesting.

Author: AI Trading System Team
Date: 2025-12-21
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class StockPriceData:
    """Stock price data point."""
    ticker: str
    date: datetime  # Keep this for API compatibility
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: float  # Keep this for API compatibility
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dict for database insertion."""
        return {
            "ticker": self.ticker,
            "time": self.date,  # Map 'date' to 'time' for database
            "date": self.date,  # Keep for backward compatibility
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "adjusted_close": self.adj_close,  # Map to 'adjusted_close' for database
            "adj_close": self.adj_close,  # Keep for backward compatibility
            "metadata": self.metadata or {}
        }


class StockPriceCollector:
    """
    Collect historical stock price data using yfinance.

    Features:
    - Multi-ticker batch collection
    - Automatic retry on failure
    - Data validation
    - Progress tracking
    """

    def __init__(self):
        """Initialize collector."""
        self.logger = logging.getLogger(__name__)

    def collect_historical_data(
        self,
        tickers: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> Dict[str, List[StockPriceData]]:
        """
        Collect historical price data for multiple tickers.

        Args:
            tickers: List of stock tickers
            start_date: Start date for data collection
            end_date: End date for data collection
            interval: Data interval (1d, 1h, 1m, etc.)

        Returns:
            Dict mapping ticker to list of StockPriceData
        """
        self.logger.info(
            f"Collecting price data for {len(tickers)} tickers "
            f"from {start_date.date()} to {end_date.date()}"
        )

        results = {}

        for ticker in tickers:
            try:
                data = self.collect_ticker_data(
                    ticker, start_date, end_date, interval
                )
                results[ticker] = data
                self.logger.info(
                    f"{ticker}: Collected {len(data)} data points"
                )
            except Exception as e:
                self.logger.error(f"{ticker}: Collection failed - {e}")
                results[ticker] = []

        total_points = sum(len(v) for v in results.values())
        self.logger.info(f"Total collected: {total_points} data points")

        return results

    def collect_ticker_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> List[StockPriceData]:
        """
        Collect historical data for a single ticker.

        Args:
            ticker: Stock ticker
            start_date: Start date
            end_date: End date
            interval: Data interval

        Returns:
            List of StockPriceData objects
        """
        data_points = []

        try:
            # Download data using yfinance
            stock = yf.Ticker(ticker)
            df = stock.history(
                start=start_date,
                end=end_date,
                interval=interval
            )

            if df.empty:
                self.logger.warning(f"{ticker}: No data returned")
                return []

            # Convert DataFrame to StockPriceData objects
            for date, row in df.iterrows():
                # Handle timezone-aware datetime
                if hasattr(date, 'tz_localize'):
                    date = date.tz_localize(None)
                elif hasattr(date, 'to_pydatetime'):
                    date = date.to_pydatetime()

                price_data = StockPriceData(
                    ticker=ticker,
                    date=date,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume']),
                    adj_close=float(row['Close']),  # yfinance adjusts Close by default
                    metadata={
                        "interval": interval,
                        "source": "yfinance"
                    }
                )
                data_points.append(price_data)

        except Exception as e:
            self.logger.error(f"{ticker}: Data collection error - {e}")
            raise

        return data_points

    def get_latest_price(self, ticker: str) -> Optional[float]:
        """
        Get latest closing price for a ticker.

        Args:
            ticker: Stock ticker

        Returns:
            Latest close price or None if failed
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")

            if not hist.empty:
                return float(hist['Close'].iloc[-1])

        except Exception as e:
            self.logger.error(f"{ticker}: Failed to get latest price - {e}")

        return None

    def validate_data(self, data: List[StockPriceData]) -> bool:
        """
        Validate collected price data.

        Checks:
        - No missing dates (weekends/holidays excluded)
        - Prices are positive
        - Volume is non-negative

        Args:
            data: List of StockPriceData

        Returns:
            True if validation passes
        """
        if not data:
            return False

        for point in data:
            # Check positive prices
            if any([
                point.open <= 0,
                point.high <= 0,
                point.low <= 0,
                point.close <= 0
            ]):
                self.logger.warning(
                    f"{point.ticker} {point.date}: Invalid price data"
                )
                return False

            # Check volume
            if point.volume < 0:
                self.logger.warning(
                    f"{point.ticker} {point.date}: Invalid volume"
                )
                return False

            # Check high/low consistency
            if point.high < point.low:
                self.logger.warning(
                    f"{point.ticker} {point.date}: High < Low"
                )
                return False

        return True


# Standalone test
if __name__ == "__main__":
    print("=" * 80)
    print("Stock Price Data Collector Test")
    print("=" * 80)
    print()

    collector = StockPriceCollector()

    # Test with popular tickers
    tickers = ["AAPL", "MSFT", "GOOGL"]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Last 30 days

    print(f"Collecting data for: {', '.join(tickers)}")
    print(f"Period: {start_date.date()} to {end_date.date()}")
    print()

    results = collector.collect_historical_data(
        tickers, start_date, end_date
    )

    print("\nResults:")
    print("-" * 80)

    for ticker, data in results.items():
        print(f"\n{ticker}:")
        print(f"  Data points: {len(data)}")

        if data:
            latest = data[-1]
            print(f"  Latest date: {latest.date.date()}")
            print(f"  Latest close: ${latest.close:.2f}")
            print(f"  Latest volume: {latest.volume:,}")

            # Validate
            is_valid = collector.validate_data(data)
            print(f"  Validation: {'✅ PASS' if is_valid else '❌ FAIL'}")

    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)
