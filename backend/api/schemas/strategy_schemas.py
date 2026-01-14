"""
Multi-Strategy Orchestration API Schemas

Phase 0, Task T0.4

Pydantic schemas for request/response validation:
- Strategy: 전략 레지스트리
- PositionOwnership: 포지션 소유권
- ConflictLog: 충돌 로그
- ConflictCheck: 충돌 검사 전용

DTO Pattern:
- Base: 공통 필드
- Create: 생성 요청
- Update: 수정 요청
- Response: API 응답

Usage:
    from backend.api.schemas.strategy_schemas import StrategyCreate, StrategyResponse

    # Request validation
    strategy_data = StrategyCreate(
        name="trading",
        display_name="단기 트레이딩",
        persona_type=PersonaType.TRADING,
        priority=50,
        time_horizon=TimeHorizon.SHORT
    )

    # Response serialization
    response = StrategyResponse.from_orm(strategy_model)
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# ====================================
# Enums
# ====================================

class PersonaType(str, Enum):
    """PersonaRouter에서 사용하는 페르소나 타입"""
    TRADING = "trading"
    LONG_TERM = "long_term"
    DIVIDEND = "dividend"
    AGGRESSIVE = "aggressive"


class TimeHorizon(str, Enum):
    """투자 시간 프레임"""
    SHORT = "short"      # 1일~1주
    MEDIUM = "medium"    # 1주~3개월
    LONG = "long"        # 3개월+


class OwnershipType(str, Enum):
    """포지션 소유권 유형"""
    PRIMARY = "primary"  # 독점 소유
    SHARED = "shared"    # 공유 소유


class ConflictResolution(str, Enum):
    """충돌 해결 방법"""
    ALLOWED = "allowed"                  # 충돌 없음, 허용
    BLOCKED = "blocked"                  # 충돌 감지, 차단
    PRIORITY_OVERRIDE = "priority_override"  # 우선순위로 override


class OrderAction(str, Enum):
    """주문 액션"""
    BUY = "buy"
    SELL = "sell"


# ====================================
# ConfigMetadata Schemas (Optional)
# ====================================

class TradingConfigMetadata(BaseModel):
    """단기 트레이딩 전략 설정"""
    max_hold_days: Optional[int] = Field(7, description="최대 보유 기간 (일)")
    stop_loss_pct: Optional[float] = Field(3.0, description="손절 비율 (%)")
    take_profit_pct: Optional[float] = Field(5.0, description="목표 수익률 (%)")


class LongTermConfigMetadata(BaseModel):
    """장기 투자 전략 설정"""
    default_hold_period_days: Optional[int] = Field(90, description="기본 보유 기간 (일)")
    sector_focus: Optional[List[str]] = Field(["technology", "healthcare"], description="섹터 집중")
    rebalance_frequency_days: Optional[int] = Field(30, description="리밸런싱 주기 (일)")


class DividendConfigMetadata(BaseModel):
    """배당 투자 전략 설정"""
    min_dividend_yield: Optional[float] = Field(3.0, description="최소 배당 수익률 (%)")
    dividend_growth_years: Optional[int] = Field(10, description="배당 성장 연속 기간 (년)")
    payout_ratio_max: Optional[float] = Field(70.0, description="최대 배당 성향 (%)")


# ====================================
# Strategy Schemas
# ====================================

class StrategyBase(BaseModel):
    """Strategy 공통 필드"""
    name: str = Field(..., min_length=1, max_length=50, description="전략 시스템명 (unique)")
    display_name: str = Field(..., min_length=1, max_length=100, description="사용자 표시용 이름")
    persona_type: PersonaType = Field(..., description="PersonaRouter 타입")
    priority: int = Field(..., ge=0, le=1000, description="충돌 시 우선순위 (0-1000, 높을수록 우선)")
    time_horizon: TimeHorizon = Field(..., description="투자 시간 프레임")

    @validator('name')
    def name_alphanumeric_underscore(cls, v):
        """이름은 영문자, 숫자, 언더스코어만 허용"""
        if not v.replace('_', '').isalnum():
            raise ValueError('name must contain only alphanumeric characters and underscores')
        return v.lower()


class StrategyCreate(StrategyBase):
    """Strategy 생성 요청"""
    is_active: bool = Field(True, description="활성화 여부")
    config_metadata: Optional[Dict[str, Any]] = Field(None, description="전략별 설정 (JSONB)")


class StrategyUpdate(BaseModel):
    """Strategy 수정 요청 (모든 필드 optional)"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    priority: Optional[int] = Field(None, ge=0, le=1000)
    is_active: Optional[bool] = None
    config_metadata: Optional[Dict[str, Any]] = None


class StrategyResponse(StrategyBase):
    """Strategy 응답"""
    id: str = Field(..., description="전략 ID (UUID)")
    is_active: bool
    config_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====================================
# PositionOwnership Schemas
# ====================================

class PositionOwnershipBase(BaseModel):
    """PositionOwnership 공통 필드"""
    ticker: str = Field(..., min_length=1, max_length=10, description="종목 코드")
    ownership_type: OwnershipType = Field(..., description="소유권 유형")

    @validator('ticker')
    def ticker_uppercase(cls, v):
        """티커는 대문자로 변환"""
        return v.upper()


class PositionOwnershipCreate(PositionOwnershipBase):
    """PositionOwnership 생성 요청"""
    strategy_id: str = Field(..., description="소유 전략 ID")
    position_id: Optional[str] = Field(None, description="포지션 ID (nullable)")
    locked_until: Optional[datetime] = Field(None, description="잠금 해제 시각")
    reasoning: Optional[str] = Field(None, description="소유 이유")


class PositionOwnershipResponse(PositionOwnershipBase):
    """PositionOwnership 응답"""
    id: str = Field(..., description="소유권 ID (UUID)")
    strategy_id: str
    position_id: Optional[str] = None
    locked_until: Optional[datetime] = None
    reasoning: Optional[str] = None
    created_at: datetime

    # Nested: Strategy 정보 포함 (lazy="joined"로 N+1 방지)
    strategy: Optional[StrategyResponse] = None

    class Config:
        from_attributes = True


class PositionOwnershipWithStrategy(PositionOwnershipResponse):
    """PositionOwnership + Strategy 조인 응답"""
    strategy: StrategyResponse = Field(..., description="소유 전략 정보")


# ====================================
# ConflictLog Schemas
# ====================================

class ConflictLogBase(BaseModel):
    """ConflictLog 공통 필드"""
    ticker: str = Field(..., min_length=1, max_length=10, description="충돌 발생 종목")
    action_attempted: OrderAction = Field(..., description="시도된 주문 액션")
    action_blocked: bool = Field(..., description="주문 차단 여부")
    resolution: ConflictResolution = Field(..., description="충돌 해결 방법")
    reasoning: str = Field(..., min_length=1, description="충돌 이유 및 해결 설명 (필수)")

    @validator('ticker')
    def ticker_uppercase(cls, v):
        return v.upper()


class ConflictLogCreate(ConflictLogBase):
    """ConflictLog 생성 요청"""
    conflicting_strategy_id: str = Field(..., description="충돌을 일으킨 전략 ID")
    owning_strategy_id: str = Field(..., description="기존 소유 전략 ID")
    conflicting_strategy_priority: Optional[int] = Field(None, description="충돌 전략 우선순위 (스냅샷)")
    owning_strategy_priority: Optional[int] = Field(None, description="소유 전략 우선순위 (스냅샷)")
    order_id: Optional[str] = Field(None, description="관련 주문 ID")
    ownership_id: Optional[str] = Field(None, description="관련 소유권 ID")


class ConflictLogResponse(ConflictLogBase):
    """ConflictLog 응답"""
    id: str = Field(..., description="충돌 로그 ID (UUID)")
    conflicting_strategy_id: Optional[str] = None
    owning_strategy_id: Optional[str] = None
    conflicting_strategy_priority: Optional[int] = None
    owning_strategy_priority: Optional[int] = None
    order_id: Optional[str] = None
    ownership_id: Optional[str] = None
    created_at: datetime

    # Nested: Strategy 정보 포함 (optional, FK SET NULL)
    conflicting_strategy: Optional[StrategyResponse] = None
    owning_strategy: Optional[StrategyResponse] = None

    class Config:
        from_attributes = True


# ====================================
# ConflictCheck Schemas (전용)
# ====================================

class ConflictCheckRequest(BaseModel):
    """충돌 검사 요청"""
    strategy_id: str = Field(..., description="주문을 시도하는 전략 ID")
    ticker: str = Field(..., min_length=1, max_length=10, description="종목 코드")
    action: OrderAction = Field(..., description="주문 액션")
    quantity: int = Field(..., gt=0, description="주문 수량")

    @validator('ticker')
    def ticker_uppercase(cls, v):
        return v.upper()


class ConflictDetail(BaseModel):
    """충돌 상세 정보"""
    owning_strategy_id: str = Field(..., description="현재 소유 전략 ID")
    owning_strategy_name: str = Field(..., description="현재 소유 전략명")
    owning_strategy_priority: int = Field(..., description="소유 전략 우선순위")
    ownership_type: OwnershipType = Field(..., description="소유권 유형")
    locked_until: Optional[datetime] = Field(None, description="잠금 해제 시각")
    reasoning: str = Field(..., description="충돌 이유 설명")


class ConflictCheckResponse(BaseModel):
    """충돌 검사 응답"""
    has_conflict: bool = Field(..., description="충돌 발생 여부")
    resolution: ConflictResolution = Field(..., description="해결 방법")
    can_proceed: bool = Field(..., description="주문 실행 가능 여부 (True: 허용, False: 차단)")

    # 충돌 상세 (has_conflict=True일 때만)
    conflict_detail: Optional[ConflictDetail] = Field(None, description="충돌 상세 정보")

    # 추가 정보
    reasoning: str = Field(..., description="결정 이유 (AI 설명 가능성)")
    timestamp: datetime = Field(default_factory=datetime.now, description="검사 시각")


# ====================================
# Statistics & Analytics Schemas
# ====================================

class ConflictStatistics(BaseModel):
    """충돌 통계"""
    total_conflicts: int = Field(..., description="총 충돌 건수")
    blocked_count: int = Field(..., description="차단된 건수")
    allowed_count: int = Field(..., description="허용된 건수")
    top_conflicting_tickers: List[tuple] = Field(..., description="충돌 많은 종목 Top 10")
    conflict_by_strategy: Dict[str, int] = Field(..., description="전략별 충돌 건수")


class StrategyPerformanceSummary(BaseModel):
    """전략 성과 요약"""
    strategy_id: str
    strategy_name: str
    total_orders: int = Field(..., description="총 주문 건수")
    successful_orders: int = Field(..., description="성공한 주문")
    blocked_orders: int = Field(..., description="충돌로 차단된 주문")
    active_positions: int = Field(..., description="현재 보유 포지션 수")
    locked_positions: int = Field(..., description="잠금 상태 포지션 수")


# ====================================
# Bulk Operations Schemas
# ====================================

class BulkStrategyActivateRequest(BaseModel):
    """전략 일괄 활성화/비활성화 요청"""
    strategy_ids: List[str] = Field(..., min_items=1, description="전략 ID 목록")
    is_active: bool = Field(..., description="활성화 여부")


class BulkOperationResponse(BaseModel):
    """일괄 작업 응답"""
    success_count: int = Field(..., description="성공 건수")
    failed_count: int = Field(..., description="실패 건수")
    errors: List[str] = Field([], description="오류 메시지 목록")
