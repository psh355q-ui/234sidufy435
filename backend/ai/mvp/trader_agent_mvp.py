"""
Trader Agent MVP - Attack (35% weight)

Phase: MVP Consolidation
Date: 2025-12-31

Purpose:
    전문 트레이더의 공격적 관점
    - 단기 기회 포착 (Trader Agent 흡수)
    - 칩워 관련 기회 포착 (ChipWar Agent 일부 흡수)
    - 진입/청산 타이밍 제안

Key Responsibilities:
    1. 단기 트레이딩 기회 식별
    2. 기술적 진입/청산 시그널 생성
    3. 칩워 관련 단기 기회 포착
    4. 모멘텀 및 트렌드 분석

Absorbed Legacy Agents:
    - Trader Agent (100%)
    - ChipWar Agent (기회 포착 부분만)
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai

from backend.ai.schemas.war_room_schemas import TraderOpinion


class TraderAgentMVP:
    """MVP Trader Agent - 공격적 트레이딩 기회 포착"""

    def __init__(self):
        """Initialize Trader Agent MVP"""
        # Gemini API 설정
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Agent configuration
        self.weight = 0.35  # 35% voting weight
        self.role = "공격적 트레이더"

        # System prompt
        self.system_prompt = """당신은 'War Room'의 공격적 트레이더(Aggressive Trader)입니다. 리스크 관리나 방어적인 태도는 Risk Agent의 몫입니다. 당신의 유일한 목표는 **'수익 기회 포착'**입니다.

역할:
1. **돈이 되는 자리(Setup)만 찾으십시오.** (애매하면 'pass')
2. "지지선 근처입니다" 같은 뻔한 말 대신, **"지금 진입하면 손익비 1:3 나오는 자리"**인지 분석하십시오.
3. 기술적 지표를 단순 나열하지 말고, **시장 심리와 모멘텀(추세 강도)**을 읽어내십시오.
4. 칩워/뉴스 호재가 터졌을 때 즉각적인 가격 반응을 예측하십시오.

분석 원칙:
- **Aggressive & Sharp**: 말투는 간결하고 확신에 차야 합니다.
- **Setup Is King**: 단순한 상승 추세가 아니라, 구체적인 '진입 트리거'가 보여야 합니다.
- **Ignore Macro Noise**: 거시경제 걱정은 Analyst가 합니다. 당신은 지금 차트와 수급, 호재에만 집중하십시오.

출력 형식 (JSON):
{
    "action": "buy" | "sell" | "hold" | "pass",
    "confidence": 0.0 ~ 1.0, (확신 없으면 과감히 0점대 부여)
    "reasoning": "핵심 진입 근거 3줄 요약 (기술적 셋업 + 모멘텀)",
    "entry_price": 목표 진입가 (현재가 근처 or 돌파 매수),
    "exit_price": 1차 목표가 (저항선 or 피보나치),
    "stop_loss": **기술적 무효화 지점** (손절가),
    "risk_reward_ratio": 손익비 (예: 3.5),
    "support_levels": [390, 380, 350],
    "resistance_levels": [420, 445, 480],
    "volume_reader": "거래량 분석 (예: '매집봉 출현', '하락 다이버전스')",
    "setup_quality": "High" | "Medium" | "Low",
    "momentum_strength": "weak" | "moderate" | "strong" (강한 모멘텀 선호)
}

중요:
- **Risk Agent와 겹치는 분석("변동성이 크니 주의하세요" 등)은 절대 금지.**
- 당신은 엑셀러레이터를 밟는 역할입니다. 브레이크는 Risk Agent가 밟습니다.
- **반드시 한글로 응답할 것.**
"""

    def analyze(
        self,
        symbol: str,
        price_data: Dict[str, Any],
        technical_data: Optional[Dict[str, Any]] = None,
        chipwar_events: Optional[list] = None,
        market_context: Optional[Dict[str, Any]] = None,
        multi_timeframe_data: Optional[Dict[str, Any]] = None, # [Phase 3]
        option_data: Optional[Dict[str, Any]] = None           # [Phase 3]
    ) -> Dict[str, Any]:
        """
        트레이딩 기회 분석
        
        Returns:
            Dict (compatible with TraderOpinion model)
        """
        # Construct analysis prompt
        prompt = self._build_prompt(
            symbol=symbol,
            price_data=price_data,
            technical_data=technical_data,
            chipwar_events=chipwar_events,

            market_context=market_context,
            multi_timeframe_data=multi_timeframe_data,
            option_data=option_data
        )

        # Call Gemini API
        try:
            response = self.model.generate_content([
                self.system_prompt,
                prompt
            ])

            # Parse and Validate with Pydantic
            # _parse_response now returns TraderOpinion object
            opinion = self._parse_response(response.text)

            # Convert to dict for compatibility
            result = opinion.model_dump()

            # Add metadata (that are not in schema or overwrite defaults)
            result['weight'] = self.weight
            result['timestamp'] = datetime.utcnow().isoformat()
            result['symbol'] = symbol

            return result

        except Exception as e:
            # Error handling - return safe default
            return {
                'agent': 'trader_mvp',
                'action': 'pass',
                'confidence': 0.0,
                'reasoning': f'분석 실패: {str(e)}',
                'opportunity_score': 0.0,
                'momentum_strength': 'weak',
                'weight': self.weight,
                'timestamp': datetime.utcnow().isoformat(),
                'symbol': symbol,
                'error': str(e)
            }

    def _build_prompt(
        self,
        symbol: str,
        price_data: Dict[str, Any],
        technical_data: Optional[Dict[str, Any]],
        chipwar_events: Optional[list],
        market_context: Optional[Dict[str, Any]],
        multi_timeframe_data: Optional[Dict[str, Any]] = None,
        option_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build analysis prompt"""
        prompt_parts = [
            f"종목: {symbol}",
            f"현재가: ${price_data.get('current_price', 'N/A')}",
            f"시가: ${price_data.get('open', 'N/A')}",
            f"고가: ${price_data.get('high', 'N/A')}",
            f"저가: ${price_data.get('low', 'N/A')}",
            f"거래량: {price_data.get('volume', 0):,}" if isinstance(price_data.get('volume'), (int, float)) else f"거래량: {price_data.get('volume', 'N/A')}",
        ]

        # Technical indicators
        if technical_data:
            prompt_parts.append("\n기술적 지표:")
            if 'rsi' in technical_data:
                prompt_parts.append(f"- RSI: {technical_data['rsi']:.2f}")
            if 'macd' in technical_data:
                macd = technical_data['macd']
                prompt_parts.append(f"- MACD: {macd.get('value', 0):.2f} (Signal: {macd.get('signal', 0):.2f})")
            if 'moving_averages' in technical_data:
                ma = technical_data['moving_averages']
                prompt_parts.append(f"- MA50: ${ma.get('ma50', 0):.2f}, MA200: ${ma.get('ma200', 0):.2f}")
            if 'bollinger_bands' in technical_data:
                bb = technical_data['bollinger_bands']
                prompt_parts.append(f"- Bollinger Bands: Upper ${bb.get('upper', 0):.2f}, Lower ${bb.get('lower', 0):.2f}")

        # ChipWar events
        if chipwar_events and len(chipwar_events) > 0:
            prompt_parts.append("\n칩워 관련 이벤트:")
            for event in chipwar_events[:3]:  # Top 3
                prompt_parts.append(f"- {event.get('event', 'N/A')} (영향: {event.get('impact', 'N/A')})")

        # Market context
        if market_context:
            prompt_parts.append("\n시장 맥락:")
            if 'market_trend' in market_context:
                prompt_parts.append(f"- 시장 트렌드: {market_context['market_trend']}")
            if 'sector_performance' in market_context:
                prompt_parts.append(f"- 섹터 성과: {market_context['sector_performance']:+.2f}%")
            if 'news_sentiment' in market_context:
                prompt_parts.append(f"- 뉴스 심리: {market_context['news_sentiment']:.2f}")
                
        # [Phase 3] Multi-Timeframe Analysis
        if multi_timeframe_data:
            prompt_parts.append("\n멀티 타임프레임 분석:")
            for tf, data in multi_timeframe_data.items():
                if data:
                    prompt_parts.append(f"- [{tf}] Price: {data.get('current_price')}, RSI: {data.get('rsi')}, Trend: {data.get('trend')}")

        # [Phase 3] Option Data
        if option_data:
            prompt_parts.append("\n옵션 데이터 분석:")
            prompt_parts.append(f"- P/C Ratio: {option_data.get('put_call_ratio', 'N/A')}")
            prompt_parts.append(f"- Max Pain: {option_data.get('max_pain', 'N/A')}")
            prompt_parts.append(f"- Volume: Call {option_data.get('total_call_volume', 0)} vs Put {option_data.get('total_put_volume', 0)}")

        prompt_parts.append("\n위 정보를 바탕으로 트레이딩 기회를 분석하고 JSON 형식으로 답변하세요.")

        return "\n".join(prompt_parts)

    def _parse_response(self, response_text: str) -> TraderOpinion:
        """Parse Gemini response using Pydantic"""
        import json
        import re

        # Extract JSON from response
        try:
            # Try direct JSON parsing first
            result_dict = json.loads(response_text)
        except json.JSONDecodeError:
            # Extract JSON from markdown code block
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                result_dict = json.loads(json_match.group(1))
            else:
                # Last resort: find JSON-like structure
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result_dict = json.loads(json_match.group(0))
                else:
                    raise ValueError("No valid JSON found in response")

        # Normalize fields for Pydantic if needed
        # e.g. momentum_strength validation is handled by Pydantic Literal
        # But we might need to handle case insensitivity or mapping
        if 'momentum_strength' in result_dict:
             result_dict['momentum_strength'] = result_dict['momentum_strength'].lower()
        
        # Instantiate and Validate with Pydantic
        # This will raise ValidationError if data is invalid
        return TraderOpinion(**result_dict)

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            'name': 'TraderAgentMVP',
            'role': self.role,
            'weight': self.weight,
            'focus': '공격적 트레이딩 기회 포착',
            'absorbed_agents': ['Trader Agent', 'ChipWar Agent (opportunity)'],
            'responsibilities': [
                '단기 트레이딩 기회 식별',
                '기술적 진입/청산 시그널',
                '칩워 관련 기회 평가',
                '모멘텀 및 트렌드 분석'
            ]
        }


# Example usage
if __name__ == "__main__":
    agent = TraderAgentMVP()

    # Test data
    price_data = {
        'current_price': 150.25,
        'open': 148.50,
        'high': 151.00,
        'low': 147.80,
        'volume': 45000000
    }

    technical_data = {
        'rsi': 62.5,
        'macd': {'value': 1.2, 'signal': 0.8},
        'moving_averages': {'ma50': 145.00, 'ma200': 140.00}
    }

    result = agent.analyze(
        symbol='AAPL',
        price_data=price_data,
        technical_data=technical_data
    )

    print(f"Action: {result['action']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Opportunity Score: {result['opportunity_score']:.1f}")
