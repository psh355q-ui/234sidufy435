"""
Analyst Agent for War Room Debate System

Role: Fundamental analysis specialist
Focuses on: Earnings, valuation (P/E), growth rate, financial health

Author: ai-trading-system
Date: 2025-12-21
"""

import logging
from typing import Dict, Any, Optional
import random

logger = logging.getLogger(__name__)


class AnalystAgent:
    """
    Analyst Agent - 펀더멘털 분석 전문가
    
    Core Capabilities:
    - Earnings analysis
    - Valuation metrics (P/E, P/B, P/S)
    - Growth rate assessment
    - Financial health check
    """
    
    def __init__(self):
        self.agent_name = "analyst"
        self.vote_weight = 0.15  # 15% voting weight
    
    async def analyze(self, ticker: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze ticker using fundamental metrics.
        
        Args:
            ticker: Stock ticker symbol
            context: Optional context (financial data, earnings, etc.)
        
        Returns:
            {
                "agent": "analyst",
                "action": "BUY|SELL|HOLD",
                "confidence": 0.0-1.0,
                "reasoning": str,
                "fundamental_factors": {...}
            }
        """
        try:
            logger.info(f"[Analyst Agent] Analyzing {ticker}")
            
            if context and "fundamental_data" in context:
                return await self._analyze_with_real_data(ticker, context["fundamental_data"])
            else:
                return await self._analyze_mock(ticker)
        
        except Exception as e:
            logger.error(f"[Analyst Agent] Error analyzing {ticker}: {e}")
            return self._fallback_response(ticker)
    
    async def _analyze_with_real_data(self, ticker: str, fundamental_data: Dict) -> Dict:
        """
        Analyze using real fundamental metrics.
        
        Expected fundamental_data format:
        {
            "pe_ratio": 25.5,
            "earnings_growth": 0.18,  # 18% YoY
            "revenue_growth": 0.12,
            "profit_margin": 0.22,
            "debt_to_equity": 0.45
        }
        """
        pe_ratio = fundamental_data.get("pe_ratio", 20)
        earnings_growth = fundamental_data.get("earnings_growth", 0.10)
        revenue_growth = fundamental_data.get("revenue_growth", 0.08)
        profit_margin = fundamental_data.get("profit_margin", 0.15)
        debt_to_equity = fundamental_data.get("debt_to_equity", 0.50)
        
        action = "HOLD"
        confidence = 0.5
        
        # BUY Signals - Strong fundamentals
        if earnings_growth > 0.15 and pe_ratio < 25 and profit_margin > 0.20:
            action = "BUY"
            confidence = 0.88
            reasoning = f"강한 펀더멘털 (실적 성장 {earnings_growth*100:.1f}%, P/E {pe_ratio:.1f}, 이익률 {profit_margin*100:.1f}%)"
        
        elif earnings_growth > 0.10 and debt_to_equity < 0.40:
            action = "BUY"
            confidence = 0.80
            reasoning = f"안정적 성장 (실적 +{earnings_growth*100:.1f}%, 낮은 부채비율 {debt_to_equity:.2f})"
        
        # SELL Signals - Weak fundamentals
        elif earnings_growth < -0.05 or profit_margin < 0.05:
            action = "SELL"
            confidence = 0.78
            reasoning = f"펀더멘털 악화 (실적 성장 {earnings_growth*100:+.1f}%, 이익률 {profit_margin*100:.1f}%)"
        
        elif pe_ratio > 40 and earnings_growth < 0.10:
            action = "SELL"
            confidence = 0.72
            reasoning = f"고평가 우려 (P/E {pe_ratio:.1f}, 성장률 {earnings_growth*100:.1f}% 불균형)"
        
        # HOLD - Mixed signals
        else:
            reasoning = f"중립 (P/E {pe_ratio:.1f}, 실적 성장 {earnings_growth*100:+.1f}%, 추가 분석 필요)"
            confidence = 0.65
        
        fundamental_factors = {
            "pe_ratio": pe_ratio,
            "earnings_growth": f"{earnings_growth*100:+.1f}%",
            "revenue_growth": f"{revenue_growth*100:+.1f}%",
            "profit_margin": f"{profit_margin*100:.1f}%",
            "debt_to_equity": debt_to_equity,
            "valuation": "UNDERVALUED" if pe_ratio < 20 else "OVERVALUED" if pe_ratio > 30 else "FAIR"
        }
        
        return {
            "agent": "analyst",
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "fundamental_factors": fundamental_factors
        }
    
    async def _analyze_mock(self, ticker: str) -> Dict:
        """Mock fundamental analysis"""
        scenarios = [
            {
                "action": "BUY",
                "confidence": 0.88,
                "reasoning": "실적 폭발적 성장 (+22% YoY), P/E 18로 저평가, 이익률 25%",
                "fundamental_factors": {
                    "pe_ratio": 18.5,
                    "earnings_growth": "+22%",
                    "valuation": "UNDERVALUED"
                }
            },
            {
                "action": "SELL",
                "confidence": 0.80,
                "reasoning": "실적 부진 (-8% YoY), P/E 45로 고평가, 부채비율 0.85",
                "fundamental_factors": {
                    "pe_ratio": 45.0,
                    "earnings_growth": "-8%",
                    "debt_to_equity": 0.85,
                    "valuation": "OVERVALUED"
                }
            },
            {
                "action": "HOLD",
                "confidence": 0.70,
                "reasoning": "혼조 (실적 +5%, P/E 28, 이익률 안정적)",
                "fundamental_factors": {
                    "pe_ratio": 28.0,
                    "earnings_growth": "+5%",
                    "valuation": "FAIR"
                }
            }
        ]
        
        return {
            "agent": "analyst",
            **random.choice(scenarios)
        }
    
    def _fallback_response(self, ticker: str) -> Dict:
        """Fallback on error"""
        return {
            "agent": "analyst",
            "action": "HOLD",
            "confidence": 0.55,
            "reasoning": f"펀더멘털 데이터 부족 - {ticker} 추가 조사 필요",
            "fundamental_factors": {
                "error": True
            }
        }
