"""
Position Tracker - 포지션 추적 시스템

Phase E3: Position Tracking System

포지션별 진입가, DCA 이력, 수익률 등을 추적

작성일: 2025-12-06
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class PositionStatus(str, Enum):
    """포지션 상태"""
    OPEN = "open"           # 진행중
    CLOSED = "closed"       # 청산 완료
    STOPPED = "stopped"     # 손절매로 종료


@dataclass
class DCAEntry:
    """DCA 진입 기록"""
    entry_date: datetime
    price: float
    amount: float           # 투자 금액
    shares: float           # 매수 주식 수
    dca_number: int         # 몇 번째 DCA인지 (0=초기 매수, 1=1차 DCA, ...)
    reasoning: str = ""     # DCA 실행 사유

    def to_dict(self) -> Dict[str, Any]:
        """dict 변환"""
        return {
            "entry_date": self.entry_date.isoformat(),
            "price": self.price,
            "amount": self.amount,
            "shares": self.shares,
            "dca_number": self.dca_number,
            "reasoning": self.reasoning
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DCAEntry":
        """dict에서 복원"""
        return DCAEntry(
            entry_date=datetime.fromisoformat(data["entry_date"]),
            price=data["price"],
            amount=data["amount"],
            shares=data["shares"],
            dca_number=data["dca_number"],
            reasoning=data.get("reasoning", "")
        )


@dataclass
class Position:
    """
    포지션 (종목별 보유 현황)

    DCA 이력, 평균 단가, 수익률 등을 추적
    """
    ticker: str
    company_name: str
    status: PositionStatus = PositionStatus.OPEN

    # 포지션 정보
    total_shares: float = 0.0           # 총 보유 주식 수
    total_invested: float = 0.0         # 총 투자액
    avg_entry_price: float = 0.0        # 평균 매수가

    # DCA 이력
    dca_entries: List[DCAEntry] = field(default_factory=list)
    dca_count: int = 0                  # DCA 실행 횟수 (0=초기 매수만)

    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    closed_at: Optional[datetime] = None

    # 청산 정보 (청산 시)
    exit_price: Optional[float] = None
    exit_date: Optional[datetime] = None
    realized_pnl: Optional[float] = None    # 실현 손익
    realized_pnl_pct: Optional[float] = None

    def add_entry(
        self,
        price: float,
        amount: float,
        reasoning: str = ""
    ) -> None:
        """
        포지션 진입 추가 (초기 매수 또는 DCA)

        Args:
            price: 진입 가격
            amount: 투자 금액
            reasoning: 진입 사유
        """
        shares = amount / price

        # DCA Entry 생성
        entry = DCAEntry(
            entry_date=datetime.now(),
            price=price,
            amount=amount,
            shares=shares,
            dca_number=self.dca_count,
            reasoning=reasoning
        )

        self.dca_entries.append(entry)

        # 포지션 업데이트
        self.total_shares += shares
        self.total_invested += amount
        self.avg_entry_price = self.total_invested / self.total_shares

        # DCA 횟수 증가 (초기 매수 후부터 카운트)
        if self.dca_count > 0 or len(self.dca_entries) > 1:
            self.dca_count = len(self.dca_entries) - 1

        self.updated_at = datetime.now()

        logger.info(
            f"Position updated: {self.ticker} - "
            f"Entry #{self.dca_count}: ${price:.2f} x {shares:.4f} shares, "
            f"New avg: ${self.avg_entry_price:.2f}"
        )

    def get_unrealized_pnl(self, current_price: float) -> Dict[str, float]:
        """
        미실현 손익 계산

        Args:
            current_price: 현재 가격

        Returns:
            Dict with pnl (금액), pnl_pct (%)
        """
        if self.status != PositionStatus.OPEN:
            return {"pnl": 0.0, "pnl_pct": 0.0}

        current_value = self.total_shares * current_price
        pnl = current_value - self.total_invested
        pnl_pct = (pnl / self.total_invested) * 100 if self.total_invested > 0 else 0.0

        return {
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "current_value": current_value
        }

    def close_position(
        self,
        exit_price: float,
        reason: str = "manual"
    ) -> Dict[str, float]:
        """
        포지션 청산

        Args:
            exit_price: 청산 가격
            reason: 청산 사유

        Returns:
            실현 손익 정보
        """
        if self.status != PositionStatus.OPEN:
            raise ValueError(f"Position already closed: {self.status}")

        exit_value = self.total_shares * exit_price
        self.realized_pnl = exit_value - self.total_invested
        self.realized_pnl_pct = (self.realized_pnl / self.total_invested) * 100

        self.exit_price = exit_price
        self.exit_date = datetime.now()
        self.closed_at = datetime.now()

        if reason == "stop_loss":
            self.status = PositionStatus.STOPPED
        else:
            self.status = PositionStatus.CLOSED

        self.updated_at = datetime.now()

        logger.info(
            f"Position closed: {self.ticker} - "
            f"Exit: ${exit_price:.2f}, PnL: ${self.realized_pnl:.2f} ({self.realized_pnl_pct:.2f}%)"
        )

        return {
            "realized_pnl": self.realized_pnl,
            "realized_pnl_pct": self.realized_pnl_pct,
            "exit_value": exit_value
        }

    def to_dict(self) -> Dict[str, Any]:
        """dict 변환 (직렬화)"""
        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "status": self.status.value,
            "total_shares": self.total_shares,
            "total_invested": self.total_invested,
            "avg_entry_price": self.avg_entry_price,
            "dca_entries": [entry.to_dict() for entry in self.dca_entries],
            "dca_count": self.dca_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "exit_price": self.exit_price,
            "exit_date": self.exit_date.isoformat() if self.exit_date else None,
            "realized_pnl": self.realized_pnl,
            "realized_pnl_pct": self.realized_pnl_pct
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Position":
        """dict에서 복원 (역직렬화)"""
        return Position(
            ticker=data["ticker"],
            company_name=data["company_name"],
            status=PositionStatus(data["status"]),
            total_shares=data["total_shares"],
            total_invested=data["total_invested"],
            avg_entry_price=data["avg_entry_price"],
            dca_entries=[DCAEntry.from_dict(e) for e in data["dca_entries"]],
            dca_count=data["dca_count"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            closed_at=datetime.fromisoformat(data["closed_at"]) if data["closed_at"] else None,
            exit_price=data.get("exit_price"),
            exit_date=datetime.fromisoformat(data["exit_date"]) if data.get("exit_date") else None,
            realized_pnl=data.get("realized_pnl"),
            realized_pnl_pct=data.get("realized_pnl_pct")
        )


class PositionTracker:
    """
    포지션 추적기

    모든 포지션을 관리하고 영속화
    """

    def __init__(self, data_dir: str = "backend/data"):
        """
        Args:
            data_dir: 데이터 저장 디렉토리
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.positions_file = self.data_dir / "positions.json"

        # 포지션 저장소 (ticker -> Position)
        self.positions: Dict[str, Position] = {}

        # 파일에서 로드
        self._load_positions()

        logger.info(f"PositionTracker initialized with {len(self.positions)} positions")

    def _load_positions(self) -> None:
        """파일에서 포지션 로드"""
        if not self.positions_file.exists():
            logger.info("No existing positions file, starting fresh")
            return

        try:
            with open(self.positions_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for ticker, pos_data in data.items():
                self.positions[ticker] = Position.from_dict(pos_data)

            logger.info(f"Loaded {len(self.positions)} positions from file")

        except Exception as e:
            logger.error(f"Failed to load positions: {e}", exc_info=True)

    def _save_positions(self) -> None:
        """파일에 포지션 저장"""
        try:
            data = {
                ticker: position.to_dict()
                for ticker, position in self.positions.items()
            }

            with open(self.positions_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved {len(self.positions)} positions to file")

        except Exception as e:
            logger.error(f"Failed to save positions: {e}", exc_info=True)

    def get_position(self, ticker: str) -> Optional[Position]:
        """포지션 조회"""
        return self.positions.get(ticker)

    def get_open_positions(self) -> List[Position]:
        """진행중인 포지션 목록"""
        return [
            pos for pos in self.positions.values()
            if pos.status == PositionStatus.OPEN
        ]

    def get_all_positions(self) -> List[Position]:
        """모든 포지션 목록 (청산 포함)"""
        return list(self.positions.values())

    def create_position(
        self,
        ticker: str,
        company_name: str,
        initial_price: float,
        initial_amount: float,
        reasoning: str = "Initial entry",
        strategy_id: Optional[str] = None
    ) -> Position:
        """
        새 포지션 생성 (초기 매수)

        Phase 2, T2.2: Multi-Strategy Orchestration 통합
        strategy_id가 제공되면 자동으로 PositionOwnership을 생성하여 소유권을 할당합니다.

        Args:
            ticker: 종목 티커
            company_name: 회사명
            initial_price: 초기 매수가
            initial_amount: 초기 투자액
            reasoning: 매수 사유
            strategy_id: 소유 전략 ID (Optional)

        Returns:
            생성된 Position
        """
        if ticker in self.positions and self.positions[ticker].status == PositionStatus.OPEN:
            raise ValueError(f"Position already exists for {ticker}")

        position = Position(ticker=ticker, company_name=company_name)
        position.add_entry(initial_price, initial_amount, reasoning)

        self.positions[ticker] = position
        self._save_positions()

        logger.info(f"Created new position: {ticker} @ ${initial_price:.2f}")

        # Phase 2, T2.2: 자동 소유권 할당
        if strategy_id:
            try:
                self._assign_ownership(ticker, strategy_id, reasoning)
                logger.info(f"✅ Assigned ownership: {ticker} → strategy {strategy_id[:8]}...")
            except Exception as e:
                logger.warning(f"⚠️ Failed to assign ownership for {ticker}: {e}")
                # 소유권 할당 실패해도 포지션 생성은 성공 (best-effort)

        return position

    def _assign_ownership(self, ticker: str, strategy_id: str, reasoning: str):
        """
        포지션 소유권 자동 할당 (Phase 2, T2.2)

        Args:
            ticker: 종목 티커
            strategy_id: 소유 전략 ID
            reasoning: 소유 사유
        """
        from backend.database.repository import get_sync_session
        from backend.database.repository_multi_strategy import PositionOwnershipRepository, StrategyRepository
        from backend.events import event_bus, EventType

        db = get_sync_session()
        try:
            ownership_repo = PositionOwnershipRepository(session=db)
            strategy_repo = StrategyRepository(session=db)

            # Primary ownership 획득 시도
            ownership = ownership_repo.create(
                strategy_id=strategy_id,
                ticker=ticker.upper(),
                ownership_type="primary",
                reasoning=reasoning
            )
            db.commit()

            logger.info(f"Ownership created: {ticker} (ID: {ownership.id[:8]}...)")

            # Publish OWNERSHIP_ACQUIRED Event (Phase 4, T4.2)
            try:
                strategy = strategy_repo.get_by_id(strategy_id)
                if strategy:
                    event_bus.publish(EventType.OWNERSHIP_ACQUIRED, {
                        'ticker': ticker.upper(),
                        'strategy_id': strategy_id,
                        'strategy_name': strategy.name,
                        'ownership_type': 'primary',
                        'reasoning': reasoning,
                        'ownership_id': ownership.id
                    })
                    logger.info(f"📢 Event published: OWNERSHIP_ACQUIRED for {ticker}")
            except Exception as e:
                logger.warning(f"Failed to publish ownership acquired event: {e}")
                # Event publishing failure should not affect ownership assignment

        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()

    def add_dca_entry(
        self,
        ticker: str,
        price: float,
        amount: float,
        reasoning: str = ""
    ) -> Position:
        """
        DCA 진입 추가

        Args:
            ticker: 종목 티커
            price: DCA 가격
            amount: DCA 투자액
            reasoning: DCA 사유

        Returns:
            업데이트된 Position
        """
        position = self.get_position(ticker)

        if not position:
            raise ValueError(f"No position found for {ticker}")

        if position.status != PositionStatus.OPEN:
            raise ValueError(f"Position is not open: {ticker} ({position.status})")

        position.add_entry(price, amount, reasoning)
        self._save_positions()

        return position

    def close_position(
        self,
        ticker: str,
        exit_price: float,
        reason: str = "manual"
    ) -> Dict[str, float]:
        """
        포지션 청산

        Args:
            ticker: 종목 티커
            exit_price: 청산 가격
            reason: 청산 사유

        Returns:
            실현 손익 정보
        """
        position = self.get_position(ticker)

        if not position:
            raise ValueError(f"No position found for {ticker}")

        result = position.close_position(exit_price, reason)
        self._save_positions()

        return result

    def get_portfolio_summary(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        포트폴리오 전체 요약

        Args:
            current_prices: 종목별 현재 가격 {ticker: price}

        Returns:
            포트폴리오 요약 정보
        """
        open_positions = self.get_open_positions()

        total_invested = sum(pos.total_invested for pos in open_positions)
        total_current_value = 0.0
        total_unrealized_pnl = 0.0

        positions_detail = []

        for pos in open_positions:
            current_price = current_prices.get(pos.ticker, pos.avg_entry_price)
            pnl_info = pos.get_unrealized_pnl(current_price)

            total_current_value += pnl_info["current_value"]
            total_unrealized_pnl += pnl_info["pnl"]

            positions_detail.append({
                "ticker": pos.ticker,
                "total_invested": pos.total_invested,
                "current_value": pnl_info["current_value"],
                "unrealized_pnl": pnl_info["pnl"],
                "unrealized_pnl_pct": pnl_info["pnl_pct"],
                "avg_entry_price": pos.avg_entry_price,
                "current_price": current_price,
                "dca_count": pos.dca_count
            })

        total_unrealized_pnl_pct = (
            (total_unrealized_pnl / total_invested * 100)
            if total_invested > 0 else 0.0
        )

        # 청산 포지션 통계
        closed_positions = [
            pos for pos in self.positions.values()
            if pos.status in [PositionStatus.CLOSED, PositionStatus.STOPPED]
        ]

        total_realized_pnl = sum(
            pos.realized_pnl for pos in closed_positions
            if pos.realized_pnl is not None
        )

        return {
            "open_positions_count": len(open_positions),
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_unrealized_pnl_pct": total_unrealized_pnl_pct,
            "positions": positions_detail,
            "closed_positions_count": len(closed_positions),
            "total_realized_pnl": total_realized_pnl
        }


# ============================================================================
# Global Singleton
# ============================================================================

_position_tracker: Optional[PositionTracker] = None


def get_position_tracker(data_dir: str = "backend/data") -> PositionTracker:
    """
    PositionTracker 싱글톤 인스턴스 가져오기

    Args:
        data_dir: 데이터 디렉토리

    Returns:
        PositionTracker 인스턴스
    """
    global _position_tracker

    if _position_tracker is None:
        _position_tracker = PositionTracker(data_dir=data_dir)

    return _position_tracker
