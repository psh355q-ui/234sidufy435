"""
Multi-Strategy Orchestration Repository Layer

Phase 0, Task T0.3

Repository pattern for multi-strategy feature:
- StrategyRepository: Strategy registry management
- PositionOwnershipRepository: Position ownership tracking
- ConflictLogRepository: Conflict history (insert-only audit log)

Usage:
    from backend.database.connection import get_sync_session

    with get_sync_session() as session:
        strategy_repo = StrategyRepository(session)
        strategies = strategy_repo.get_active_strategies_by_priority()
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from sqlalchemy.exc import IntegrityError

from backend.database.models import Strategy, PositionOwnership, ConflictLog


# ====================================
# StrategyRepository
# ====================================

class StrategyRepository:
    """전략 레지스트리 관리"""

    def __init__(self, session: Session):
        self.session = session

    # ===== CRUD =====

    def create(self,
               name: str,
               display_name: str,
               persona_type: str,
               priority: int,
               time_horizon: str,
               is_active: bool = True,
               config_metadata: Optional[Dict] = None) -> Strategy:
        """
        새 전략 생성

        Args:
            name: 전략 시스템명 (unique)
            display_name: 표시 이름
            persona_type: PersonaRouter 타입
            priority: 우선순위 (높을수록 우선)
            time_horizon: short/medium/long
            is_active: 활성화 여부
            config_metadata: JSONB 설정

        Returns:
            생성된 Strategy 객체

        Raises:
            IntegrityError: name 중복 시
        """
        strategy = Strategy(
            name=name,
            display_name=display_name,
            persona_type=persona_type,
            priority=priority,
            time_horizon=time_horizon,
            is_active=is_active,
            config_metadata=config_metadata
        )

        self.session.add(strategy)
        self.session.flush()  # ID 생성 (commit은 service layer에서)

        return strategy

    def get_by_id(self, strategy_id: str) -> Optional[Strategy]:
        """ID로 전략 조회"""
        return self.session.query(Strategy).filter(Strategy.id == strategy_id).first()

    def get_by_name(self, name: str) -> Optional[Strategy]:
        """이름으로 전략 조회"""
        return self.session.query(Strategy).filter(Strategy.name == name).first()

    def get_all(self) -> List[Strategy]:
        """모든 전략 조회 (우선순위 내림차순)"""
        return (
            self.session.query(Strategy)
            .order_by(desc(Strategy.priority))
            .all()
        )

    def update(self, strategy_id: str, **kwargs) -> Optional[Strategy]:
        """
        전략 업데이트

        Args:
            strategy_id: 전략 ID
            **kwargs: 업데이트할 필드 (display_name, priority, is_active, config_metadata 등)

        Returns:
            업데이트된 Strategy 또는 None (존재하지 않으면)
        """
        strategy = self.get_by_id(strategy_id)
        if not strategy:
            return None

        for key, value in kwargs.items():
            if hasattr(strategy, key):
                setattr(strategy, key, value)

        strategy.updated_at = datetime.now()
        self.session.flush()

        return strategy

    def delete(self, strategy_id: str) -> bool:
        """
        전략 삭제 (소프트 삭제 권장 - is_active=False)

        주의: position_ownership FK RESTRICT로 인해 소유권이 있으면 삭제 불가

        Returns:
            삭제 성공 여부
        """
        strategy = self.get_by_id(strategy_id)
        if not strategy:
            return False

        self.session.delete(strategy)
        self.session.flush()

        return True

    # ===== Strategy-Specific Methods =====

    def get_active_strategies(self) -> List[Strategy]:
        """활성화된 전략 조회"""
        return (
            self.session.query(Strategy)
            .filter(Strategy.is_active == True)
            .order_by(desc(Strategy.priority))
            .all()
        )

    def get_active_strategies_by_priority(self) -> List[Strategy]:
        """
        활성 전략을 우선순위 내림차순으로 조회

        충돌 검사 핫 경로에서 사용 (캐싱 권장)
        """
        return self.get_active_strategies()

    def activate(self, strategy_id: str) -> bool:
        """전략 활성화"""
        strategy = self.get_by_id(strategy_id)
        if not strategy:
            return False

        strategy.is_active = True
        strategy.updated_at = datetime.now()
        self.session.flush()

        return True

    def deactivate(self, strategy_id: str) -> bool:
        """
        전략 비활성화

        비활성화 시:
        - 새 주문 생성 차단
        - 기존 소유권은 유지 (locked_until 만료 시 자동 해제)
        """
        strategy = self.get_by_id(strategy_id)
        if not strategy:
            return False

        strategy.is_active = False
        strategy.updated_at = datetime.now()
        self.session.flush()

        return True

    def get_by_priority_range(self, min_priority: int, max_priority: int) -> List[Strategy]:
        """우선순위 범위로 전략 조회"""
        return (
            self.session.query(Strategy)
            .filter(
                and_(
                    Strategy.priority >= min_priority,
                    Strategy.priority <= max_priority,
                    Strategy.is_active == True
                )
            )
            .order_by(desc(Strategy.priority))
            .all()
        )


# ====================================
# PositionOwnershipRepository
# ====================================

class PositionOwnershipRepository:
    """포지션 소유권 추적"""

    def __init__(self, session: Session):
        self.session = session

    # ===== CRUD =====

    def create(self,
               strategy_id: str,
               ticker: str,
               ownership_type: str,
               position_id: Optional[str] = None,
               locked_until: Optional[datetime] = None,
               reasoning: Optional[str] = None) -> PositionOwnership:
        """
        소유권 생성

        Args:
            strategy_id: 소유 전략 ID
            ticker: 종목 코드
            ownership_type: primary/shared
            position_id: 포지션 ID (nullable)
            locked_until: 잠금 해제 시각
            reasoning: 소유 이유

        Returns:
            생성된 PositionOwnership

        Raises:
            IntegrityError: primary 소유권 중복 시 (uk_ownership_primary_ticker)
        """
        ownership = PositionOwnership(
            strategy_id=strategy_id,
            ticker=ticker,
            ownership_type=ownership_type,
            position_id=position_id,
            locked_until=locked_until,
            reasoning=reasoning
        )

        self.session.add(ownership)
        self.session.flush()

        return ownership

    def get_by_id(self, ownership_id: str) -> Optional[PositionOwnership]:
        """ID로 소유권 조회"""
        return self.session.query(PositionOwnership).filter(PositionOwnership.id == ownership_id).first()

    def get_by_ticker(self, ticker: str) -> List[PositionOwnership]:
        """
        종목별 소유권 조회

        충돌 검사 핫 경로 (인덱스: idx_ownership_ticker)
        """
        return (
            self.session.query(PositionOwnership)
            .filter(PositionOwnership.ticker == ticker)
            .all()
        )

    def get_by_strategy(self, strategy_id: str) -> List[PositionOwnership]:
        """전략별 소유권 조회"""
        return (
            self.session.query(PositionOwnership)
            .filter(PositionOwnership.strategy_id == strategy_id)
            .all()
        )

    def delete(self, ownership_id: str) -> bool:
        """소유권 삭제"""
        ownership = self.get_by_id(ownership_id)
        if not ownership:
            return False

        self.session.delete(ownership)
        self.session.flush()

        return True

    # ===== Ownership-Specific Methods =====

    def get_primary_ownership(self, ticker: str) -> Optional[PositionOwnership]:
        """
        종목의 primary 소유권 조회

        Returns:
            PositionOwnership 또는 None (소유권 없으면)
        """
        return (
            self.session.query(PositionOwnership)
            .filter(
                and_(
                    PositionOwnership.ticker == ticker,
                    PositionOwnership.ownership_type == 'primary'
                )
            )
            .first()
        )

    def is_ticker_locked(self, ticker: str) -> bool:
        """
        종목 잠금 상태 확인

        잠금 조건:
        - primary 소유권 존재
        - locked_until이 현재 시간보다 미래

        Returns:
            True: 잠금 상태, False: 잠금 해제
        """
        ownership = self.get_primary_ownership(ticker)

        if not ownership:
            return False

        if not ownership.locked_until:
            return False

        return ownership.locked_until > datetime.now()

    def get_locked_ownerships(self) -> List[PositionOwnership]:
        """현재 잠금 상태인 소유권 조회"""
        now = datetime.now()
        return (
            self.session.query(PositionOwnership)
            .filter(
                and_(
                    PositionOwnership.locked_until.isnot(None),
                    PositionOwnership.locked_until > now
                )
            )
            .all()
        )

    def acquire_ownership(self,
                          strategy_id: str,
                          ticker: str,
                          ownership_type: str = 'primary',
                          lock_duration_days: Optional[int] = None,
                          reasoning: Optional[str] = None) -> PositionOwnership:
        """
        소유권 획득 (원자적 작업)

        Args:
            strategy_id: 획득할 전략 ID
            ticker: 종목 코드
            ownership_type: primary/shared
            lock_duration_days: 잠금 기간 (일 단위)
            reasoning: 소유 이유

        Returns:
            생성된 PositionOwnership

        Raises:
            IntegrityError: 이미 primary 소유권이 있으면
        """
        locked_until = None
        if lock_duration_days:
            locked_until = datetime.now() + timedelta(days=lock_duration_days)

        return self.create(
            strategy_id=strategy_id,
            ticker=ticker,
            ownership_type=ownership_type,
            locked_until=locked_until,
            reasoning=reasoning
        )

    def transfer_ownership(self,
                           ticker: str,
                           from_strategy_id: str,
                           to_strategy_id: str,
                           reasoning: Optional[str] = None) -> bool:
        """
        소유권 이전 (원자적 작업)

        1. 기존 소유권 삭제
        2. 새 소유권 생성

        트랜잭션 보장 필요 (Service Layer에서 commit)

        Args:
            ticker: 종목 코드
            from_strategy_id: 기존 소유 전략
            to_strategy_id: 새 소유 전략
            reasoning: 이전 이유

        Returns:
            성공 여부
        """
        # 기존 소유권 조회
        old_ownership = (
            self.session.query(PositionOwnership)
            .filter(
                and_(
                    PositionOwnership.ticker == ticker,
                    PositionOwnership.strategy_id == from_strategy_id
                )
            )
            .first()
        )

        if not old_ownership:
            return False

        # 기존 소유권 삭제
        self.session.delete(old_ownership)

        # 새 소유권 생성
        self.create(
            strategy_id=to_strategy_id,
            ticker=ticker,
            ownership_type=old_ownership.ownership_type,
            locked_until=old_ownership.locked_until,
            reasoning=reasoning or f"Transferred from {from_strategy_id}"
        )

        return True

    def release_ownership(self, ticker: str, strategy_id: str) -> bool:
        """
        소유권 해제 (삭제)

        Args:
            ticker: 종목 코드
            strategy_id: 해제할 전략 ID

        Returns:
            성공 여부
        """
        ownership = (
            self.session.query(PositionOwnership)
            .filter(
                and_(
                    PositionOwnership.ticker == ticker,
                    PositionOwnership.strategy_id == strategy_id
                )
            )
            .first()
        )

        if not ownership:
            return False

        self.session.delete(ownership)
        self.session.flush()

        return True


# ====================================
# ConflictLogRepository
# ====================================

class ConflictLogRepository:
    """충돌 로그 (Insert-Only 감사 로그)"""

    def __init__(self, session: Session):
        self.session = session

    # ===== Create Only (Insert-Only Pattern) =====

    def create(self,
               ticker: str,
               conflicting_strategy_id: str,
               owning_strategy_id: str,
               action_attempted: str,
               action_blocked: bool,
               resolution: str,
               reasoning: str,
               conflicting_strategy_priority: Optional[int] = None,
               owning_strategy_priority: Optional[int] = None,
               order_id: Optional[str] = None,
               ownership_id: Optional[str] = None) -> ConflictLog:
        """
        충돌 로그 생성 (수정/삭제 불가)

        Args:
            ticker: 종목 코드
            conflicting_strategy_id: 충돌 전략 ID
            owning_strategy_id: 소유 전략 ID
            action_attempted: buy/sell
            action_blocked: 차단 여부
            resolution: allowed/blocked/priority_override
            reasoning: 충돌 이유 (필수)
            conflicting_strategy_priority: 우선순위 스냅샷
            owning_strategy_priority: 우선순위 스냅샷
            order_id: 관련 주문 ID
            ownership_id: 관련 소유권 ID

        Returns:
            생성된 ConflictLog
        """
        conflict_log = ConflictLog(
            ticker=ticker,
            conflicting_strategy_id=conflicting_strategy_id,
            owning_strategy_id=owning_strategy_id,
            action_attempted=action_attempted,
            action_blocked=action_blocked,
            resolution=resolution,
            reasoning=reasoning,
            conflicting_strategy_priority=conflicting_strategy_priority,
            owning_strategy_priority=owning_strategy_priority,
            order_id=order_id,
            ownership_id=ownership_id
        )

        self.session.add(conflict_log)
        self.session.flush()

        return conflict_log

    # ===== Read Methods =====

    def get_by_id(self, log_id: str) -> Optional[ConflictLog]:
        """ID로 충돌 로그 조회"""
        return self.session.query(ConflictLog).filter(ConflictLog.id == log_id).first()

    def get_recent_conflicts(self, days: int = 7, limit: int = 100) -> List[ConflictLog]:
        """
        최근 N일간 충돌 로그 조회

        Args:
            days: 조회 기간 (일)
            limit: 최대 개수

        Returns:
            최신순 ConflictLog 리스트
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        return (
            self.session.query(ConflictLog)
            .filter(ConflictLog.created_at >= cutoff_time)
            .order_by(desc(ConflictLog.created_at))
            .limit(limit)
            .all()
        )

    def get_by_ticker(self, ticker: str, days: int = 30) -> List[ConflictLog]:
        """
        종목별 충돌 이력 조회

        Args:
            ticker: 종목 코드
            days: 조회 기간

        Returns:
            해당 종목의 충돌 로그 (최신순)
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        return (
            self.session.query(ConflictLog)
            .filter(
                and_(
                    ConflictLog.ticker == ticker,
                    ConflictLog.created_at >= cutoff_time
                )
            )
            .order_by(desc(ConflictLog.created_at))
            .all()
        )

    def get_blocked_conflicts(self, days: int = 7) -> List[ConflictLog]:
        """
        차단된 충돌 조회 (action_blocked=True)

        분석용: 어떤 전략 조합이 자주 충돌하는지 확인
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        return (
            self.session.query(ConflictLog)
            .filter(
                and_(
                    ConflictLog.action_blocked == True,
                    ConflictLog.created_at >= cutoff_time
                )
            )
            .order_by(desc(ConflictLog.created_at))
            .all()
        )

    def get_conflict_count_by_strategy(self, days: int = 30) -> Dict[str, int]:
        """
        전략별 충돌 발생 건수 집계

        Returns:
            {strategy_id: conflict_count}
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        results = (
            self.session.query(
                ConflictLog.conflicting_strategy_id,
                func.count(ConflictLog.id).label('count')
            )
            .filter(ConflictLog.created_at >= cutoff_time)
            .group_by(ConflictLog.conflicting_strategy_id)
            .all()
        )

        return {str(strategy_id): count for strategy_id, count in results if strategy_id}

    def get_conflict_count_by_ticker(self, days: int = 30, top_n: int = 10) -> List[tuple]:
        """
        종목별 충돌 발생 건수 Top N

        Args:
            days: 조회 기간
            top_n: 상위 N개

        Returns:
            [(ticker, count), ...] 튜플 리스트
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        results = (
            self.session.query(
                ConflictLog.ticker,
                func.count(ConflictLog.id).label('count')
            )
            .filter(ConflictLog.created_at >= cutoff_time)
            .group_by(ConflictLog.ticker)
            .order_by(desc('count'))
            .limit(top_n)
            .all()
        )

        return [(ticker, count) for ticker, count in results]
