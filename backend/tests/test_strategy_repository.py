"""
Unit Tests for Strategy Repositories - TDD RED State

Phase 0, Task T0.6

Test cases for repository pattern:
1. test_create_strategy: Create new strategy
2. test_get_active_strategies: Get only active strategies
3. test_update_strategy_priority: Update strategy priority
4. test_create_ownership: Create position ownership
5. test_get_primary_ownership: Get primary owner of a ticker
6. test_is_ticker_locked: Check if ticker is locked

Expected: SOME TESTS MAY PASS (Repository already implemented in T0.3)
Purpose: Validate repository implementation before integration

Run:
    pytest backend/tests/test_strategy_repository.py -v
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import models
from backend.database.models import Base, Strategy, PositionOwnership, ConflictLog

# Import repositories
from backend.database.repository_multi_strategy import (
    StrategyRepository,
    PositionOwnershipRepository,
    ConflictLogRepository
)

# Import mocks for comparison
from backend.tests.mocks.strategy_mocks import get_preset_strategies


@pytest.fixture(scope="function")
def test_db_session():
    """
    Create an in-memory SQLite database for testing

    Each test gets a fresh database instance

    Note: Only creates multi-strategy tables, not all Base tables
    (SQLite doesn't support PostgreSQL-specific types like ARRAY, Vector)
    """
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    # Create only the tables we need for multi-strategy tests
    # Avoid creating all tables (some have PostgreSQL-specific types)
    Strategy.__table__.create(bind=engine, checkfirst=True)
    PositionOwnership.__table__.create(bind=engine, checkfirst=True)
    ConflictLog.__table__.create(bind=engine, checkfirst=True)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Drop only our tables
        ConflictLog.__table__.drop(bind=engine, checkfirst=True)
        PositionOwnership.__table__.drop(bind=engine, checkfirst=True)
        Strategy.__table__.drop(bind=engine, checkfirst=True)


@pytest.fixture
def strategy_repo(test_db_session):
    """Create StrategyRepository instance"""
    return StrategyRepository(db=test_db_session)


@pytest.fixture
def ownership_repo(test_db_session):
    """Create PositionOwnershipRepository instance"""
    return PositionOwnershipRepository(db=test_db_session)


@pytest.fixture
def conflict_log_repo(test_db_session):
    """Create ConflictLogRepository instance"""
    return ConflictLogRepository(db=test_db_session)


class TestStrategyRepository:
    """
    Test suite for StrategyRepository

    Tests CRUD operations for Strategy model
    """

    def test_create_strategy(self, strategy_repo, test_db_session):
        """
        Test creating a new strategy

        Expected:
        - Strategy created with all fields
        - ID is auto-generated UUID
        - Timestamps are set
        """
        # Arrange
        strategy_data = {
            "name": "test_strategy",
            "display_name": "Test Strategy",
            "persona_type": "trading",
            "priority": 75,
            "time_horizon": "medium",
            "is_active": True,
            "config_metadata": {"test_param": 123}
        }

        # Act
        strategy = strategy_repo.create(**strategy_data)
        test_db_session.commit()

        # Assert
        assert strategy.id is not None, "ID should be auto-generated"
        assert strategy.name == "test_strategy"
        assert strategy.display_name == "Test Strategy"
        assert strategy.priority == 75
        assert strategy.config_metadata["test_param"] == 123
        assert strategy.created_at is not None
        assert strategy.updated_at is not None

    def test_get_active_strategies(self, strategy_repo, test_db_session):
        """
        Test getting only active strategies

        Expected:
        - Only strategies with is_active=True are returned
        - Inactive strategies are filtered out
        """
        # Arrange - Create 2 active, 1 inactive strategy
        strategy_repo.create(
            name="active_1",
            display_name="Active 1",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        strategy_repo.create(
            name="active_2",
            display_name="Active 2",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        strategy_repo.create(
            name="inactive_1",
            display_name="Inactive 1",
            persona_type="dividend",
            priority=90,
            time_horizon="long",
            is_active=False
        )
        test_db_session.commit()

        # Act
        active_strategies = strategy_repo.get_active_strategies()

        # Assert
        assert len(active_strategies) == 2, "Should return only active strategies"
        assert all(s.is_active for s in active_strategies), "All should be active"
        active_names = [s.name for s in active_strategies]
        assert "active_1" in active_names
        assert "active_2" in active_names
        assert "inactive_1" not in active_names

    def test_update_strategy_priority(self, strategy_repo, test_db_session):
        """
        Test updating strategy priority

        Expected:
        - Priority updated successfully
        - updated_at timestamp changed
        """
        # Arrange - Create strategy
        strategy = strategy_repo.create(
            name="priority_test",
            display_name="Priority Test",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        test_db_session.commit()
        original_updated_at = strategy.updated_at

        # Act - Update priority
        updated = strategy_repo.update(strategy.id, priority=80)
        test_db_session.commit()

        # Assert
        assert updated.priority == 80, "Priority should be updated"
        assert updated.updated_at > original_updated_at, "updated_at should change"

    def test_get_by_name(self, strategy_repo, test_db_session):
        """
        Test getting strategy by name

        Expected:
        - Strategy found by unique name
        - None returned for non-existent name
        """
        # Arrange
        strategy_repo.create(
            name="findme",
            display_name="Find Me",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        test_db_session.commit()

        # Act
        found = strategy_repo.get_by_name("findme")
        not_found = strategy_repo.get_by_name("doesnotexist")

        # Assert
        assert found is not None, "Strategy should be found"
        assert found.name == "findme"
        assert not_found is None, "Non-existent strategy should return None"

    def test_delete_strategy(self, strategy_repo, test_db_session):
        """
        Test deleting a strategy

        Expected:
        - Strategy deleted successfully
        - get_by_id returns None after deletion
        """
        # Arrange
        strategy = strategy_repo.create(
            name="deleteme",
            display_name="Delete Me",
            persona_type="aggressive",
            priority=30,
            time_horizon="short",
            is_active=True
        )
        test_db_session.commit()
        strategy_id = strategy.id

        # Act
        success = strategy_repo.delete(strategy_id)
        test_db_session.commit()

        # Assert
        assert success is True, "Delete should succeed"
        assert strategy_repo.get_by_id(strategy_id) is None, "Strategy should be gone"

    def test_get_active_strategies_by_priority(self, strategy_repo, test_db_session):
        """
        Test getting active strategies sorted by priority (DESC)

        Expected:
        - Strategies returned in priority order (highest first)
        - Only active strategies included

        This is critical for conflict detection hot path
        """
        # Arrange - Create strategies with different priorities
        strategy_repo.create(
            name="low_priority",
            display_name="Low Priority",
            persona_type="aggressive",
            priority=30,
            time_horizon="short",
            is_active=True
        )
        strategy_repo.create(
            name="high_priority",
            display_name="High Priority",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        strategy_repo.create(
            name="medium_priority",
            display_name="Medium Priority",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        strategy_repo.create(
            name="inactive_highest",
            display_name="Inactive Highest",
            persona_type="dividend",
            priority=150,
            time_horizon="long",
            is_active=False
        )
        test_db_session.commit()

        # Act
        strategies = strategy_repo.get_active_strategies_by_priority()

        # Assert
        assert len(strategies) == 3, "Should return 3 active strategies"
        priorities = [s.priority for s in strategies]
        assert priorities == [100, 50, 30], "Should be sorted DESC by priority"
        assert "inactive_highest" not in [s.name for s in strategies], "Inactive excluded"


class TestPositionOwnershipRepository:
    """
    Test suite for PositionOwnershipRepository

    Tests ownership tracking and conflict detection support
    """

    def test_create_ownership(self, ownership_repo, strategy_repo, test_db_session):
        """
        Test creating position ownership

        Expected:
        - Ownership created with strategy reference
        - Ticker is uppercase
        """
        # Arrange - Create strategy first
        strategy = strategy_repo.create(
            name="owner",
            display_name="Owner",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        test_db_session.commit()

        # Act
        ownership = ownership_repo.create(
            strategy_id=strategy.id,
            ticker="aapl",  # lowercase - should be converted
            ownership_type="primary",
            reasoning="Test ownership"
        )
        test_db_session.commit()

        # Assert
        assert ownership.id is not None
        assert ownership.ticker == "AAPL", "Ticker should be uppercase"
        assert ownership.strategy_id == strategy.id
        assert ownership.ownership_type == "primary"
        assert ownership.created_at is not None

    def test_get_primary_ownership(self, ownership_repo, strategy_repo, test_db_session):
        """
        Test getting primary owner of a ticker

        Expected:
        - Returns ownership with type='primary'
        - None if no primary ownership exists
        """
        # Arrange
        strategy = strategy_repo.create(
            name="primary_owner",
            display_name="Primary Owner",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        test_db_session.commit()

        ownership_repo.create(
            strategy_id=strategy.id,
            ticker="TSLA",
            ownership_type="primary",
            reasoning="Primary holder"
        )
        test_db_session.commit()

        # Act
        primary = ownership_repo.get_primary_ownership("TSLA")
        no_owner = ownership_repo.get_primary_ownership("GOOGL")

        # Assert
        assert primary is not None, "Should find primary ownership"
        assert primary.ticker == "TSLA"
        assert primary.ownership_type == "primary"
        assert no_owner is None, "Should return None for unowned ticker"

    def test_is_ticker_locked(self, ownership_repo, strategy_repo, test_db_session):
        """
        Test checking if ticker is locked

        Expected:
        - True if primary ownership exists with locked_until > now
        - False if no lock or lock expired
        """
        # Arrange
        strategy = strategy_repo.create(
            name="locker",
            display_name="Locker",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        test_db_session.commit()

        # Create locked ownership
        ownership_repo.create(
            strategy_id=strategy.id,
            ticker="NVDA",
            ownership_type="primary",
            locked_until=datetime.now() + timedelta(days=30),
            reasoning="Long-term lock"
        )

        # Create expired lock
        ownership_repo.create(
            strategy_id=strategy.id,
            ticker="AMD",
            ownership_type="primary",
            locked_until=datetime.now() - timedelta(days=1),  # Expired yesterday
            reasoning="Expired lock"
        )

        # Create unlocked ownership
        ownership_repo.create(
            strategy_id=strategy.id,
            ticker="INTC",
            ownership_type="primary",
            locked_until=None,
            reasoning="Unlocked"
        )
        test_db_session.commit()

        # Act
        nvda_locked = ownership_repo.is_ticker_locked("NVDA")
        amd_locked = ownership_repo.is_ticker_locked("AMD")
        intc_locked = ownership_repo.is_ticker_locked("INTC")
        no_ownership_locked = ownership_repo.is_ticker_locked("FB")

        # Assert
        assert nvda_locked is True, "NVDA should be locked"
        assert amd_locked is False, "AMD lock expired"
        assert intc_locked is False, "INTC has no lock"
        assert no_ownership_locked is False, "No ownership means not locked"

    def test_get_strategy_ownerships(self, ownership_repo, strategy_repo, test_db_session):
        """
        Test getting all ownerships for a strategy

        Expected:
        - Returns all ownerships belonging to the strategy
        - Empty list if strategy has no ownerships
        """
        # Arrange
        strategy1 = strategy_repo.create(
            name="owner1",
            display_name="Owner 1",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        strategy2 = strategy_repo.create(
            name="owner2",
            display_name="Owner 2",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        test_db_session.commit()

        # Create ownerships
        ownership_repo.create(strategy_id=strategy1.id, ticker="AAPL", ownership_type="primary")
        ownership_repo.create(strategy_id=strategy1.id, ticker="TSLA", ownership_type="primary")
        ownership_repo.create(strategy_id=strategy2.id, ticker="GOOGL", ownership_type="primary")
        test_db_session.commit()

        # Act
        strategy1_ownerships = ownership_repo.get_strategy_ownerships(strategy1.id)
        strategy2_ownerships = ownership_repo.get_strategy_ownerships(strategy2.id)

        # Assert
        assert len(strategy1_ownerships) == 2, "Strategy1 should own 2 tickers"
        assert len(strategy2_ownerships) == 1, "Strategy2 should own 1 ticker"
        strategy1_tickers = [o.ticker for o in strategy1_ownerships]
        assert "AAPL" in strategy1_tickers
        assert "TSLA" in strategy1_tickers

    def test_transfer_ownership(self, ownership_repo, strategy_repo, test_db_session):
        """
        Test transferring ownership from one strategy to another

        Expected:
        - Old ownership deleted
        - New ownership created
        - Atomic operation
        """
        # Arrange
        strategy1 = strategy_repo.create(
            name="from_strategy",
            display_name="From Strategy",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        strategy2 = strategy_repo.create(
            name="to_strategy",
            display_name="To Strategy",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        test_db_session.commit()

        # Create initial ownership
        ownership_repo.create(
            strategy_id=strategy1.id,
            ticker="MSFT",
            ownership_type="primary",
            reasoning="Initial holder"
        )
        test_db_session.commit()

        # Act
        success = ownership_repo.transfer_ownership(
            ticker="MSFT",
            from_strategy_id=strategy1.id,
            to_strategy_id=strategy2.id,
            reasoning="Upgrading to long-term"
        )
        test_db_session.commit()

        # Assert
        assert success is True, "Transfer should succeed"

        # Verify new ownership
        new_ownership = ownership_repo.get_primary_ownership("MSFT")
        assert new_ownership is not None
        assert new_ownership.strategy_id == strategy2.id, "Should be owned by strategy2"
        assert "Upgrading to long-term" in new_ownership.reasoning


class TestConflictLogRepository:
    """
    Test suite for ConflictLogRepository

    Tests conflict audit log creation and retrieval
    """

    def test_create_conflict_log(self, conflict_log_repo, strategy_repo, test_db_session):
        """
        Test creating a conflict log entry

        Expected:
        - Log created with all fields
        - Insert-only pattern (no updates)
        """
        # Arrange
        strategy1 = strategy_repo.create(
            name="conflicting",
            display_name="Conflicting",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        strategy2 = strategy_repo.create(
            name="owning",
            display_name="Owning",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        test_db_session.commit()

        # Act
        log = conflict_log_repo.create(
            ticker="AAPL",
            action_attempted="sell",
            action_blocked=True,
            resolution="blocked",
            reasoning="Trading strategy blocked by Long-term (priority 100 > 50)",
            conflicting_strategy_id=strategy1.id,
            owning_strategy_id=strategy2.id,
            conflicting_strategy_priority=50,
            owning_strategy_priority=100
        )
        test_db_session.commit()

        # Assert
        assert log.id is not None
        assert log.ticker == "AAPL"
        assert log.action_attempted == "sell"
        assert log.action_blocked is True
        assert log.resolution == "blocked"
        assert log.conflicting_strategy_id == strategy1.id
        assert log.owning_strategy_id == strategy2.id
        assert log.created_at is not None

    def test_get_logs_by_ticker(self, conflict_log_repo, strategy_repo, test_db_session):
        """
        Test getting conflict logs for a specific ticker

        Expected:
        - Returns all logs for the ticker
        - Sorted by created_at DESC (most recent first)
        """
        # Arrange
        strategy = strategy_repo.create(
            name="test",
            display_name="Test",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        test_db_session.commit()

        # Create multiple logs
        conflict_log_repo.create(
            ticker="AAPL",
            action_attempted="sell",
            action_blocked=True,
            resolution="blocked",
            reasoning="Test 1",
            conflicting_strategy_id=strategy.id,
            owning_strategy_id=strategy.id
        )
        conflict_log_repo.create(
            ticker="AAPL",
            action_attempted="buy",
            action_blocked=False,
            resolution="allowed",
            reasoning="Test 2",
            conflicting_strategy_id=strategy.id,
            owning_strategy_id=strategy.id
        )
        conflict_log_repo.create(
            ticker="TSLA",
            action_attempted="sell",
            action_blocked=True,
            resolution="blocked",
            reasoning="Test 3",
            conflicting_strategy_id=strategy.id,
            owning_strategy_id=strategy.id
        )
        test_db_session.commit()

        # Act
        aapl_logs = conflict_log_repo.get_logs_by_ticker("AAPL")

        # Assert
        assert len(aapl_logs) == 2, "Should find 2 logs for AAPL"
        assert all(log.ticker == "AAPL" for log in aapl_logs)
        assert aapl_logs[0].created_at >= aapl_logs[1].created_at, "Should be sorted DESC"

    def test_get_logs_by_date_range(self, conflict_log_repo, strategy_repo, test_db_session):
        """
        Test getting conflict logs within a date range

        Expected:
        - Returns logs within specified range
        - Excludes logs outside the range
        """
        # Arrange
        strategy = strategy_repo.create(
            name="test",
            display_name="Test",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        test_db_session.commit()

        # Create logs
        conflict_log_repo.create(
            ticker="AAPL",
            action_attempted="sell",
            action_blocked=True,
            resolution="blocked",
            reasoning="Test log",
            conflicting_strategy_id=strategy.id,
            owning_strategy_id=strategy.id
        )
        test_db_session.commit()

        # Act
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        logs_in_range = conflict_log_repo.get_logs_by_date_range(start_date=yesterday, end_date=tomorrow)
        logs_out_of_range = conflict_log_repo.get_logs_by_date_range(start_date=yesterday - timedelta(days=10), end_date=yesterday)

        # Assert
        assert len(logs_in_range) > 0, "Should find logs in range"
        assert len(logs_out_of_range) == 0, "Should not find logs out of range"


# ====================================
# Run Tests
# ====================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
