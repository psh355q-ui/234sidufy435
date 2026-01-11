"""
Conflict Detector System
Phase 1, Task T1.1

This module handles conflict detection and resolution between multiple trading strategies.
It uses the Strategy Registry and Position Ownership to ensure safe and coordinated execution.

Dependencies:
    - StrategyRepository
    - PositionOwnershipRepository
    - ConflictLogRepository

Algorithm:
    1. Check if the ticker is currently owned (PositionOwnership).
    2. If NOT owned:
        - ALLOW (unless prohibited by other rules)
    3. If OWNED by SAME strategy:
        - ALLOW (Primary owner control)
    4. If OWNED by DIFFERENT strategy:
        - Compare Priorities (Conflicting vs Owner)
        - If Conflicting > Owner:
            - OVERRIDE (with logging)
        - Else:
            - BLOCK (with logging)
"""

from typing import Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database.repository_multi_strategy import (
    StrategyRepository,
    PositionOwnershipRepository,
    ConflictLogRepository
)
from backend.api.schemas.strategy_schemas import (
    ConflictResolution, 
    OrderAction, 
    ConflictCheckResponse, 
    ConflictDetail, 
    OwnershipType
)
from backend.database.models import Strategy, PositionOwnership

class ConflictDetector:
    """전략 충돌 감지 및 해결 엔진"""

    def __init__(self, session: Session):
        self.session = session
        self.strategy_repo = StrategyRepository(session)
        self.ownership_repo = PositionOwnershipRepository(session)
        self.conflict_log_repo = ConflictLogRepository(session)

    def check_conflict(self, 
                       strategy_id: str, 
                       ticker: str, 
                       action: OrderAction, 
                       quantity: int = 0) -> ConflictCheckResponse:
        """
        충돌 여부 검사 및 해결 방법 결정

        Args:
            strategy_id: 요청 전략 ID
            ticker: 종목 코드
            action: 주문 액션 (BUY/SELL)
            quantity: 수량 (0이면 단순 시그널 체크)

        Returns:
            ConflictCheckResponse (allow/block/override + reasoning)
        """
        # 1. 요청 전략 정보 조회
        requesting_strategy = self.strategy_repo.get_by_id(strategy_id)
        if not requesting_strategy:
            return self._create_response(
                has_conflict=True,
                resolution=ConflictResolution.BLOCKED,
                can_proceed=False,
                reasoning=f"Strategy not found: {strategy_id}"
            )

        if not requesting_strategy.is_active:
             return self._create_response(
                has_conflict=True,
                resolution=ConflictResolution.BLOCKED,
                can_proceed=False,
                reasoning=f"Strategy is inactive: {requesting_strategy.name}"
            )
        
        # 2. 현재 소유권 확인
        primary_ownership = self.ownership_repo.get_primary_ownership(ticker)
        
        # Case A: 소유권 없음 (자유 경쟁)
        if not primary_ownership:
            return self._create_response(
                has_conflict=False,
                resolution=ConflictResolution.ALLOWED,
                can_proceed=True,
                reasoning="No current owner. Free to trade."
            )
            
        # Case B: 자신이 소유함 (자유 거래)
        if primary_ownership.strategy_id == strategy_id:
            return self._create_response(
                has_conflict=False,
                resolution=ConflictResolution.ALLOWED,
                can_proceed=True,
                reasoning="Already owned by requesting strategy."
            )
            
        # Case C: 타 전략 소유 (충돌 발생)
        return self._resolve_conflict(requesting_strategy, primary_ownership, action, ticker)

    def _resolve_conflict(self, 
                          requesting_strategy: Strategy, 
                          ownership: PositionOwnership, 
                          action: OrderAction,
                          ticker: str) -> ConflictCheckResponse:
        """충돌 해결 로직 (우선순위 비교)"""
        
        owning_strategy = self.strategy_repo.get_by_id(ownership.strategy_id)

        # 1. 잠금 상태 확인
        is_locked = False
        now = datetime.now()
        if ownership.locked_until and ownership.locked_until > now:
            is_locked = True
            
        # 2. 우선순위 비교
        req_prio = requesting_strategy.priority
        own_prio = owning_strategy.priority
        
        conflict_detail = ConflictDetail(
            owning_strategy_id=owning_strategy.id,
            owning_strategy_name=owning_strategy.name,
            owning_strategy_priority=own_prio,
            ownership_type=OwnershipType(ownership.ownership_type),
            locked_until=ownership.locked_until,
            reasoning=ownership.reasoning or "Owned"
        )
        
        decision_resolution = ConflictResolution.BLOCKED
        decision_blocked = True
        decision_reasoning = ""

        # Decision Logic
        if req_prio > own_prio:
            if is_locked:
                decision_resolution = ConflictResolution.BLOCKED
                decision_blocked = True
                decision_reasoning = f"Target is LOCKED until {ownership.locked_until}"
            else:
                decision_resolution = ConflictResolution.PRIORITY_OVERRIDE
                decision_blocked = False
                decision_reasoning = f"Priority Override: {req_prio} > {own_prio}"
        else:
            decision_resolution = ConflictResolution.BLOCKED
            decision_blocked = True
            decision_reasoning = f"Insufficient Priority: {req_prio} <= {own_prio}"

        # 3. Log to DB
        self.log_decision(
            ticker=ticker,
            conflicting_strategy=requesting_strategy,
            owning_strategy=owning_strategy,
            action=action,
            resolution=decision_resolution,
            reasoning=decision_reasoning,
            action_blocked=decision_blocked,
            ownership_id=ownership.id
        )

        return self._create_response(
            has_conflict=True,
            resolution=decision_resolution,
            can_proceed=not decision_blocked,
            reasoning=decision_reasoning,
            detail=conflict_detail
        )

    def log_decision(self, 
                     ticker: str, 
                     conflicting_strategy: Strategy, 
                     owning_strategy: Strategy, 
                     action: OrderAction, 
                     resolution: ConflictResolution, 
                     reasoning: str,
                     action_blocked: bool,
                     ownership_id: Optional[str] = None):
        """충돌 로그 저장"""
        self.conflict_log_repo.create(
            ticker=ticker,
            conflicting_strategy_id=conflicting_strategy.id,
            owning_strategy_id=owning_strategy.id,
            action_attempted=action.value if hasattr(action, 'value') else str(action),
            action_blocked=action_blocked,
            resolution=resolution.value if hasattr(resolution, 'value') else str(resolution),
            reasoning=reasoning,
            conflicting_strategy_priority=conflicting_strategy.priority,
            owning_strategy_priority=owning_strategy.priority,
            ownership_id=ownership_id
        )

    def _create_response(self, 
                         has_conflict: bool, 
                         resolution: ConflictResolution, 
                         can_proceed: bool, 
                         reasoning: str,
                         detail: Optional[ConflictDetail] = None) -> ConflictCheckResponse:
        """응답 객체 생성 헬퍼"""
        return ConflictCheckResponse(
            has_conflict=has_conflict,
            resolution=resolution,
            can_proceed=can_proceed,
            reasoning=reasoning,
            conflict_detail=detail
        )
