"""
Order Manager - Single Writer 원칙

핵심 규칙:
- 상태 변경은 오직 이 클래스를 통해서만 가능
- order.status = "xxx" 직접 변경 절대 금지
- 모든 전이는 DB 영속화 + 로깅 포함

작성일: 2026-01-10
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from .state_machine import (
    OrderState,
    OrderStateMachine,
    InvalidStateTransitionError,
    state_machine
)
from backend.events import event_bus, EventType

logger = logging.getLogger(__name__)


class OrderManager:
    """
    주문 관리자 - Single Writer

    모든 주문 상태 변경은 이 클래스를 통해서만 수행
    """

    def __init__(self, db_session, broker_client=None):
        """
        Args:
            db_session: SQLAlchemy 세션
            broker_client: 브로커 API 클라이언트 (Optional)
        """
        self.db = db_session
        self.broker = broker_client
        self.sm = state_machine

        # 상태 전이 이력 (메모리 캐시)
        self._transition_history: List[Dict] = []

    # ================================================================
    # 핵심 메서드: 상태 전이 (Single Writer)
    # ================================================================

    def transition(
        self,
        order,
        target: OrderState,
        reason: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        상태 전이 실행 (Single Writer)

        Args:
            order: Order 모델 인스턴스
            target: 목표 상태
            reason: 전이 사유
            metadata: 추가 메타데이터

        Returns:
            bool: 성공 여부

        Raises:
            InvalidStateTransitionError: 유효하지 않은 전이
        """
        current = OrderState(order.status)

        # 1. 전이 가능 여부 검증
        if not self.sm.can_transition(current, target):
            error_msg = f"Invalid transition: {current.value} → {target.value}"
            logger.error(f"[ORDER:{order.id}] {error_msg}")
            raise InvalidStateTransitionError(error_msg)

        # 2. 상태 변경 (원자적)
        old_status = order.status
        order.status = target.value
        order.updated_at = datetime.utcnow()

        # 3. 메타데이터 업데이트
        if metadata:
            if not order.order_metadata:
                order.order_metadata = {}
            order.order_metadata.update(metadata)

        # 4. DB 영속화
        try:
            self.db.add(order)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            order.status = old_status  # 롤백
            logger.error(f"[ORDER:{order.id}] DB commit failed: {e}")
            raise

        # 5. 로깅
        self._log_transition(order, current, target, reason)

        # 6. 이력 저장
        self._transition_history.append({
            'order_id': order.id,
            'symbol': order.ticker,
            'from': current.value,
            'to': target.value,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })

        # 7. Event Bus 발행 (Phase 3)
        self._publish_event(order, target, reason)

        return True

    # ================================================================
    # 편의 메서드: 상태별 전이
    # ================================================================

    def receive_signal(self, order, signal_data: Dict) -> bool:
        """시그널 수신 → SIGNAL_RECEIVED"""
        return self.transition(
            order,
            OrderState.SIGNAL_RECEIVED,
            reason="Signal received from AI ensemble",
            metadata={'signal': signal_data}
        )

    def start_validation(self, order) -> bool:
        """검증 시작 → VALIDATING"""
        return self.transition(
            order,
            OrderState.VALIDATING,
            reason="Starting order validation"
        )

    def validation_passed(self, order, validation_result: Dict) -> bool:
        """검증 통과 → ORDER_PENDING"""
        return self.transition(
            order,
            OrderState.ORDER_PENDING,
            reason="Validation passed",
            metadata={'validation': validation_result}
        )

    def validation_failed(self, order, violations: List[str]) -> bool:
        """검증 실패 → REJECTED"""
        return self.transition(
            order,
            OrderState.REJECTED,
            reason=f"Validation failed: {', '.join(violations)}",
            metadata={'violations': violations}
        )

    def order_sent(self, order, broker_order_id: str) -> bool:
        """주문 전송 완료 → ORDER_SENT"""
        order.order_id = broker_order_id
        return self.transition(
            order,
            OrderState.ORDER_SENT,
            reason=f"Order sent to broker: {broker_order_id}",
            metadata={'broker_order_id': broker_order_id}
        )

    def order_failed(self, order, error: str) -> bool:
        """주문 전송 실패 → FAILED"""
        order.error_message = error
        return self.transition(
            order,
            OrderState.FAILED,
            reason=f"Order failed: {error}"
        )

    def partial_fill(self, order, filled_qty: int, filled_price: float) -> bool:
        """부분 체결 → PARTIAL_FILLED"""
        order.filled_quantity = filled_qty
        order.filled_price = filled_price
        return self.transition(
            order,
            OrderState.PARTIAL_FILLED,
            reason=f"Partial fill: {filled_qty} @ ${filled_price}",
            metadata={'filled_qty': filled_qty, 'filled_price': filled_price}
        )

    def fully_filled(self, order, filled_price: float) -> bool:
        """전체 체결 → FULLY_FILLED"""
        order.filled_price = filled_price
        order.filled_at = datetime.utcnow()
        return self.transition(
            order,
            OrderState.FULLY_FILLED,
            reason=f"Fully filled @ ${filled_price}"
        )

    def cancel(self, order, reason: str = "User requested") -> bool:
        """취소 → CANCELLED"""
        return self.transition(
            order,
            OrderState.CANCELLED,
            reason=reason
        )

    # ================================================================
    # 조회 메서드
    # ================================================================

    def get_pending_orders(self) -> List:
        """미완료 주문 조회 (Recovery 대상)"""
        from backend.database.models import Order

        pending_values = [s.value for s in self.sm.PENDING_STATES]
        return self.db.query(Order).filter(
            Order.status.in_(pending_values)
        ).all()

    def get_transition_history(self, order_id: Optional[int] = None) -> List[Dict]:
        """전이 이력 조회"""
        if order_id:
            return [h for h in self._transition_history if h['order_id'] == order_id]
        return self._transition_history

    # ================================================================
    # Private 메서드
    # ================================================================

    def _log_transition(
        self,
        order,
        from_state: OrderState,
        to_state: OrderState,
        reason: Optional[str]
    ):
        """상태 전이 로깅"""
        log_msg = (
            f"[ORDER:{order.id}] "
            f"{order.ticker} "
            f"{from_state.value} → {to_state.value}"
        )
        if reason:
            log_msg += f" | {reason}"

        # 종료 상태는 INFO, 나머지는 DEBUG
        if self.sm.is_terminal(to_state):
            logger.info(log_msg)
        else:
            logger.debug(log_msg)

    def _publish_event(
        self,
        order,
        to_state: OrderState,
        reason: Optional[str]
    ):
        """상태 전이 이벤트 발행 (Phase 3)"""
        event_data = {
            'order_id': order.id,
            'ticker': order.ticker,
            'action': order.action,
            'quantity': order.quantity,
            'status': to_state.value,
            'reason': reason
        }

        # 상태별 이벤트 매핑
        event_map = {
            OrderState.ORDER_SENT: EventType.ORDER_SENT,
            OrderState.FULLY_FILLED: EventType.ORDER_FILLED,
            OrderState.CANCELLED: EventType.ORDER_CANCELLED,
            OrderState.REJECTED: EventType.ORDER_REJECTED,
            OrderState.FAILED: EventType.ORDER_FAILED,
        }

        event_type = event_map.get(to_state)
        if event_type:
            try:
                event_bus.publish(event_type, event_data)
            except Exception as e:
                logger.error(f"Failed to publish event {event_type}: {e}")
