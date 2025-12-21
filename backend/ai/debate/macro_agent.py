"""
Macro Agent for War Room Debate System

Role: Macroeconomic analysis specialist
Focuses on: Interest rates, inflation, GDP, employment, market regime

Author: ai-trading-system
Date: 2025-12-21
"""

import logging
from typing import Dict, Any, Optional
import random

logger = logging.getLogger(__name__)


class MacroAgent:
    """
    Macro Agent - 거시경제 분석 전문가
    
    Core Capabilities:
    - Interest rate analysis (Fed policy)
    - Inflation monitoring (CPI, PPI)
    - GDP growth assessment
    - Employment data analysis
    - Market regime classification
    """
    
    def __init__(self):
        self.agent_name = "macro"
        self.vote_weight = 0.10  # 10% voting weight
    
    async def analyze(self, ticker: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze macro environment impact on ticker.
        
        Args:
            ticker: Stock ticker symbol
            context: Optional context (macro indicators, sector data)
        
        Returns:
            {
                "agent": "macro",
                "action": "BUY|SELL|HOLD",
                "confidence": 0.0-1.0,
                "reasoning": str,
                "macro_factors": {...}
            }
        """
        try:
            logger.info(f"[Macro Agent] Analyzing {ticker}")
            
            if context and "macro_data" in context:
                return await self._analyze_with_real_data(ticker, context["macro_data"])
            else:
                return await self._analyze_mock(ticker)
        
        except Exception as e:
            logger.error(f"[Macro Agent] Error analyzing {ticker}: {e}")
            return self._fallback_response(ticker)
    
    async def _analyze_with_real_data(self, ticker: str, macro_data: Dict) -> Dict:
        """
        Analyze using real macro indicators.
        
        Expected macro_data format:
        {
            "fed_rate": 5.25,  # %
            "fed_direction": "HIKING|CUTTING|HOLDING",
            "cpi_yoy": 3.2,  # %
            "gdp_growth": 2.5,  # %
            "unemployment": 3.7,  # %
            "market_regime": "RISK_ON|RISK_OFF|NEUTRAL"
        }
        """
        fed_rate = macro_data.get("fed_rate", 5.0)
        fed_direction = macro_data.get("fed_direction", "HOLDING")
        cpi_yoy = macro_data.get("cpi_yoy", 3.0)
        gdp_growth = macro_data.get("gdp_growth", 2.0)
        unemployment = macro_data.get("unemployment", 4.0)
        market_regime = macro_data.get("market_regime", "NEUTRAL")
        
        action = "HOLD"
        confidence = 0.5
        
        # RISK-ON Environment (favorable for stocks)
        if fed_direction == "CUTTING" and cpi_yoy < 3.0:
            action = "BUY"
            confidence = 0.84
            reasoning = f"금리 인하 사이클 + 인플레 진정 (CPI {cpi_yoy:.1f}%) - Risk ON 국면"
        
        elif gdp_growth > 2.5 and unemployment < 4.0 and cpi_yoy < 3.5:
            action = "BUY"
            confidence = 0.78
            reasoning = f"골디락스 환경 (GDP +{gdp_growth:.1f}%, 실업률 {unemployment:.1f}%, 인플레 안정)"
        
        # RISK-OFF Environment (unfavorable)
        elif fed_direction == "HIKING" and cpi_yoy > 4.5:
            action = "SELL"
            confidence = 0.76
            reasoning = f"긴축 사이클 + 고인플레 (CPI {cpi_yoy:.1f}%) - Risk OFF 국면"
        
        elif gdp_growth < 1.0 or unemployment > 5.0:
            action = "SELL"
            confidence = 0.72
            reasoning = f"경기 둔화 우려 (GDP {gdp_growth:.1f}%, 실업률 {unemployment:.1f}%)"
        
        # NEUTRAL
        else:
            reasoning = f"혼조 (Fed {fed_direction}, GDP {gdp_growth:.1f}%, CPI {cpi_yoy:.1f}%)"
            confidence = 0.65
        
        macro_factors = {
            "fed_rate": f"{fed_rate:.2f}%",
            "fed_direction": fed_direction,
            "cpi_yoy": f"{cpi_yoy:.1f}%",
            "gdp_growth": f"{gdp_growth:.1f}%",
            "unemployment": f"{unemployment:.1f}%",
            "market_regime": market_regime
        }
        
        return {
            "agent": "macro",
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "macro_factors": macro_factors
        }
    
    async def _analyze_mock(self, ticker: str) -> Dict:
        """Mock macro analysis"""
        scenarios = [
            {
                "action": "BUY",
                "confidence": 0.84,
                "reasoning": "Fed 금리 인하 사이클 시작, CPI 2.8%로 목표치 근접 - Risk ON",
                "macro_factors": {
                    "fed_direction": "CUTTING",
                    "cpi_yoy": "2.8%",
                    "market_regime": "RISK_ON"
                }
            },
            {
                "action": "SELL",
                "confidence": 0.74,
                "reasoning": "Fed 매파적 스탠스 유지, CPI 5.2% 고착화 - Risk OFF",
                "macro_factors": {
                    "fed_direction": "HIKING",
                    "cpi_yoy": "5.2%",
                    "market_regime": "RISK_OFF"
                }
            },
            {
                "action": "HOLD",
                "confidence": 0.68,
                "reasoning": "혼조 (Fed 동결, GDP 성장 완만, 인플레 소폭 하락)",
                "macro_factors": {
                    "fed_direction": "HOLDING",
                    "gdp_growth": "1.8%",
                    "market_regime": "NEUTRAL"
                }
            }
        ]
        
        return {
            "agent": "macro",
            **random.choice(scenarios)
        }
    
    def _fallback_response(self, ticker: str) -> Dict:
        """Fallback on error"""
        return {
            "agent": "macro",
            "action": "HOLD",
            "confidence": 0.60,
            "reasoning": f"거시경제 데이터 부족 - {ticker} 매크로 환경 불확실",
            "macro_factors": {
                "error": True
            }
        }
