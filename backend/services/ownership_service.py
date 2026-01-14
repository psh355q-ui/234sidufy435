"""
Ownership Service
Phase 2, Task T2.3

Handles the transfer of position ownership between strategies.
Implements business rules for:
- Priority comparison
- Lock status checks
- Transfer logging
- Atomic ownership updates

Dependencies:
    - PositionOwnershipRepository
    - StrategyRepository
    - ConflictLogRepository
    - EventBus (OwnershipTransferredEvent)
"""

from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from backend.database.repository_multi_strategy import (
    PositionOwnershipRepository,
    StrategyRepository,
    ConflictLogRepository
)
from backend.database.models import PositionOwnership, Strategy
from backend.api.schemas.strategy_schemas import OwnershipType
from backend.events import event_bus, EventType

logger = logging.getLogger(__name__)

class OwnershipService:
    """소유권 관리 및 이전 서비스"""

    def __init__(self, session: Session):
        self.session = session
        self.ownership_repo = PositionOwnershipRepository(session)
        self.strategy_repo = StrategyRepository(session)
        self.conflict_repo = ConflictLogRepository(session)

    def transfer_ownership(self, 
                           ticker: str, 
                           from_strategy_id: str, 
                           to_strategy_id: str, 
                           reason: str) -> Dict[str, Any]:
        """
        소유권 이전 (T2.3)

        Args:
            ticker: 종목 코드
            from_strategy_id: 현재 소유 전략 ID
            to_strategy_id: 새 소유 전략 ID
            reason: 이전 사유

        Returns:
            Dict: {success: bool, message: str, ownership_id: str}
        """
        # 1. Validation
        ownership = self.ownership_repo.get_primary_ownership(ticker)
        if not ownership:
            return {"success": False, "message": f"No primary ownership found for {ticker}"}

        if ownership.strategy_id != from_strategy_id:
            # 강제 이전 케이스가 아닌 이상, 소유자가 일치해야 함
            # (Force transfer logic matches from_strategy_id check contextually)
            return {"success": False, "message": f"Owner mismatch: Expected {from_strategy_id}, Found {ownership.strategy_id}"}
        
        target_strategy = self.strategy_repo.get_by_id(to_strategy_id)
        if not target_strategy:
            return {"success": False, "message": f"Target strategy not found: {to_strategy_id}"}

        if not target_strategy.is_active:
             return {"success": False, "message": f"Target strategy inactive: {target_strategy.name}"}

        target_strategy_name = target_strategy.name
        
        # 2. Lock Check
        if ownership.locked_until and ownership.locked_until > datetime.now():
             return {"success": False, "message": f"Ownership is LOCKED until {ownership.locked_until}"}

        # 3. Priority Check (Business Rule: Higher priority can take from lower priority)
        current_strategy = self.strategy_repo.get_by_id(from_strategy_id)
        if not current_strategy:
            return {"success": False, "message": f"Current strategy not found: {from_strategy_id}"}
            
        current_strategy_name = current_strategy.name

        # Refresh/Merge removed to rely on Raw SQL (Fix for DetachedInstanceError loops)
        # ownership = self.session.merge(ownership)
        # target_strategy = self.session.merge(target_strategy)
        # current_strategy = self.session.merge(current_strategy)

        # 우선순위 규칙: 높은 우선순위만 낮은 우선순위로부터 빼앗을 수 있음
        if target_strategy.priority <= current_strategy.priority:
            # Log the blocked attempt
            self._log_conflict(
                ticker=ticker,
                conflicting_strategy_id=to_strategy_id,
                owning_strategy_id=from_strategy_id,
                action_attempted="transfer",
                action_blocked=True,
                resolution="priority_blocked",
                reasoning=f"Priority violation: {target_strategy.priority} <= {current_strategy.priority}",
                conflicting_priority=target_strategy.priority,
                owning_priority=current_strategy.priority
            )

            return {
                "success": False,
                "message": f"Priority violation: {target_strategy_name} (priority={target_strategy.priority}) "
                          f"cannot take from {current_strategy_name} (priority={current_strategy.priority})"
            }

        ownership_id = ownership.id
        
        # 4. Execute Transfer (Query-based Update to avoid instance state issues)
        try:
            # Update via query (bypasses attached/detached instance state)
            self.session.query(PositionOwnership).filter(
                PositionOwnership.id == ownership_id
            ).update({
                "strategy_id": to_strategy_id,
                "reasoning": f"Transferred from {from_strategy_id}: {reason}"
            }, synchronize_session=False)

            # Flush changes
            self.session.flush()

            # Log via scalar values only
            logger.info(f"✅ Ownership transferred: {ticker} | {from_strategy_id} -> {to_strategy_id}")

            # 5. Publish OWNERSHIP_TRANSFERRED Event (Phase 4, T4.2)
            self._publish_transfer_event(
                ticker=ticker,
                from_strategy_id=from_strategy_id,
                from_strategy_name=current_strategy_name,
                to_strategy_id=to_strategy_id,
                to_strategy_name=target_strategy_name,
                reason=reason,
                ownership_id=ownership_id
            )

            return {
                "success": True,
                "message": "Transfer successful",
                "ownership_id": ownership_id,
                "new_owner": target_strategy_name
            }

        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            return {"success": False, "message": str(e)}

    def lock_ownership(self, ticker: str, duration_seconds: int, reason: str) -> bool:
        """소유권 잠금 (일정 시간 동안 이전 불가)"""
        ownership = self.ownership_repo.get_primary_ownership(ticker)
        if not ownership:
            return False
            
        from datetime import timedelta
        ownership.locked_until = datetime.now() + timedelta(seconds=duration_seconds)
        ownership.reasoning += f" | Locked: {reason}"
        self.session.flush()
        return True

    def release_lock(self, ticker: str) -> bool:
        """잠금 해제"""
        ownership = self.ownership_repo.get_primary_ownership(ticker)
        if not ownership:
            return False

        ownership.locked_until = None
        self.session.flush()
        return True

    def _log_conflict(
        self,
        ticker: str,
        conflicting_strategy_id: str,
        owning_strategy_id: str,
        action_attempted: str,
        action_blocked: bool,
        resolution: str,
        reasoning: str,
        conflicting_priority: Optional[int] = None,
        owning_priority: Optional[int] = None,
        ownership_id: Optional[str] = None
    ):
        """
        ConflictLog에 이전 시도 기록 (Phase 2, T2.3)

        Args:
            ticker: 종목 코드
            conflicting_strategy_id: 이전 시도 전략
            owning_strategy_id: 기존 소유 전략
            action_attempted: 시도한 액션
            action_blocked: 차단 여부
            resolution: 해결 방법
            reasoning: 사유
            conflicting_priority: 시도 전략 우선순위
            owning_priority: 소유 전략 우선순위
            ownership_id: 소유권 ID
        """
        try:
            self.conflict_repo.create(
                ticker=ticker,
                action_attempted=action_attempted,
                action_blocked=action_blocked,
                resolution=resolution,
                reasoning=reasoning,
                conflicting_strategy_id=conflicting_strategy_id,
                owning_strategy_id=owning_strategy_id,
                conflicting_strategy_priority=conflicting_priority,
                owning_strategy_priority=owning_priority,
                ownership_id=ownership_id
            )
            self.session.flush()
        except Exception as e:
            logger.warning(f"Failed to log conflict: {e}")
            # 로그 실패는 이전 작업에 영향 주지 않음 (best-effort)

    def _publish_transfer_event(self,
                                ticker: str,
                                from_strategy_id: str,
                                from_strategy_name: str,
                                to_strategy_id: str,
                                to_strategy_name: str,
                                reason: str,
                                ownership_id: str):
        """
        소유권 이전 이벤트 발행 (Phase 4, T4.2)

        Args:
            ticker: 종목 코드
            from_strategy_id: 이전 소유 전략 ID
            from_strategy_name: 이전 소유 전략 이름
            to_strategy_id: 새 소유 전략 ID
            to_strategy_name: 새 소유 전략 이름
            reason: 이전 사유
            ownership_id: 소유권 ID
        """
        event_data = {
            'ticker': ticker,
            'from_strategy_id': from_strategy_id,
            'from_strategy_name': from_strategy_name,
            'to_strategy_id': to_strategy_id,
            'to_strategy_name': to_strategy_name,
            'reason': reason,
            'ownership_id': ownership_id
        }

        try:
            event_bus.publish(EventType.OWNERSHIP_TRANSFERRED, event_data)
            logger.info(f"📢 Event published: OWNERSHIP_TRANSFERRED for {ticker}")
        except Exception as e:
            logger.error(f"Failed to publish ownership transfer event: {e}")
            # Event publishing failure should not affect ownership transfer logic
