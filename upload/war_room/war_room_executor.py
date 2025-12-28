"""
War Room Executor - War Room 결정을 실제 주문으로 실행

워크플로우:
1. War Room 토론 → PM 결정 (BUY/SELL/HOLD)
2. 포지션 크기 계산 (Constitution Rules)
3. KIS Broker로 주문 전송
4. 체결 결과 DB 저장
5. 자기학습 데이터 수집

Author: AI Trading System
Date: 2025-12-23
Phase: 25.0 (실거래 테스트)
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WarRoomExecutor:
    """War Room 결정을 실제 주문으로 실행"""

    def __init__(self, kis_broker=None):
        """
        초기화

        Args:
            kis_broker: KIS Broker 인스턴스 (None이면 DRY RUN만 가능)
        """
        self.broker = kis_broker

    async def execute_war_room_decision(
        self,
        ticker: str,
        consensus_action: str,
        consensus_confidence: float,
        votes: Dict[str, Any],
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        War Room 결정을 실제 주문으로 실행

        Args:
            ticker: 종목 코드
            consensus_action: PM 결정 (BUY/SELL/HOLD)
            consensus_confidence: PM 신뢰도 (0.0-1.0)
            votes: 모든 에이전트 투표
            dry_run: True = 실제 주문 안 보냄 (시뮬레이션만)

        Returns:
            실행 결과
        """
        logger.info(
            f"🎯 War Room 결정 실행: {ticker} {consensus_action} "
            f"({consensus_confidence:.0%} 확신)"
        )

        # HOLD/MAINTAIN은 스킵 (아무 행동도 하지 않음)
        if consensus_action in ["HOLD", "MAINTAIN"]:
            logger.info(f"⏸️  {ticker} {consensus_action} → 주문 없음")
            return {
                "status": "skipped",
                "reason": f"{consensus_action} decision",
                "ticker": ticker,
                "action": consensus_action,
                "confidence": consensus_confidence
            }

        # Step 1: 포지션 크기 계산
        position_size = self._calculate_position_size(
            ticker, consensus_action, consensus_confidence
        )

        if position_size == 0:
            logger.info(f"⏸️  {ticker} 포지션 크기 0 → 주문 없음")
            return {
                "status": "skipped",
                "reason": "position_size_zero",
                "ticker": ticker,
                "action": consensus_action,
                "confidence": consensus_confidence
            }

        # Step 2: 현재 가격 조회 (시뮬레이션)
        current_price = await self._get_current_price(ticker)

        # Step 3: 주문 생성
        order = {
            "ticker": ticker,
            "action": consensus_action,  # BUY/SELL
            "quantity": position_size,
            "price": current_price,
            "order_type": "market",  # 시장가
            "reason": f"War Room consensus {consensus_confidence:.0%}",
            "votes": votes
        }

        logger.info(
            f"📝 주문 생성: {consensus_action} {position_size}주 @ ${current_price:.2f}"
        )

        # Step 4: 주문 실행 (dry_run 체크)
        if dry_run or self.broker is None:
            logger.info(f"🧪 DRY RUN 모드 → 실제 주문 안 보냄")
            execution_result = {
                "status": "dry_run",
                "order": order,
                "execution_price": current_price,
                "executed_quantity": position_size,
                "total_value": current_price * position_size,
                "message": "Dry run - no real order sent"
            }
        else:
            # 실제 주문 전송
            logger.info(f"📤 KIS Broker로 실제 주문 전송...")
            execution_result = await self._send_order_to_broker(order)

        logger.info(
            f"✅ {ticker} 주문 완료: {execution_result['status']}"
        )

        return execution_result

    def _calculate_position_size(
        self,
        ticker: str,
        action: str,
        confidence: float
    ) -> int:
        """
        포지션 크기 계산 (Constitution Rules + Extended Actions)

        기본 규칙:
        - 신뢰도 >= 80%: 2% 자본
        - 신뢰도 60-80%: 1% 자본
        - 신뢰도 < 60%: 0.5% 자본

        확장 액션:
        - REDUCE: 기본 크기의 50% (점진적 축소)
        - INCREASE: 기본 크기의 50% (점진적 확대)
        - DCA: 기본 크기의 50% (물타기)
        """
        # 시뮬레이션 자본 (모의투자 기본값)
        total_capital = 100000  # $100,000

        # 신뢰도 기반 자본 배분
        if confidence >= 0.80:
            capital_ratio = 0.02  # 2%
        elif confidence >= 0.60:
            capital_ratio = 0.01  # 1%
        else:
            capital_ratio = 0.005  # 0.5%

        # 액션별 크기 조정
        size_multiplier = 1.0
        if action in ["REDUCE", "INCREASE", "DCA"]:
            size_multiplier = 0.5  # 50% 크기로 점진적 조정
            logger.info(f"📐 {action} 액션: 크기 50% 조정")

        allocated_capital = total_capital * capital_ratio * size_multiplier

        # 시뮬레이션 가격 (나중에 실제 API로 대체)
        simulated_price = 200.0  # $200 가정

        position_size = int(allocated_capital / simulated_price)

        logger.info(
            f"💰 포지션 크기: {position_size}주 "
            f"(자본 {capital_ratio:.1%} × {size_multiplier:.0%} = ${allocated_capital:,.0f})"
        )

        return position_size

    async def _get_current_price(self, ticker: str) -> float:
        """현재 가격 조회 (시뮬레이션)"""
        # TODO: 나중에 실제 API로 대체
        simulated_prices = {
            "AAPL": 195.50,
            "NVDA": 495.75,
            "GOOGL": 140.25,
            "META": 355.80,
            "MSFT": 375.20,
            "TSLA": 245.60,
            "AMZN": 155.30
        }

        price = simulated_prices.get(ticker, 200.0)
        logger.info(f"💵 {ticker} 현재가: ${price:.2f}")
        return price

    async def _send_order_to_broker(self, order: Dict) -> Dict:
        """KIS Broker로 실제 주문 전송"""
        try:
            if self.broker is None:
                raise ValueError("KIS Broker not initialized")

            if order["action"] == "BUY":
                result = self.broker.buy_market_order(
                    ticker=order["ticker"],
                    quantity=order["quantity"]
                )
            else:  # SELL
                result = self.broker.sell_market_order(
                    ticker=order["ticker"],
                    quantity=order["quantity"]
                )

            logger.info(f"📤 KIS 주문 전송 성공: {result}")
            return result

        except Exception as e:
            logger.error(f"❌ KIS 주문 실패: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "order": order
            }
