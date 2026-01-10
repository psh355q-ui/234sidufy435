"""
Sector Rotation Analyzer
- Analyzes sector performance using Sector SPDR ETFs
- Identifies leading/lagging sectors and rotation trends
"""
import logging
from typing import List, Dict, Any
import yfinance as yf
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SectorRotationAnalyzer:
    def __init__(self):
        self.sector_etfs = {
            "XLK": "Technology",
            "XLF": "Financials",
            "XLV": "Health Care",
            "XLY": "Consumer Discretionary",
            "XLP": "Consumer Staples",
            "XLE": "Energy",
            "XLI": "Industrials",
            "XLC": "Comm. Services",
            "XLB": "Materials",
            "XLU": "Utilities",
            "XLRE": "Real Estate"
        }

    async def analyze_sectors(self, period="5d") -> Dict[str, Any]:
        """
        Analyze sector performance over a given period.
        """
        results = []
        tickers = list(self.sector_etfs.keys())
        
        try:
            logger.info(f"Analyzing sector rotation for {len(tickers)} sectors...")
            
            # Batch fetch
            data = yf.download(tickers, period=period, progress=False)['Close']
            
            if data.empty:
                logger.warning("No sector data fetched")
                return {}

            # Calculate returns: (Last Price - First Price) / First Price
            for ticker in tickers:
                try:
                    if ticker not in data.columns:
                        continue
                        
                    series = data[ticker].dropna()
                    if len(series) < 2:
                        continue
                        
                    start_price = series.iloc[0]
                    end_price = series.iloc[-1]
                    
                    return_pct = ((end_price - start_price) / start_price) * 100
                    
                    results.append({
                        "ticker": ticker,
                        "name": self.sector_etfs[ticker],
                        "return_pct": round(return_pct, 2),
                        "current_price": round(end_price, 2)
                    })
                except Exception as e:
                    logger.debug(f"Error analyzing {ticker}: {e}")

        except Exception as e:
            logger.error(f"Sector analysis failed: {e}")
            return {}
            
        # Sort by return
        results.sort(key=lambda x: x['return_pct'], reverse=True)
        
        # Categorize
        leading = results[:3]
        lagging = results[-3:]
        
        return {
            "period": period,
            "all_sectors": results,
            "leading_sectors": leading,
            "lagging_sectors": lagging,
            "rotation_insight": self._generate_insight(leading, lagging)
        }

    def _generate_insight(self, leading, lagging) -> str:
        """Generate simple text insight based on leaders (Korean)"""
        if not leading:
            return "섹터 데이터가 부족합니다."
            
        leader_names = [s['name'] for s in leading]
        
        insight = f"주도 섹터: {', '.join(leader_names)}. "
        
        # Simple heuristic
        if "Technology" in leader_names or "Consumer Discretionary" in leader_names:
            insight += "기술주 및 소비재 중심의 위험자산 선호(Risk-On) 심리가 강합니다."
        elif "Utilities" in leader_names or "Consumer Staples" in leader_names:
            insight += "경기 방어주 강세로 시장의 불확실성/Risk-Off 심리가 관찰됩니다."
        elif "Energy" in leader_names or "Materials" in leader_names:
            insight += "인플레이션 헤지 또는 원자재 관련 사이클이 부각되고 있습니다."
        else:
            insight += "뚜렷한 방향성보다는 순환매 장세가 나타나고 있습니다."
            
        return insight
