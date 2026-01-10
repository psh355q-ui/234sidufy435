"""
Risk Agent MVP - Defense (35% weight)

Phase: MVP Consolidation
Date: 2025-12-31

Purpose:
    전문 리스크 관리자의 방어적 관점
    - 포지션 사이즈 결정 (NEW - ChatGPT 제안)
    - 리스크 평가 및 Stop Loss 설정
    - 감정/심리 분석 통합
    - 배당 리스크 평가

Key Responsibilities:
    1. 포지션 사이즈 계산 (Kelly Criterion + Risk-based)
    2. Stop Loss / Take Profit 설정
    3. 시장 감정 및 심리 분석
    4. 배당 일정 리스크 체크
    5. 최대 포지션 한도 검증

Absorbed Legacy Agents:
    - Risk Agent (100%)
    - Sentiment Agent (100%)
    - DividendRisk Agent (100%)
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai

from backend.ai.schemas.war_room_schemas import RiskOpinion


class RiskAgentMVP:
    """MVP Risk Agent - 방어적 리스크 관리 + Position Sizing"""

    def __init__(self):
        """Initialize Risk Agent MVP"""
        # Gemini API 설정
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Agent configuration
        self.weight = 0.35  # 35% voting weight
        self.role = "방어적 리스크 관리자"

        # Risk parameters (Hard Rules)
        self.ACCOUNT_RISK_PER_TRADE = 0.01  # 1% of account per trade
        self.MAX_POSITION_SIZE = 0.20  # 20% of portfolio max
        self.ABSOLUTE_MAX_POSITION = 0.30  # 30% hard cap (Hard Rule)
        self.MIN_CONFIDENCE_FOR_FULL_SIZE = 0.80  # 80% confidence required

        # System prompt
        self.system_prompt = """당신은 'War Room'의 방어적 리스크 관리자(Defensive Risk Manager)입니다. 수익 가능성은 Trader Agent가 볼 것입니다. 당신은 오직 **'이 거래가 어떻게 잘못될 수 있는가?'**에만 집중하십시오.

역할:
1. **모든 거래를 의심하십시오.** Trader가 "대박 기회"라고 해도, 당신은 그 이면의 함정을 찾아야 합니다.
2. **"최악의 시나리오(Worst Case)"를 항상 가정하십시오.** (예: 어닝 쇼크, 전쟁 발발, 금리 급등)
3. 단순한 변동성이 아니라, **'상관관계 리스크(Correlation Trap)'**를 경고하십시오. (예: "기술주 전체가 무너지면 얘도 못 버팁니다")
4. 당신의 승인은 "안전하다"는 뜻이 아니라, **"손실이 감내 가능하다(Calculated Risk)"**는 뜻이어야 합니다.

분석 원칙:
- **Capital Preservation First**: 원금 보존이 최우선입니다.
- **Paranoid Mode**: 낙관 편향을 제거하고 철저히 비관적으로 보십시오.
- **Hard Numbers**: "위험해 보인다" 대신, "하락 시 -15% 손실 예상"처럼 숫자로 말하십시오.

출력 형식 (JSON):
{
    "risk_level": "low" | "medium" | "high" | "extreme",
    "confidence": 0.0 ~ 1.0,
    "reasoning": "리스크 관점의 거부/축소 사유 (3줄 요약)",
    "stop_loss_pct": 손실 한도 (예: 0.02 = 2%),
    "take_profit_pct": 목표 수익 (예: 0.10 = 10%),
    "max_position_pct": 최대 포지션 비율 추천 (예: 0.15 = 15%),
    "sentiment_score": -1.0 ~ 1.0 (부정 ~ 긍정),
    "volatility_risk": 0.0 ~ 10.0,
    "dividend_risk": "none" | "ex-dividend-near" | "cut-risk",
    "fear_greed_index": 0 ~ 100 (공포 ~ 탐욕),
    "recommendation": "approve" | "reduce_size" | "reject",
    "position_sizing": {"recommended_pct": 3.5, "reason": "높은 베타 고려"},
    "var_95": -8.2,
    "beta": 2.0,
    "max_loss_scenario": {"event": "정책 변화", "loss_pct": -15},
    "risk_decomposition": {
        "structural": "추세 붕괴 위험",
        "event": "트럼프 취임",
        "sentiment": "과매도"
    }
}

중요:
- **Trader Agent의 낙관론에 휘둘리지 마십시오.**
- risk_level이 "extreme"이면 recommendation은 무조건 "reject"입니다.
- **반드시 한글로 응답할 것.**
"""

    def analyze(
        self,
        symbol: str,
        price_data: Dict[str, Any],
        trader_opinion: Optional[Dict[str, Any]] = None,
        market_conditions: Optional[Dict[str, Any]] = None,
        dividend_info: Optional[str] = None,
        portfolio_state: Optional[Dict[str, Any]] = None,
        option_data: Optional[Dict[str, Any]] = None # [Phase 3]
    ) -> Dict[str, Any]:
        """
        리스크 분석 및 포지션 사이즈 계산
        
        Returns:
            Dict (compatible with RiskOpinion model)
        """
        # Construct analysis prompt
        prompt = self._build_prompt(
            symbol=symbol,
            price_data=price_data,
            trader_opinion=trader_opinion,
            market_conditions=market_conditions,
            dividend_info=dividend_info,
            portfolio_state=portfolio_state,
            option_data=option_data
        )
        try:
            response = self.model.generate_content([
                self.system_prompt,
                prompt
            ])

            # Parse response (Initial dict parsing)
            result_dict = self._parse_json_response(response.text)

            # Calculate position size (code-based, not AI)
            position_size_pct = 0.0
            kelly_breakdown = {}
            
            if portfolio_state and trader_opinion:
                position_sizing = self._calculate_position_size(
                    stop_loss_pct=result_dict.get('stop_loss_pct', 0.02),
                    confidence=trader_opinion.get('confidence', 0.5),
                    portfolio_context=portfolio_state,
                    current_price=price_data['current_price'],
                    risk_level=result_dict.get('risk_level', 'medium')
                )
                result_dict.update(position_sizing)
                position_size_pct = position_sizing.get('position_size_pct', 0.0)
                kelly_breakdown = position_sizing.get('position_sizing_breakdown', {})

            # Map fields for Schema
            current_price = price_data.get('current_price', 0)
            stop_loss_pct = result_dict.get('stop_loss_pct', 0.02)
            
            # Action Mapping
            recommendation = result_dict.get('recommendation', 'reduce_size')
            action_map = {
                'approve': 'approve',
                'reduce_size': 'reduce_size',
                'reject': 'reject'
            }
            action = action_map.get(recommendation, 'reduce_size')

            # Calculate Stop Loss Price if missing
            stop_loss_price = current_price * (1 - stop_loss_pct)

            # Construct RiskOpinion for validation
            risk_opinion_data = {
                'agent': 'risk_mvp',
                'action': action,
                'confidence': result_dict.get('confidence', 0.5),
                'position_size': position_size_pct * 100, # % value (0-100)
                'risk_level': result_dict.get('risk_level', 'medium'),
                'stop_loss': stop_loss_price,
                'stop_loss_pct': stop_loss_pct,
                'take_profit_pct': result_dict.get('take_profit_pct'),
                'reasoning': result_dict.get('reasoning', 'No reasoning'),
                'sentiment_score': result_dict.get('sentiment_score'),
                'volatility_risk': result_dict.get('volatility_risk'),
                'dividend_risk': result_dict.get('dividend_risk'),
                'kelly_calculation': kelly_breakdown,
                'position_sizing_recommendation': result_dict.get('position_sizing'),
                'var_95': result_dict.get('var_95'),
                'beta': result_dict.get('beta'),
                'max_loss_scenario': result_dict.get('max_loss_scenario'),
                'risk_decomposition': result_dict.get('risk_decomposition'),
                'warnings': []
            }
            
            # Validate with Pydantic
            opinion = RiskOpinion(**risk_opinion_data)
            
            # Convert back to dict for compatibility
            result = opinion.model_dump()
            
            # Add extra fields expected by War Room
            result.update(result_dict) # Keep original fields like position_size_usd
            result['weight'] = self.weight
            result['timestamp'] = datetime.utcnow().isoformat()
            result['symbol'] = symbol

            return result

        except Exception as e:
            # Error handling - return safe default (reject)
            return {
                'agent': 'risk_mvp',
                'risk_level': 'extreme',
                'confidence': 0.0,
                'reasoning': f'분석 실패: {str(e)}',
                'stop_loss_pct': 0.02,
                'take_profit_pct': 0.10,
                'max_position_pct': 0.0,
                'position_size_usd': 0.0,
                'position_size_shares': 0,
                'sentiment_score': 0.0,
                'volatility_risk': 10.0,
                'dividend_risk': 'none',
                'recommendation': 'reject',
                'weight': self.weight,
                'timestamp': datetime.utcnow().isoformat(),
                'symbol': symbol,
                'error': str(e)
            }

    # ... _build_prompt kept ...

    def _build_prompt(
        self,
        symbol: str,
        price_data: Dict[str, Any],
        trader_opinion: Optional[Dict[str, Any]] = None,
        market_conditions: Optional[Dict[str, Any]] = None,
        dividend_info: Optional[str] = None,
        portfolio_state: Optional[Dict[str, Any]] = None,
        option_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construct risk analysis prompt"""
        prompt_parts = [f"Analyze risk for {symbol} based on the following data:\n"]

        # 1. Price Volatility
        prompt_parts.append("1. Price & Volatility:")
        prompt_parts.append(f"- Current Price: {price_data.get('current_price')}")
        prompt_parts.append(f"- 52W High: {price_data.get('high_52w')}")
        prompt_parts.append(f"- 52W Low: {price_data.get('low_52w')}")
        prompt_parts.append(f"- Volatility: {price_data.get('volatility', 'Unknown')}\n")

        # 2. Trader Opinion (Attack view)
        prompt_parts.append("2. Trader Opinion (Attack View):")
        if trader_opinion:
            prompt_parts.append(f"- Action: {trader_opinion.get('action')}")
            prompt_parts.append(f"- Confidence: {trader_opinion.get('confidence')}")
            prompt_parts.append(f"- Reasoning: {trader_opinion.get('reasoning')}")
        else:
            prompt_parts.append("No trader opinion available.")
        prompt_parts.append("\n")

        # 3. Market Sentiment
        prompt_parts.append("3. Market Conditions:")
        if market_conditions:
            sentiment = market_conditions.get('market_sentiment', 'Neutral')
            vix = market_conditions.get('vix', 'Unknown')
            prompt_parts.append(f"- Market Sentiment: {sentiment}")
            prompt_parts.append(f"- VIX: {vix}")
        else:
             prompt_parts.append("No market data.")
        prompt_parts.append("\n")
        
        # 4. Dividend Info
        prompt_parts.append("4. Dividend Information:")
        if dividend_info:
            prompt_parts.append(f"배당 정보: {dividend_info}")
        else:
            prompt_parts.append("No dividend info.")
        prompt_parts.append("\n")

        # [Phase 3] Option Data Volatility Check
        if option_data:
            prompt_parts.append("\n옵션 내재변동성(IV) 및 리스크:")
            prompt_parts.append(f"- Put/Call Ratio: {option_data.get('put_call_ratio', 'N/A')}")
            prompt_parts.append(f"- Max Pain Price: ${option_data.get('max_pain', 'N/A')}")
            current_price = price_data.get('current_price', 0)
            max_pain = float(option_data.get('max_pain', 0))
            if max_pain > 0 and current_price > 0:
                deviation = (current_price - max_pain) / current_price * 100
                prompt_parts.append(f"- Current vs Max Pain: {deviation:+.2f}% (Deviation)")
            prompt_parts.append("\n")

        prompt_parts.append("위 정보를 바탕으로 리스크를 분석하고 JSON 형식으로 답변하세요.")
            
        return "\n".join(prompt_parts)

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Deprecated: Use _parse_json_response and Pydantic validation in analyze"""
        return self._parse_json_response(response_text)

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from response text"""
        import json
        import re

        # Extract JSON from response
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                else:
                    raise ValueError("No valid JSON found in response")

        # Basic validation of required fields for dict
        required_fields = ['risk_level', 'confidence', 'reasoning']
        for field in required_fields:
            if field not in result:
                # Provide minimal defaults for resilience
                if field == 'risk_level': result[field] = 'medium'
                if field == 'confidence': result[field] = 0.5
                if field == 'reasoning': result[field] = 'Default reasoning'
        
        return result

    def _calculate_position_size(
        self,
        stop_loss_pct: float,
        confidence: float,
        portfolio_context: Dict[str, Any],
        current_price: float,
        risk_level: str
    ) -> Dict[str, Any]:
        """
        Calculate position size using Kelly Criterion + Risk-based approach

        Formula:
        1. Base Size = (Account Risk % / Stop Loss %) * Account Value
        2. Confidence Adjustment = Base Size * Confidence
        3. Risk Level Adjustment = Adjusted Size * Risk Multiplier
        4. Hard Cap = min(Final Size, ABSOLUTE_MAX_POSITION)

        Args:
            stop_loss_pct: Stop loss percentage (e.g., 0.02 = 2%)
            confidence: Trader confidence (0.0 ~ 1.0)
            portfolio_context: Portfolio information
            current_price: Current stock price
            risk_level: low/medium/high/extreme

        Returns:
            Dict with position_size_usd, position_size_shares, position_size_pct
        """
        total_value = portfolio_context.get('total_value', 100000)  # Default $100k
        current_cash = portfolio_context.get('current_cash', total_value)

        # Step 1: Base position size (Kelly-like)
        base_size_pct = self.ACCOUNT_RISK_PER_TRADE / max(stop_loss_pct, 0.01)
        base_size_usd = total_value * base_size_pct

        # Step 2: Confidence adjustment
        confidence_adjusted_usd = base_size_usd * confidence

        # Step 3: Risk level adjustment
        risk_multipliers = {
            'low': 1.0,
            'medium': 0.7,
            'high': 0.4,
            'extreme': 0.0  # No position on extreme risk
        }
        risk_multiplier = risk_multipliers.get(risk_level, 0.5)
        risk_adjusted_usd = confidence_adjusted_usd * risk_multiplier

        # Step 4: Apply hard caps
        risk_adjusted_pct = risk_adjusted_usd / total_value
        final_pct = min(risk_adjusted_pct, self.MAX_POSITION_SIZE, self.ABSOLUTE_MAX_POSITION)
        final_usd = total_value * final_pct

        # Step 5: Check available cash
        final_usd = min(final_usd, current_cash)

        # Step 6: Calculate shares
        shares = int(final_usd / current_price) if current_price > 0 else 0
        actual_usd = shares * current_price

        return {
            'position_size_usd': round(actual_usd, 2),
            'position_size_shares': shares,
            'position_size_pct': round(actual_usd / total_value, 4),
            'position_sizing_breakdown': {
                'base_size_usd': round(base_size_usd, 2),
                'confidence_adjusted_usd': round(confidence_adjusted_usd, 2),
                'risk_adjusted_usd': round(risk_adjusted_usd, 2),
                'final_usd': round(actual_usd, 2),
                'risk_multiplier': risk_multiplier,
                'hard_cap_applied': final_pct >= self.ABSOLUTE_MAX_POSITION
            }
        }

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            'name': 'RiskAgentMVP',
            'role': self.role,
            'weight': self.weight,
            'focus': '방어적 리스크 관리 + Position Sizing',
            'absorbed_agents': ['Risk Agent', 'Sentiment Agent', 'DividendRisk Agent'],
            'responsibilities': [
                '포지션 사이즈 계산 (Kelly + Risk-based)',
                'Stop Loss / Take Profit 설정',
                '시장 감정 및 심리 분석',
                '배당 일정 리스크 체크',
                '최대 포지션 한도 검증'
            ],
            'hard_rules': {
                'account_risk_per_trade': f'{self.ACCOUNT_RISK_PER_TRADE * 100}%',
                'max_position_size': f'{self.MAX_POSITION_SIZE * 100}%',
                'absolute_max_position': f'{self.ABSOLUTE_MAX_POSITION * 100}%',
                'min_confidence_for_full_size': f'{self.MIN_CONFIDENCE_FOR_FULL_SIZE * 100}%'
            }
        }


# Example usage
if __name__ == "__main__":
    agent = RiskAgentMVP()

    # Test data
    price_data = {
        'current_price': 150.25,
        'high_52w': 180.00,
        'low_52w': 120.00,
        'volatility': 0.25
    }

    trader_opinion = {
        'action': 'buy',
        'confidence': 0.75,
        'opportunity_score': 7.5
    }

    portfolio_context = {
        'current_cash': 50000,
        'total_value': 100000,
        'current_positions': 3
    }

    result = agent.analyze(
        symbol='AAPL',
        price_data=price_data,
        trader_opinion=trader_opinion,
        portfolio_context=portfolio_context
    )

    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Position Size: ${result.get('position_size_usd', 0):,.2f} ({result.get('position_size_shares', 0)} shares)")
    print(f"Stop Loss: {(result['stop_loss_pct'] * 100):.1f}%")
    print(f"Reasoning: {result['reasoning']}")
