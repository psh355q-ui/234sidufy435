"""
Integration Tests for Strategy Repositories with Real PostgreSQL

Phase 1, Task T1.1 - TDD RED→GREEN

Tests repository implementation against actual PostgreSQL database.
Uses settings.DATABASE_URL for connection.

Prerequisites:
    - PostgreSQL running (docker compose up -d db)
    - Tables created (migrations applied)

Run:
    pytest backend/tests/integration/test_strategy_repository_integration.py -v
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Import database setup
from backend.database.repository import get_sync_session
from backend.database.models import Strategy, PositionOwnership, ConflictLog

# Import repositories
from backend.database.repository_multi_strategy import (
    StrategyRepository,
    PositionOwnershipRepository,
    ConflictLogRepository
)


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
        # Order matters due to foreign keys
        db.query(ConflictLog).filter(ConflictLog.ticker.like("TEST_%")).delete()
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
def conflict_log_repo(db_session):
    """Create ConflictLogRepository instance"""
    return ConflictLogRepository(session=db_session)


class TestStrategyRepositoryIntegration:
    """Integration tests for StrategyRepository with real PostgreSQL"""

    def test_create_strategy(self, strategy_repo, db_session):
        """Test creating a new strategy"""
        # Arrange
        strategy_data = {
            "name": "test_integration",
            "display_name": "Integration Test Strategy",
            "persona_type": "trading",
            "priority": 75,
            "time_horizon": "medium",
            "is_active": True,
            "config_metadata": {"test_param": 123}
        }

        # Act
        strategy = strategy_repo.create(**strategy_data)
        db_session.commit()

        # Assert
        assert strategy.id is not None
        assert strategy.name == "test_integration"
        assert strategy.priority == 75
        assert strategy.config_metadata["test_param"] == 123

        # Verify in database
        found = strategy_repo.get_by_name("test_integration")
        assert found is not None
        assert found.id == strategy.id

    def test_get_active_strategies(self, strategy_repo, db_session):
        """Test getting only active strategies"""
        # Arrange - Create test strategies
        strategy_repo.create(
            name="test_active_1",
            display_name="Active 1",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        strategy_repo.create(
            name="test_inactive_1",
            display_name="Inactive 1",
            persona_type="dividend",
            priority=90,
            time_horizon="long",
            is_active=False
        )
        db_session.commit()

        # Act
        active_strategies = strategy_repo.get_active_strategies()

        # Assert
        test_active = [s for s in active_strategies if s.name.startswith("test_")]
        assert len(test_active) >= 1
        assert all(s.is_active for s in test_active)

    def test_update_strategy_priority(self, strategy_repo, db_session):
        """Test updating strategy priority"""
        # Arrange
        strategy = strategy_repo.create(
            name="test_priority",
            display_name="Priority Test",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        db_session.commit()

        # Act
        updated = strategy_repo.update(strategy.id, priority=80)
        db_session.commit()

        # Assert
        assert updated.priority == 80

    def test_create_ownership(self, ownership_repo, strategy_repo, db_session):
        """Test creating position ownership"""
        # Arrange - Create strategy first
        strategy = strategy_repo.create(
            name="test_owner",
            display_name="Owner",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        db_session.commit()

        # Act
        ownership = ownership_repo.create(
            strategy_id=strategy.id,
            ticker="TEST_AAPL",
            ownership_type="primary",
            reasoning="Test ownership"
        )
        db_session.commit()

        # Assert
        assert ownership.id is not None
        assert ownership.ticker == "TEST_AAPL"
        assert ownership.strategy_id == strategy.id

    def test_get_primary_ownership(self, ownership_repo, strategy_repo, db_session):
        """Test getting primary owner of a ticker"""
        # Arrange
        strategy = strategy_repo.create(
            name="test_primary_owner",
            display_name="Primary Owner",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        db_session.commit()

        ownership_repo.create(
            strategy_id=strategy.id,
            ticker="TEST_TSLA",
            ownership_type="primary",
            reasoning="Primary holder"
        )
        db_session.commit()

        # Act
        primary = ownership_repo.get_primary_ownership("TEST_TSLA")

        # Assert
        assert primary is not None
        assert primary.ticker == "TEST_TSLA"
        assert primary.ownership_type == "primary"

    def test_is_ticker_locked(self, ownership_repo, strategy_repo, db_session):
        """Test checking if ticker is locked"""
        # Arrange
        strategy = strategy_repo.create(
            name="test_locker",
            display_name="Locker",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        db_session.commit()

        # Create locked ownership
        ownership_repo.create(
            strategy_id=strategy.id,
            ticker="TEST_NVDA",
            ownership_type="primary",
            locked_until=datetime.now() + timedelta(days=30),
            reasoning="Long-term lock"
        )
        db_session.commit()

        # Act
        is_locked = ownership_repo.is_ticker_locked("TEST_NVDA")

        # Assert
        assert is_locked is True

    def test_create_conflict_log(self, conflict_log_repo, strategy_repo, db_session):
        """Test creating a conflict log entry"""
        # Arrange
        strategy1 = strategy_repo.create(
            name="test_conflicting",
            display_name="Conflicting",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        strategy2 = strategy_repo.create(
            name="test_owning",
            display_name="Owning",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        db_session.commit()

        # Act
        log = conflict_log_repo.create(
            ticker="TEST_AAPL",
            action_attempted="sell",
            action_blocked=True,
            resolution="blocked",
            reasoning="Trading strategy blocked by Long-term (priority 100 > 50)",
            conflicting_strategy_id=strategy1.id,
            owning_strategy_id=strategy2.id,
            conflicting_strategy_priority=50,
            owning_strategy_priority=100
        )
        db_session.commit()

        # Assert
        assert log.id is not None
        assert log.ticker == "TEST_AAPL"
        assert log.action_blocked is True

    def test_seed_strategies_exist(self, strategy_repo):
        """Test that seed strategies were created by migration"""
        # Act
        long_term = strategy_repo.get_by_name("long_term")
        dividend = strategy_repo.get_by_name("dividend")
        trading = strategy_repo.get_by_name("trading")
        aggressive = strategy_repo.get_by_name("aggressive")

        # Assert
        assert long_term is not None
        assert long_term.priority == 100
        assert dividend is not None
        assert dividend.priority == 90
        assert trading is not None
        assert trading.priority == 50
        assert aggressive is not None
        assert aggressive.priority == 30


class TestPositionOwnershipRepositoryIntegration:
    """Integration tests for PositionOwnershipRepository"""

    def test_transfer_ownership(self, ownership_repo, strategy_repo, db_session):
        """Test transferring ownership from one strategy to another"""
        # Arrange
        strategy1 = strategy_repo.create(
            name="test_from_strategy",
            display_name="From Strategy",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        strategy2 = strategy_repo.create(
            name="test_to_strategy",
            display_name="To Strategy",
            persona_type="long_term",
            priority=100,
            time_horizon="long",
            is_active=True
        )
        db_session.commit()

        # Create initial ownership
        ownership_repo.create(
            strategy_id=strategy1.id,
            ticker="TEST_MSFT",
            ownership_type="primary",
            reasoning="Initial holder"
        )
        db_session.commit()

        # Act
        success = ownership_repo.transfer_ownership(
            ticker="TEST_MSFT",
            from_strategy_id=strategy1.id,
            to_strategy_id=strategy2.id,
            reasoning="Upgrading to long-term"
        )
        db_session.commit()

        # Assert
        assert success is True

        # Verify new ownership
        new_ownership = ownership_repo.get_primary_ownership("TEST_MSFT")
        assert new_ownership is not None
        assert new_ownership.strategy_id == strategy2.id


class TestConflictLogRepositoryIntegration:
    """Integration tests for ConflictLogRepository"""

    def test_get_logs_by_ticker(self, conflict_log_repo, strategy_repo, db_session):
        """Test getting conflict logs for a specific ticker"""
        # Arrange
        strategy = strategy_repo.create(
            name="test_logger",
            display_name="Logger",
            persona_type="trading",
            priority=50,
            time_horizon="short",
            is_active=True
        )
        db_session.commit()

        # Create logs
        conflict_log_repo.create(
            ticker="TEST_LOG_AAPL",
            action_attempted="sell",
            action_blocked=True,
            resolution="blocked",
            reasoning="Test 1",
            conflicting_strategy_id=strategy.id,
            owning_strategy_id=strategy.id
        )
        conflict_log_repo.create(
            ticker="TEST_LOG_AAPL",
            action_attempted="buy",
            action_blocked=False,
            resolution="allowed",
            reasoning="Test 2",
            conflicting_strategy_id=strategy.id,
            owning_strategy_id=strategy.id
        )
        db_session.commit()

        # Act
        logs = conflict_log_repo.get_logs_by_ticker("TEST_LOG_AAPL")

        # Assert
        assert len(logs) == 2
        assert all(log.ticker == "TEST_LOG_AAPL" for log in logs)


# ====================================
# Run Tests
# ====================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
