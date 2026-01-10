"""
Event Types - 이벤트 타입 정의

작성일: 2026-01-10
"""

from enum import Enum


class EventType(Enum):
    """시스템 이벤트 타입"""

    # ================================================================
    # 데이터 이벤트
    # ================================================================
    MARKET_DATA_RECEIVED = "market_data_received"    # 시장 데이터 수신
    NEWS_RECEIVED = "news_received"                  # 뉴스 수신

    # ================================================================
    # AI 분석 이벤트
    # ================================================================
    AI_ANALYSIS_STARTED = "ai_analysis_started"      # AI 분석 시작
    AI_ANALYSIS_COMPLETE = "ai_analysis_complete"    # AI 분석 완료
    SIGNAL_GENERATED = "signal_generated"            # 시그널 생성

    # ================================================================
    # 주문 이벤트
    # ================================================================
    ORDER_REQUESTED = "order_requested"              # 주문 요청
    ORDER_VALIDATED = "order_validated"              # 주문 검증 완료
    ORDER_REJECTED = "order_rejected"                # 주문 거부
    ORDER_SENT = "order_sent"                        # 주문 전송
    ORDER_FILLED = "order_filled"                    # 주문 체결
    ORDER_CANCELLED = "order_cancelled"              # 주문 취소
    ORDER_FAILED = "order_failed"                    # 주문 실패

    # ================================================================
    # 포지션 이벤트
    # ================================================================
    POSITION_OPENED = "position_opened"              # 포지션 오픈
    POSITION_UPDATED = "position_updated"            # 포지션 업데이트
    POSITION_CLOSED = "position_closed"              # 포지션 종료

    # ================================================================
    # 리스크 이벤트
    # ================================================================
    RISK_ALERT = "risk_alert"                        # 리스크 경고
    STOP_LOSS_HIT = "stop_loss_hit"                  # 스탑로스 도달
    CIRCUIT_BREAKER = "circuit_breaker"              # 서킷브레이커 발동

    # ================================================================
    # 시스템 이벤트
    # ================================================================
    SYSTEM_STARTED = "system_started"                # 시스템 시작
    SYSTEM_SHUTDOWN = "system_shutdown"              # 시스템 종료
    RECOVERY_COMPLETE = "recovery_complete"          # 복구 완료
