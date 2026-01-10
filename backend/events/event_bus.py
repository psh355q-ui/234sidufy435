"""
Event Bus - In-process 이벤트 버스

핵심 원칙:
- 가벼운 In-process 구현 (Kafka/Redis 아님)
- 모든 이벤트 로깅 (추적성)
- 동기/비동기 핸들러 구분

작성일: 2026-01-10
"""

from typing import Callable, Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import logging
import asyncio
from functools import wraps

from .event_types import EventType

logger = logging.getLogger(__name__)


class EventBus:
    """
    In-process Event Bus

    사용법:
        event_bus = EventBus()
        event_bus.subscribe(EventType.ORDER_FILLED, handle_fill)
        event_bus.publish(EventType.ORDER_FILLED, {'order_id': 123})
    """

    def __init__(self):
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._async_handlers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Dict] = []
        self._max_history = 1000  # 최대 이력 보관

    # ================================================================
    # 구독
    # ================================================================

    def subscribe(
        self,
        event_type: EventType,
        handler: Callable,
        is_async: bool = False
    ):
        """
        이벤트 구독

        Args:
            event_type: 구독할 이벤트 타입
            handler: 핸들러 함수
            is_async: 비동기 핸들러 여부
        """
        if is_async:
            if event_type not in self._async_handlers:
                self._async_handlers[event_type] = []
            self._async_handlers[event_type].append(handler)
        else:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)

        logger.debug(f"Subscribed {handler.__name__} to {event_type.value} (async={is_async})")

    def unsubscribe(self, event_type: EventType, handler: Callable):
        """이벤트 구독 해제"""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ]
        if event_type in self._async_handlers:
            self._async_handlers[event_type] = [
                h for h in self._async_handlers[event_type] if h != handler
            ]

    # ================================================================
    # 발행
    # ================================================================

    def publish(self, event_type: EventType, data: Dict[str, Any]):
        """
        이벤트 발행 (동기)

        Args:
            event_type: 이벤트 타입
            data: 이벤트 데이터
        """
        event = self._create_event(event_type, data)

        # 로깅 (추적성)
        self._log_event(event)

        # 이력 저장
        self._save_history(event)

        # 동기 핸들러 실행
        for handler in self._handlers.get(event_type, []):
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Handler {handler.__name__} failed: {e}")
                # 핸들러 실패가 전체 흐름을 막지 않음

    async def publish_async(self, event_type: EventType, data: Dict[str, Any]):
        """
        이벤트 발행 (비동기 핸들러 포함)

        Args:
            event_type: 이벤트 타입
            data: 이벤트 데이터
        """
        event = self._create_event(event_type, data)

        # 로깅
        self._log_event(event)

        # 이력 저장
        self._save_history(event)

        # 동기 핸들러 먼저
        for handler in self._handlers.get(event_type, []):
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Sync handler {handler.__name__} failed: {e}")

        # 비동기 핸들러
        async_handlers = self._async_handlers.get(event_type, [])
        if async_handlers:
            tasks = [handler(data) for handler in async_handlers]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for handler, result in zip(async_handlers, results):
                if isinstance(result, Exception):
                    logger.error(f"Async handler {handler.__name__} failed: {result}")

    # ================================================================
    # 이력 조회
    # ================================================================

    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        이벤트 이력 조회

        Args:
            event_type: 필터링할 이벤트 타입 (None=전체)
            limit: 최대 조회 개수

        Returns:
            List[Dict]: 이벤트 이력
        """
        history = self._event_history

        if event_type:
            history = [e for e in history if e['type'] == event_type.value]

        return history[-limit:]

    def reconstruct_day(self, date: str) -> List[Dict]:
        """
        특정 날짜의 이벤트 흐름 재구성

        Args:
            date: 날짜 (YYYY-MM-DD)

        Returns:
            List[Dict]: 해당 날짜의 이벤트 목록
        """
        return [
            e for e in self._event_history
            if e['timestamp'].startswith(date)
        ]

    # ================================================================
    # Private 메서드
    # ================================================================

    def _create_event(self, event_type: EventType, data: Dict) -> Dict:
        """이벤트 객체 생성"""
        return {
            'type': event_type.value,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'symbol': data.get('symbol', data.get('ticker', 'N/A')),
            'order_id': data.get('order_id', data.get('id', None)),
        }

    def _log_event(self, event: Dict):
        """이벤트 로깅"""
        log_msg = f"EVENT: {event['type']} | {event['symbol']}"

        if event['order_id']:
            log_msg += f" | order:{event['order_id']}"

        # 중요 이벤트는 INFO, 나머지는 DEBUG
        important_events = {
            'order_filled', 'order_rejected', 'stop_loss_hit',
            'circuit_breaker', 'risk_alert', 'position_opened', 'position_closed'
        }

        if event['type'] in important_events:
            logger.info(log_msg)
        else:
            logger.debug(log_msg)

    def _save_history(self, event: Dict):
        """이벤트 이력 저장"""
        self._event_history.append(event)

        # 최대 개수 초과 시 오래된 것 제거
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]


# 싱글톤 인스턴스
event_bus = EventBus()
