"""
Order Recovery - 재시작 시 미완료 주문 복구

핵심 원칙:
- 브로커 상태가 진실(Source of Truth)
- 실패한 주문은 수동 검토 플래그
- 자동화의 한계를 시스템이 인지

작성일: 2026-01-10
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

from .state_machine import OrderState, state_machine
from .order_manager import OrderManager

logger = logging.getLogger(__name__)


class OrderRecovery:
    """주문 복구 시스템"""

    def __init__(self, order_manager: OrderManager):
        self.om = order_manager
        self.recovery_results: List[Dict] = []

    async def recover_on_startup(self) -> Dict:
        """
        프로그램 시작 시 미완료 주문 복구

        Returns:
            Dict: 복구 결과 요약
        """
        logger.info("=" * 50)
        logger.info("🔄 Starting Order Recovery...")
        logger.info("=" * 50)

        # 1. 미완료 주문 조회
        pending_orders = self.om.get_pending_orders()

        if not pending_orders:
            logger.info("✅ No pending orders to recover")
            return {'recovered': 0, 'failed': 0, 'total': 0}

        logger.info(f"Found {len(pending_orders)} pending orders")

        recovered = 0
        failed = 0

        # 2. 각 주문 복구 시도
        for order in pending_orders:
            try:
                result = await self._recover_order(order)
                if result['success']:
                    recovered += 1
                else:
                    failed += 1
                self.recovery_results.append(result)

            except Exception as e:
                logger.error(f"[ORDER:{order.id}] Recovery exception: {e}")
                await self._mark_for_review(order, str(e))
                failed += 1

        # 3. 결과 요약
        summary = {
            'recovered': recovered,
            'failed': failed,
            'total': len(pending_orders),
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info("=" * 50)
        logger.info(f"✅ Recovery Complete: {recovered}/{len(pending_orders)} recovered")
        if failed > 0:
            logger.warning(f"⚠️ {failed} orders need manual review")
        logger.info("=" * 50)

        return summary

    async def _recover_order(self, order) -> Dict:
        """
        개별 주문 복구

        Args:
            order: Order 모델 인스턴스

        Returns:
            Dict: 복구 결과
        """
        current_state = OrderState(order.status)
        logger.info(f"[ORDER:{order.id}] {order.ticker} - Recovering from {current_state.value}")

        # 브로커에서 실제 상태 확인
        if not self.om.broker:
            logger.warning(f"[ORDER:{order.id}] No broker client - marking for review")
            await self._mark_for_review(order, "No broker client available")
            return {'success': False, 'order_id': order.id, 'reason': 'No broker'}

        try:
            broker_status = await self.om.broker.get_order_status(order.order_id)
        except Exception as e:
            logger.error(f"[ORDER:{order.id}] Broker API error: {e}")
            await self._mark_for_review(order, f"Broker API error: {e}")
            return {'success': False, 'order_id': order.id, 'reason': str(e)}

        # 브로커 상태에 따라 동기화
        broker_state = broker_status.get('status', '').lower()

        if broker_state == 'filled':
            # 전체 체결
            self.om.fully_filled(order, broker_status.get('filled_price', 0))
            logger.info(f"  ✅ {order.ticker}: Recovered as FULLY_FILLED")
            return {'success': True, 'order_id': order.id, 'new_state': 'fully_filled'}

        elif broker_state == 'cancelled':
            # 취소됨
            self.om.cancel(order, reason="Recovered as cancelled from broker")
            logger.info(f"  ⚠️ {order.ticker}: Recovered as CANCELLED")
            return {'success': True, 'order_id': order.id, 'new_state': 'cancelled'}

        elif broker_state == 'partial':
            # 부분 체결 → 모니터링 재개
            filled_qty = broker_status.get('filled_quantity', 0)
            filled_price = broker_status.get('filled_price', 0)

            if current_state != OrderState.PARTIAL_FILLED:
                self.om.partial_fill(order, filled_qty, filled_price)

            logger.info(f"  🔶 {order.ticker}: Partial filled ({filled_qty}), resuming monitor")
            return {'success': True, 'order_id': order.id, 'new_state': 'partial_filled', 'monitor': True}

        elif broker_state in ['pending', 'open', 'new']:
            # 여전히 진행 중 → 모니터링 재개
            logger.info(f"  🔵 {order.ticker}: Still pending, resuming monitor")
            return {'success': True, 'order_id': order.id, 'new_state': order.status, 'monitor': True}

        else:
            # 알 수 없는 상태
            logger.warning(f"  ❓ {order.ticker}: Unknown broker state '{broker_state}'")
            await self._mark_for_review(order, f"Unknown broker state: {broker_state}")
            return {'success': False, 'order_id': order.id, 'reason': f'Unknown state: {broker_state}'}

    async def _mark_for_review(self, order, error_message: str):
        """수동 검토 필요 플래그 설정"""
        order.needs_manual_review = True
        order.error_message = error_message
        order.updated_at = datetime.utcnow()

        self.om.db.add(order)
        self.om.db.commit()

        logger.warning(f"[ORDER:{order.id}] Marked for manual review: {error_message}")

    def get_recovery_results(self) -> List[Dict]:
        """복구 결과 조회"""
        return self.recovery_results
