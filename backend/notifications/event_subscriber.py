"""
Event Subscriber - EventBus와 RealtimeNotifier 연결
"""

import logging
from typing import Dict, Any

from backend.events import EventBus, EventType
from backend.notifications.realtime_notifier import RealtimeNotifier, NotificationChannel

logger = logging.getLogger(__name__)

class EventSubscriber:
    """
    EventBus 이벤트를 구독하고 RealtimeNotifier를 통해 알림을 전송하는 중계자
    """
    
    def __init__(self, event_bus: EventBus, notifier: RealtimeNotifier):
        self.event_bus = event_bus
        self.notifier = notifier
        
    def start(self):
        """이벤트 구독 시작"""
        logger.info("Starting EventSubscriber...")
        
        # 주문 관련 이벤트 구독
        self.event_bus.subscribe(EventType.ORDER_FILLED, self._handle_order_filled)
        self.event_bus.subscribe(EventType.ORDER_SENT, self._handle_order_sent)
        self.event_bus.subscribe(EventType.ORDER_CANCELLED, self._handle_order_cancelled)
        self.event_bus.subscribe(EventType.ORDER_REJECTED, self._handle_order_rejected)
        
        # 리스크 관련 이벤트 구독 (예시)
        self.event_bus.subscribe(EventType.STOP_LOSS_HIT, self._handle_stop_loss)
        
        logger.info("EventSubscriber started listening to events")

    async def _handle_order_filled(self, data: Dict[str, Any]):
        """주문 체결 처리"""
        try:
            # WebSocket Broadcast
            await self.notifier.notify_order_filled(data)
            logger.debug(f"Processed ORDER_FILLED event for {data.get('ticker')}")
        except Exception as e:
            logger.error(f"Error handling ORDER_FILLED: {e}")

    async def _handle_order_sent(self, data: Dict[str, Any]):
        """주문 전송 처리"""
        try:
            # WebSocket Broadcast
            # RealtimeNotifier에 notify_order_sent가 없으므로 직접 구성
            message = {
                "type": "order_sent",
                "data": data
            }
            await self.notifier.broadcast_websocket(message)
        except Exception as e:
            logger.error(f"Error handling ORDER_SENT: {e}")

    async def _handle_order_cancelled(self, data: Dict[str, Any]):
        """주문 취소 처리"""
        try:
            message = {
                "type": "order_cancelled",
                "data": data
            }
            await self.notifier.broadcast_websocket(message)
        except Exception as e:
            logger.error(f"Error handling ORDER_CANCELLED: {e}")

    async def _handle_order_rejected(self, data: Dict[str, Any]):
        """주문 거부 처리"""
        try:
            message = {
                "type": "order_rejected",
                "data": data
            }
            await self.notifier.broadcast_websocket(message)
        except Exception as e:
            logger.error(f"Error handling ORDER_REJECTED: {e}")

    async def _handle_stop_loss(self, data: Dict[str, Any]):
        """스탑로스 처리"""
        try:
            # TODO: notify_stop_loss_triggered 호출 시 인자 매핑 필요
            # 현재는 단순 브로드캐스트
            message = {
                "type": "stop_loss_triggered",
                "data": data
            }
            await self.notifier.broadcast_websocket(message)
        except Exception as e:
            logger.error(f"Error handling STOP_LOSS_HIT: {e}")


def setup_event_subscribers(event_bus: EventBus, notifier: RealtimeNotifier) -> EventSubscriber:
    """Subscriber 생성 및 시작"""
    subscriber = EventSubscriber(event_bus, notifier)
    subscriber.start()
    return subscriber
