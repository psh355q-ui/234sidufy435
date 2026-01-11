"""
Mock objects for Multi-Strategy Orchestration tests

Phase 0, Task T0.6

Mock classes for testing without database dependency:
- MockStrategy: 전략 레지스트리 Mock
- MockPositionOwnership: 포지션 소유권 Mock
- MockConflictLog: 충돌 로그 Mock

Usage:
    from backend.tests.mocks.strategy_mocks import create_mock_strategy, create_mock_ownership

    strategy = create_mock_strategy(name="trading", priority=50)
    ownership = create_mock_ownership(ticker="AAPL", strategy_id=strategy.id)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid


class MockStrategy:
    """Mock Strategy model for testing"""

    def __init__(
        self,
        id: str,
        name: str,
        display_name: str,
        persona_type: str,
        priority: int,
        time_horizon: str,
        is_active: bool = True,
        config_metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.display_name = display_name
        self.persona_type = persona_type
        self.priority = priority
        self.time_horizon = time_horizon
        self.is_active = is_active
        self.config_metadata = config_metadata or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def __repr__(self):
        return f"<MockStrategy(name='{self.name}', priority={self.priority})>"


class MockPositionOwnership:
    """Mock PositionOwnership model for testing"""

    def __init__(
        self,
        id: str,
        strategy_id: str,
        ticker: str,
        ownership_type: str,
        position_id: Optional[str] = None,
        locked_until: Optional[datetime] = None,
        reasoning: Optional[str] = None,
        created_at: Optional[datetime] = None,
        strategy: Optional[MockStrategy] = None
    ):
        self.id = id
        self.strategy_id = strategy_id
        self.ticker = ticker
        self.ownership_type = ownership_type
        self.position_id = position_id
        self.locked_until = locked_until
        self.reasoning = reasoning
        self.created_at = created_at or datetime.now()
        self.strategy = strategy

    def __repr__(self):
        return f"<MockPositionOwnership(ticker='{self.ticker}', type='{self.ownership_type}')>"


class MockConflictLog:
    """Mock ConflictLog model for testing"""

    def __init__(
        self,
        id: str,
        ticker: str,
        action_attempted: str,
        action_blocked: bool,
        resolution: str,
        reasoning: str,
        conflicting_strategy_id: Optional[str] = None,
        owning_strategy_id: Optional[str] = None,
        conflicting_strategy_priority: Optional[int] = None,
        owning_strategy_priority: Optional[int] = None,
        order_id: Optional[str] = None,
        ownership_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        conflicting_strategy: Optional[MockStrategy] = None,
        owning_strategy: Optional[MockStrategy] = None
    ):
        self.id = id
        self.ticker = ticker
        self.action_attempted = action_attempted
        self.action_blocked = action_blocked
        self.resolution = resolution
        self.reasoning = reasoning
        self.conflicting_strategy_id = conflicting_strategy_id
        self.owning_strategy_id = owning_strategy_id
        self.conflicting_strategy_priority = conflicting_strategy_priority
        self.owning_strategy_priority = owning_strategy_priority
        self.order_id = order_id
        self.ownership_id = ownership_id
        self.created_at = created_at or datetime.now()
        self.conflicting_strategy = conflicting_strategy
        self.owning_strategy = owning_strategy

    def __repr__(self):
        return f"<MockConflictLog(ticker='{self.ticker}', resolution='{self.resolution}')>"


# ====================================
# Factory Functions
# ====================================

def create_mock_strategy(
    name: str = "trading",
    display_name: Optional[str] = None,
    persona_type: Optional[str] = None,
    priority: int = 50,
    time_horizon: str = "short",
    is_active: bool = True,
    config_metadata: Optional[Dict[str, Any]] = None,
    id: Optional[str] = None
) -> MockStrategy:
    """
    Create a mock Strategy object for testing

    Args:
        name: Strategy system name (default: "trading")
        display_name: Display name (default: auto-generated from name)
        persona_type: PersonaType (default: same as name)
        priority: Priority 0-1000 (default: 50)
        time_horizon: Time horizon (default: "short")
        is_active: Active status (default: True)
        config_metadata: Strategy config (default: {})
        id: Strategy ID (default: auto-generated UUID)

    Returns:
        MockStrategy instance

    Example:
        >>> strategy = create_mock_strategy(name="long_term", priority=100)
        >>> assert strategy.priority == 100
    """
    return MockStrategy(
        id=id or str(uuid.uuid4()),
        name=name,
        display_name=display_name or f"Mock {name.title()}",
        persona_type=persona_type or name,
        priority=priority,
        time_horizon=time_horizon,
        is_active=is_active,
        config_metadata=config_metadata
    )


def create_mock_ownership(
    ticker: str = "AAPL",
    strategy_id: Optional[str] = None,
    ownership_type: str = "primary",
    locked_until: Optional[datetime] = None,
    reasoning: Optional[str] = None,
    id: Optional[str] = None,
    strategy: Optional[MockStrategy] = None
) -> MockPositionOwnership:
    """
    Create a mock PositionOwnership object for testing

    Args:
        ticker: Stock ticker (default: "AAPL")
        strategy_id: Owning strategy ID (default: auto-generated UUID)
        ownership_type: "primary" or "shared" (default: "primary")
        locked_until: Lock expiration time (default: None)
        reasoning: Ownership reason (default: auto-generated)
        id: Ownership ID (default: auto-generated UUID)
        strategy: Related MockStrategy (default: None)

    Returns:
        MockPositionOwnership instance

    Example:
        >>> ownership = create_mock_ownership(ticker="TSLA", locked_until=datetime.now() + timedelta(days=7))
        >>> assert ownership.ticker == "TSLA"
        >>> assert ownership.locked_until > datetime.now()
    """
    return MockPositionOwnership(
        id=id or str(uuid.uuid4()),
        strategy_id=strategy_id or str(uuid.uuid4()),
        ticker=ticker.upper(),
        ownership_type=ownership_type,
        locked_until=locked_until,
        reasoning=reasoning or f"Mock ownership for {ticker}",
        strategy=strategy
    )


def create_mock_conflict_log(
    ticker: str = "AAPL",
    action_attempted: str = "sell",
    action_blocked: bool = True,
    resolution: str = "blocked",
    reasoning: str = "Conflict detected",
    conflicting_strategy_id: Optional[str] = None,
    owning_strategy_id: Optional[str] = None,
    id: Optional[str] = None
) -> MockConflictLog:
    """
    Create a mock ConflictLog object for testing

    Args:
        ticker: Stock ticker (default: "AAPL")
        action_attempted: "buy" or "sell" (default: "sell")
        action_blocked: Whether action was blocked (default: True)
        resolution: Resolution type (default: "blocked")
        reasoning: Conflict reason (default: "Conflict detected")
        conflicting_strategy_id: Conflicting strategy ID (default: auto-generated)
        owning_strategy_id: Owning strategy ID (default: auto-generated)
        id: Log ID (default: auto-generated UUID)

    Returns:
        MockConflictLog instance

    Example:
        >>> log = create_mock_conflict_log(ticker="MSFT", action_blocked=False, resolution="priority_override")
        >>> assert log.action_blocked is False
        >>> assert log.resolution == "priority_override"
    """
    return MockConflictLog(
        id=id or str(uuid.uuid4()),
        ticker=ticker.upper(),
        action_attempted=action_attempted,
        action_blocked=action_blocked,
        resolution=resolution,
        reasoning=reasoning,
        conflicting_strategy_id=conflicting_strategy_id or str(uuid.uuid4()),
        owning_strategy_id=owning_strategy_id or str(uuid.uuid4())
    )


# ====================================
# Preset Mocks (Default Strategies)
# ====================================

def get_preset_strategies() -> Dict[str, MockStrategy]:
    """
    Get preset strategy mocks matching the seed data

    Returns:
        Dict mapping strategy name to MockStrategy

    Example:
        >>> strategies = get_preset_strategies()
        >>> assert strategies["long_term"].priority == 100
        >>> assert strategies["trading"].priority == 50
    """
    return {
        "long_term": create_mock_strategy(
            name="long_term",
            display_name="장기 투자",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            config_metadata={"default_hold_period_days": 90}
        ),
        "dividend": create_mock_strategy(
            name="dividend",
            display_name="배당 투자",
            persona_type="dividend",
            priority=90,
            time_horizon="long",
            config_metadata={"min_dividend_yield": 3.0}
        ),
        "trading": create_mock_strategy(
            name="trading",
            display_name="단기 트레이딩",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            config_metadata={"max_hold_days": 7}
        ),
        "aggressive": create_mock_strategy(
            name="aggressive",
            display_name="공격적 단타",
            persona_type="aggressive",
            priority=30,
            time_horizon="short",
            config_metadata={"max_hold_days": 1}
        )
    }


def create_conflict_scenario_long_vs_trading() -> tuple:
    """
    Create a conflict scenario: Long-term owns AAPL, Trading tries to sell

    Returns:
        (long_term_strategy, trading_strategy, ownership)

    Example:
        >>> long_term, trading, ownership = create_conflict_scenario_long_vs_trading()
        >>> assert ownership.ticker == "AAPL"
        >>> assert ownership.strategy_id == long_term.id
    """
    strategies = get_preset_strategies()
    long_term = strategies["long_term"]
    trading = strategies["trading"]

    ownership = create_mock_ownership(
        ticker="AAPL",
        strategy_id=long_term.id,
        ownership_type="primary",
        locked_until=datetime.now() + timedelta(days=30),
        reasoning="Long-term growth investment",
        strategy=long_term
    )

    return long_term, trading, ownership


def create_conflict_scenario_same_strategy() -> tuple:
    """
    Create a scenario: Same strategy (no conflict)

    Returns:
        (trading_strategy, ownership)

    Example:
        >>> trading, ownership = create_conflict_scenario_same_strategy()
        >>> assert ownership.strategy_id == trading.id
    """
    strategies = get_preset_strategies()
    trading = strategies["trading"]

    ownership = create_mock_ownership(
        ticker="TSLA",
        strategy_id=trading.id,
        ownership_type="primary",
        reasoning="Short-term momentum trade",
        strategy=trading
    )

    return trading, ownership


def create_conflict_scenario_priority_override() -> tuple:
    """
    Create a scenario: Higher priority strategy overrides lower priority

    Long-term (priority=100) owns NVDA, Trading (priority=50) tries to sell
    → Trading should be blocked

    But if we reverse: Trading owns, Long-term tries to buy
    → Long-term should override (priority_override)

    Returns:
        (trading_strategy, long_term_strategy, trading_ownership)

    Example:
        >>> trading, long_term, ownership = create_conflict_scenario_priority_override()
        >>> assert long_term.priority > trading.priority
    """
    strategies = get_preset_strategies()
    trading = strategies["trading"]
    long_term = strategies["long_term"]

    # Trading owns NVDA
    ownership = create_mock_ownership(
        ticker="NVDA",
        strategy_id=trading.id,
        ownership_type="primary",
        reasoning="Short-term chip rally trade",
        strategy=trading
    )

    return trading, long_term, ownership
