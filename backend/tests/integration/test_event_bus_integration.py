"""
Integration Tests for Event Bus with Multi-Strategy Orchestration

Phase 4, Task T4.2 - Event Bus Integration

Tests that conflict detection and ownership transfer events are properly published
to the Event Bus and can be subscribed to by handlers.

Prerequisites:
    - PostgreSQL running (docker compose up -d db)
    - Seed strategies loaded

Run:
    pytest backend/tests/integration/test_event_bus_integration.py -v
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

# Import database setup
from backend.database.repository import get_sync_session
from backend.database.models import Strategy, PositionOwnership

# Import repositories
from backend.database.repository_multi_strategy import (
    StrategyRepository,
    PositionOwnershipRepository
)

# Import services
from backend.ai.skills.system.conflict_detector import ConflictDetector
from backend.services.ownership_service import OwnershipService
from backend.api.schemas.strategy_schemas import OrderAction

# Import Event Bus
from backend.events import event_bus, EventType


@pytest.fixture(scope="function")
def db_session():
    """
    Create a database session for testing

    Uses real PostgreSQL database
    Cleans up test data after each test
    """
    db = get_sync_session()

    try:
        yield db
    finally:
        # Cleanup: Delete test data created during this test
        db.query(PositionOwnership).filter(PositionOwnership.ticker.like("TEST_%")).delete()
        db.query(Strategy).filter(Strategy.name.like("test_%")).delete()
        db.commit()
        db.close()


@pytest.fixture
def strategy_repo(db_session):
    """Create StrategyRepository instance"""
    return StrategyRepository(session=db_session)


@pytest.fixture
def ownership_repo(db_session):
    """Create PositionOwnershipRepository instance"""
    return PositionOwnershipRepository(session=db_session)


@pytest.fixture
def conflict_detector(db_session):
    """Create ConflictDetector instance"""
    return ConflictDetector(session=db_session)


@pytest.fixture
def ownership_service(db_session):
    """Create OwnershipService instance"""
    return OwnershipService(session=db_session)


@pytest.fixture
def event_collector():
    """
    Fixture that collects events published during test

    Returns a dict of event_type -> list of events
    """
    collected_events = {
        EventType.CONFLICT_DETECTED: [],
        EventType.ORDER_BLOCKED_BY_CONFLICT: [],
        EventType.PRIORITY_OVERRIDE: [],
        EventType.OWNERSHIP_TRANSFERRED: [],
        EventType.OWNERSHIP_ACQUIRED: []
    }

    def make_handler(event_type):
        def handler(data):
            collected_events[event_type].append(data)
        return handler

    # Subscribe handlers
    for event_type in collected_events.keys():
        handler = make_handler(event_type)
        event_bus.subscribe(event_type, handler)

    yield collected_events

    # Cleanup: unsubscribe all handlers
    # Note: EventBus doesn't maintain handler references in current implementation
    # So we need to manually clear if necessary


class TestConflictEventPublishing:
    """Tests for conflict detection event publishing"""

    def test_conflict_detected_event_on_block(
        self,
        conflict_detector,
        strategy_repo,
        ownership_repo,
        db_session,
        event_collector
    ):
        """Test CONFLICT_DETECTED and ORDER_BLOCKED_BY_CONFLICT events are published when order is blocked"""
        # Arrange: Create two strategies with different priorities
        long_term = strategy_repo.create(
            name="test_long_term_event",
            display_name="Long Term Event Test",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        trading = strategy_repo.create(
            name="test_trading_event",
            display_name="Trading Event Test",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        db_session.commit()

        # Create ownership for long_term strategy
        ownership_repo.create(
            strategy_id=long_term.id,
            ticker="TEST_AAPL_EVENT",
            ownership_type="primary",
            reasoning="Long-term hold"
        )
        db_session.commit()

        # Act: Trading strategy tries to sell (should be BLOCKED)
        result = conflict_detector.check_conflict(
            strategy_id=trading.id,
            ticker="TEST_AAPL_EVENT",
            action=OrderAction.SELL,
            quantity=10
        )

        # Assert: Check conflict result
        assert result.has_conflict is True
        assert result.resolution.value == "blocked"
        assert result.can_proceed is False

        # Assert: Check events were published
        assert len(event_collector[EventType.CONFLICT_DETECTED]) == 1
        assert len(event_collector[EventType.ORDER_BLOCKED_BY_CONFLICT]) == 1

        # Verify event data
        conflict_event = event_collector[EventType.CONFLICT_DETECTED][0]
        assert conflict_event['ticker'] == "TEST_AAPL_EVENT"
        assert conflict_event['requesting_strategy_name'] == "test_trading_event"
        assert conflict_event['owning_strategy_name'] == "test_long_term_event"
        assert conflict_event['resolution'] == "blocked"

    def test_priority_override_event(
        self,
        conflict_detector,
        strategy_repo,
        ownership_repo,
        db_session,
        event_collector
    ):
        """Test PRIORITY_OVERRIDE event is published when higher priority strategy takes over"""
        # Arrange: Create two strategies
        long_term = strategy_repo.create(
            name="test_lt_override",
            display_name="Long Term Override Test",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        trading = strategy_repo.create(
            name="test_tr_override",
            display_name="Trading Override Test",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        db_session.commit()

        # Trading owns the position
        ownership_repo.create(
            strategy_id=trading.id,
            ticker="TEST_TSLA_OVERRIDE",
            ownership_type="primary",
            reasoning="Short-term trade"
        )
        db_session.commit()

        # Act: Long-term tries to buy (should OVERRIDE)
        result = conflict_detector.check_conflict(
            strategy_id=long_term.id,
            ticker="TEST_TSLA_OVERRIDE",
            action=OrderAction.BUY,
            quantity=5
        )

        # Assert: Check conflict result
        assert result.has_conflict is True
        assert result.resolution.value == "priority_override"
        assert result.can_proceed is True

        # Assert: Check events were published
        assert len(event_collector[EventType.CONFLICT_DETECTED]) == 1
        assert len(event_collector[EventType.PRIORITY_OVERRIDE]) == 1

        # Verify event data
        override_event = event_collector[EventType.PRIORITY_OVERRIDE][0]
        assert override_event['ticker'] == "TEST_TSLA_OVERRIDE"
        assert override_event['requesting_priority'] == 100
        assert override_event['owning_priority'] == 50
        assert override_event['resolution'] == "priority_override"


class TestOwnershipEventPublishing:
    """Tests for ownership transfer event publishing"""

    def test_ownership_transferred_event(
        self,
        ownership_service,
        strategy_repo,
        ownership_repo,
        db_session,
        event_collector
    ):
        """Test OWNERSHIP_TRANSFERRED event is published when ownership is transferred"""
        # Arrange: Create two strategies
        strategy1 = strategy_repo.create(
            name="test_from_transfer",
            display_name="From Transfer Test",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        strategy2 = strategy_repo.create(
            name="test_to_transfer",
            display_name="To Transfer Test",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        db_session.commit()

        # Create initial ownership
        ownership_repo.create(
            strategy_id=strategy1.id,
            ticker="TEST_MSFT_TRANSFER",
            ownership_type="primary",
            reasoning="Initial holder"
        )
        db_session.commit()

        # Act: Transfer ownership
        result = ownership_service.transfer_ownership(
            ticker="TEST_MSFT_TRANSFER",
            from_strategy_id=strategy1.id,
            to_strategy_id=strategy2.id,
            reason="Upgrading to long-term hold"
        )

        # Assert: Check transfer result
        assert result['success'] is True

        # Assert: Check event was published
        assert len(event_collector[EventType.OWNERSHIP_TRANSFERRED]) == 1

        # Verify event data
        transfer_event = event_collector[EventType.OWNERSHIP_TRANSFERRED][0]
        assert transfer_event['ticker'] == "TEST_MSFT_TRANSFER"
        assert transfer_event['from_strategy_name'] == "test_from_transfer"
        assert transfer_event['to_strategy_name'] == "test_to_transfer"
        assert transfer_event['reason'] == "Upgrading to long-term hold"


class TestEventBusHistory:
    """Tests for Event Bus history and reconstruction"""

    def test_event_history_recording(
        self,
        conflict_detector,
        strategy_repo,
        ownership_repo,
        db_session
    ):
        """Test that events are recorded in Event Bus history"""
        # Arrange
        long_term = strategy_repo.create(
            name="test_history_lt",
            display_name="History Long Term",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        trading = strategy_repo.create(
            name="test_history_tr",
            display_name="History Trading",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        db_session.commit()

        ownership_repo.create(
            strategy_id=long_term.id,
            ticker="TEST_HISTORY",
            ownership_type="primary",
            reasoning="Test"
        )
        db_session.commit()

        # Act: Trigger conflict
        conflict_detector.check_conflict(
            strategy_id=trading.id,
            ticker="TEST_HISTORY",
            action=OrderAction.SELL,
            quantity=5
        )

        # Assert: Check event history contains our events
        history = event_bus.get_history(event_type=EventType.CONFLICT_DETECTED)

        # Filter for our test ticker
        test_events = [e for e in history if e['data'].get('ticker') == "TEST_HISTORY"]
        assert len(test_events) >= 1


# ====================================
# Run Tests
# ====================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
