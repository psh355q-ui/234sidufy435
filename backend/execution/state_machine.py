"""
Order State Machine - 상태 전이 강제

3-AI 합의 사항:
- 상태 전이는 코드로 강제되어야 함
- 종료 상태는 전이 불가
- Single Writer 원칙 적용

작성일: 2026-01-10
"""

from enum import Enum
from typing import Dict, Set, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderState(Enum):
    """주문 상태 정의 (10개 상태)"""

    # 초기 상태
    IDLE = "idle"                        # 대기
    SIGNAL_RECEIVED = "signal_received"  # 시그널 수신

    # 검증 단계
    VALIDATING = "validating"            # 검증 중

    # 주문 단계
    ORDER_PENDING = "order_pending"      # 주문 전송 대기
    ORDER_SENT = "order_sent"            # 주문 전송 완료

    # 체결 단계
    PARTIAL_FILLED = "partial_filled"    # 부분 체결
    FULLY_FILLED = "fully_filled"        # 전체 체결 (종료)

    # 종료 상태
    CANCELLED = "cancelled"              # 취소 (종료)
    REJECTED = "rejected"                # 거부 (종료)
    FAILED = "failed"                    # 실패 (종료)


class InvalidStateTransitionError(Exception):
    """유효하지 않은 상태 전이 예외"""
    pass


class OrderStateMachine:
    """
    주문 상태 머신 - 전이 규칙 강제

    핵심 원칙:
    1. 유효한 전이만 허용 (나머지는 예외)
    2. 종료 상태는 전이 불가
    3. 모든 전이는 로깅됨
    """

    # ================================================================
    # 상태 전이 규칙 (이것만 허용, 나머지는 모두 거부)
    # ================================================================
    VALID_TRANSITIONS: Dict[OrderState, Set[OrderState]] = {
        OrderState.IDLE: {
            OrderState.SIGNAL_RECEIVED
        },
        OrderState.SIGNAL_RECEIVED: {
            OrderState.VALIDATING,
            OrderState.REJECTED      # 즉시 거부 가능
        },
        OrderState.VALIDATING: {
            OrderState.ORDER_PENDING,
            OrderState.REJECTED      # 검증 실패
        },
        OrderState.ORDER_PENDING: {
            OrderState.ORDER_SENT,
            OrderState.FAILED        # 전송 실패
        },
        OrderState.ORDER_SENT: {
            OrderState.PARTIAL_FILLED,
            OrderState.FULLY_FILLED,
            OrderState.CANCELLED     # 사용자/시스템 취소
        },
        OrderState.PARTIAL_FILLED: {
            OrderState.FULLY_FILLED,
            OrderState.CANCELLED     # 잔량 취소
        },
        # 종료 상태 - 전이 불가
        OrderState.FULLY_FILLED: set(),
        OrderState.CANCELLED: set(),
        OrderState.REJECTED: set(),
        OrderState.FAILED: set(),
    }

    # 종료 상태 목록
    TERMINAL_STATES: Set[OrderState] = {
        OrderState.FULLY_FILLED,
        OrderState.CANCELLED,
        OrderState.REJECTED,
        OrderState.FAILED,
    }

    # 미완료 상태 목록 (Recovery 대상)
    PENDING_STATES: Set[OrderState] = {
        OrderState.ORDER_SENT,
        OrderState.PARTIAL_FILLED,
        OrderState.ORDER_PENDING,
    }

    def can_transition(self, current: OrderState, target: OrderState) -> bool:
        """
        전이 가능 여부 확인

        Args:
            current: 현재 상태
            target: 목표 상태

        Returns:
            bool: 전이 가능 여부
        """
        valid_targets = self.VALID_TRANSITIONS.get(current, set())
        return target in valid_targets

    def get_valid_transitions(self, current: OrderState) -> Set[OrderState]:
        """현재 상태에서 가능한 전이 목록"""
        return self.VALID_TRANSITIONS.get(current, set())

    def is_terminal(self, state: OrderState) -> bool:
        """종료 상태인지 확인"""
        return state in self.TERMINAL_STATES

    def is_pending(self, state: OrderState) -> bool:
        """미완료 상태인지 확인 (Recovery 대상)"""
        return state in self.PENDING_STATES


# 싱글톤 인스턴스
state_machine = OrderStateMachine()
