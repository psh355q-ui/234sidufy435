"""
Unit Tests for ConflictDetector - TDD RED State

Phase 0, Task T0.6

Test cases for multi-strategy conflict detection:
1. test_detect_conflict_long_term_vs_trading: Long-term owns, Trading tries to sell → BLOCKED
2. test_detect_conflict_same_strategy: Same strategy owns and acts → ALLOWED
3. test_priority_based_resolution: Higher priority strategy can override → PRIORITY_OVERRIDE
4. test_ownership_transfer: Ownership transfer logic

Expected: ALL TESTS SHOULD FAIL (RED state)
Reason: ConflictDetector class not yet implemented (Phase 1, T1.1)

Run:
    pytest backend/tests/test_conflict_detector.py -v
    # Expected: 4 FAILED
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

# Import mocks
from backend.tests.mocks.strategy_mocks import (
    create_mock_strategy,
    create_mock_ownership,
    get_preset_strategies,
    create_conflict_scenario_long_vs_trading,
    create_conflict_scenario_same_strategy,
    create_conflict_scenario_priority_override
)

# TODO: Import ConflictDetector (not yet implemented)
# from backend.services.conflict_detector import ConflictDetector


class TestConflictDetector:
    """
    Test suite for ConflictDetector class

    ConflictDetector should:
    - Check if a strategy can perform an action on a ticker
    - Resolve conflicts based on priority rules
    - Create conflict logs for audit
    """

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return MagicMock()

    @pytest.fixture
    def conflict_detector(self, mock_db_session):
        """
        Create ConflictDetector instance with mocked dependencies

        TODO: Uncomment when ConflictDetector is implemented
        """
        # return ConflictDetector(db=mock_db_session)
        pytest.skip("ConflictDetector not yet implemented (Phase 1, T1.1)")

    def test_detect_conflict_long_term_vs_trading(self, conflict_detector):
        """
        Test Scenario 1: Long-term strategy owns AAPL, Trading strategy tries to sell

        Expected:
        - has_conflict: True
        - resolution: BLOCKED
        - can_proceed: False
        - reasoning: "Trading strategy (priority=50) cannot override Long-term (priority=100)"

        Business Rule:
        - Long-term priority (100) > Trading priority (50)
        - Lower priority strategy CANNOT sell positions owned by higher priority
        """
        # Arrange
        long_term, trading, ownership = create_conflict_scenario_long_vs_trading()

        # Mock repository responses
        conflict_detector.ownership_repo.get_primary_ownership = Mock(return_value=ownership)
        conflict_detector.strategy_repo.get_by_id = Mock(side_effect=lambda id:
            long_term if id == long_term.id else trading
        )

        # Act
        result = conflict_detector.check_conflict(
            strategy_id=trading.id,
            ticker="AAPL",
            action="sell",
            quantity=10
        )

        # Assert
        assert result["has_conflict"] is True, "Conflict should be detected"
        assert result["resolution"] == "blocked", "Lower priority should be blocked"
        assert result["can_proceed"] is False, "Trading cannot proceed"
        assert "priority" in result["reasoning"].lower(), "Reasoning should mention priority"
        assert result["conflict_detail"]["owning_strategy_id"] == long_term.id
        assert result["conflict_detail"]["owning_strategy_priority"] == 100

    def test_detect_conflict_same_strategy(self, conflict_detector):
        """
        Test Scenario 2: Same strategy owns and attempts action

        Expected:
        - has_conflict: False
        - resolution: ALLOWED
        - can_proceed: True
        - reasoning: "Same strategy owns the position"

        Business Rule:
        - A strategy can always modify its own positions
        """
        # Arrange
        trading, ownership = create_conflict_scenario_same_strategy()

        # Mock repository responses
        conflict_detector.ownership_repo.get_primary_ownership = Mock(return_value=ownership)
        conflict_detector.strategy_repo.get_by_id = Mock(return_value=trading)

        # Act
        result = conflict_detector.check_conflict(
            strategy_id=trading.id,
            ticker="TSLA",
            action="sell",
            quantity=5
        )

        # Assert
        assert result["has_conflict"] is False, "No conflict for same strategy"
        assert result["resolution"] == "allowed", "Should be allowed"
        assert result["can_proceed"] is True, "Trading can proceed"
        assert "same strategy" in result["reasoning"].lower(), "Reasoning should mention same strategy"
        assert result["conflict_detail"] is None, "No conflict detail needed"

    def test_priority_based_resolution(self, conflict_detector):
        """
        Test Scenario 3: Higher priority strategy overrides lower priority

        Scenario A: Long-term (100) tries to buy NVDA owned by Trading (50)
        Expected: PRIORITY_OVERRIDE, can_proceed=True

        Scenario B: Trading (50) tries to sell NVDA owned by Long-term (100)
        Expected: BLOCKED, can_proceed=False

        Business Rule:
        - Higher priority strategy CAN override lower priority
        - Lower priority strategy CANNOT override higher priority
        """
        # Arrange
        trading, long_term, trading_ownership = create_conflict_scenario_priority_override()

        # Scenario A: Long-term overrides Trading
        conflict_detector.ownership_repo.get_primary_ownership = Mock(return_value=trading_ownership)
        conflict_detector.strategy_repo.get_by_id = Mock(side_effect=lambda id:
            long_term if id == long_term.id else trading
        )

        # Act
        result_override = conflict_detector.check_conflict(
            strategy_id=long_term.id,
            ticker="NVDA",
            action="buy",
            quantity=20
        )

        # Assert - Scenario A
        assert result_override["has_conflict"] is True, "Conflict detected (different owner)"
        assert result_override["resolution"] == "priority_override", "Higher priority can override"
        assert result_override["can_proceed"] is True, "Long-term can proceed"
        assert "priority" in result_override["reasoning"].lower()

        # Scenario B: Trading blocked by Long-term (reverse scenario)
        long_term_ownership = create_mock_ownership(
            ticker="MSFT",
            strategy_id=long_term.id,
            ownership_type="primary",
            strategy=long_term
        )
        conflict_detector.ownership_repo.get_primary_ownership = Mock(return_value=long_term_ownership)

        # Act
        result_blocked = conflict_detector.check_conflict(
            strategy_id=trading.id,
            ticker="MSFT",
            action="sell",
            quantity=10
        )

        # Assert - Scenario B
        assert result_blocked["has_conflict"] is True
        assert result_blocked["resolution"] == "blocked", "Lower priority blocked"
        assert result_blocked["can_proceed"] is False, "Trading cannot proceed"

    def test_ownership_transfer(self, conflict_detector):
        """
        Test Scenario 4: Ownership transfer from one strategy to another

        Expected:
        - Old ownership deleted
        - New ownership created
        - Atomic transaction (both succeed or both fail)

        Business Rule:
        - Only unlocked positions can be transferred
        - Transfer should be atomic (transaction)
        """
        # Arrange
        strategies = get_preset_strategies()
        trading = strategies["trading"]
        long_term = strategies["long_term"]

        trading_ownership = create_mock_ownership(
            ticker="GOOGL",
            strategy_id=trading.id,
            ownership_type="primary",
            locked_until=None,  # Unlocked
            strategy=trading
        )

        # Mock repository methods
        conflict_detector.ownership_repo.get_primary_ownership = Mock(return_value=trading_ownership)
        conflict_detector.ownership_repo.transfer_ownership = Mock(return_value=True)
        conflict_detector.ownership_repo.is_ticker_locked = Mock(return_value=False)

        # Act
        success = conflict_detector.transfer_ownership(
            ticker="GOOGL",
            from_strategy_id=trading.id,
            to_strategy_id=long_term.id,
            reasoning="Upgrading to long-term hold"
        )

        # Assert
        assert success is True, "Transfer should succeed for unlocked position"
        conflict_detector.ownership_repo.transfer_ownership.assert_called_once()

    def test_locked_position_cannot_be_sold(self, conflict_detector):
        """
        Test Scenario 5: Locked position cannot be sold by other strategies

        Expected:
        - has_conflict: True
        - resolution: BLOCKED
        - reasoning: Should mention "locked"

        Business Rule:
        - Positions with locked_until > now cannot be sold by other strategies
        """
        # Arrange
        strategies = get_preset_strategies()
        long_term = strategies["long_term"]
        trading = strategies["trading"]

        locked_ownership = create_mock_ownership(
            ticker="AMZN",
            strategy_id=long_term.id,
            ownership_type="primary",
            locked_until=datetime.now() + timedelta(days=60),  # Locked for 60 days
            reasoning="Long-term conviction hold",
            strategy=long_term
        )

        # Mock repository responses
        conflict_detector.ownership_repo.get_primary_ownership = Mock(return_value=locked_ownership)
        conflict_detector.ownership_repo.is_ticker_locked = Mock(return_value=True)
        conflict_detector.strategy_repo.get_by_id = Mock(side_effect=lambda id:
            long_term if id == long_term.id else trading
        )

        # Act
        result = conflict_detector.check_conflict(
            strategy_id=trading.id,
            ticker="AMZN",
            action="sell",
            quantity=5
        )

        # Assert
        assert result["has_conflict"] is True, "Conflict should be detected for locked position"
        assert result["can_proceed"] is False, "Cannot sell locked position"
        assert "locked" in result["reasoning"].lower(), "Reasoning should mention lock"

    def test_no_ownership_allows_any_strategy(self, conflict_detector):
        """
        Test Scenario 6: No existing ownership allows any strategy to buy

        Expected:
        - has_conflict: False
        - resolution: ALLOWED
        - can_proceed: True

        Business Rule:
        - If no one owns the ticker, any strategy can buy
        """
        # Arrange
        strategies = get_preset_strategies()
        trading = strategies["trading"]

        # Mock repository: No ownership found
        conflict_detector.ownership_repo.get_primary_ownership = Mock(return_value=None)
        conflict_detector.strategy_repo.get_by_id = Mock(return_value=trading)

        # Act
        result = conflict_detector.check_conflict(
            strategy_id=trading.id,
            ticker="FB",
            action="buy",
            quantity=10
        )

        # Assert
        assert result["has_conflict"] is False, "No conflict for unowned ticker"
        assert result["resolution"] == "allowed", "Should be allowed"
        assert result["can_proceed"] is True, "Trading can proceed"
        assert "no ownership" in result["reasoning"].lower() or "unowned" in result["reasoning"].lower()

    def test_conflict_log_creation(self, conflict_detector):
        """
        Test Scenario 7: Conflict logs are created for blocked actions

        Expected:
        - ConflictLog created when action is blocked
        - Log contains all relevant information

        Business Rule:
        - Every conflict (blocked or override) should be logged for audit
        """
        # Arrange
        long_term, trading, ownership = create_conflict_scenario_long_vs_trading()

        # Mock repository responses
        conflict_detector.ownership_repo.get_primary_ownership = Mock(return_value=ownership)
        conflict_detector.strategy_repo.get_by_id = Mock(side_effect=lambda id:
            long_term if id == long_term.id else trading
        )
        conflict_detector.conflict_log_repo.create = Mock()

        # Act
        result = conflict_detector.check_conflict(
            strategy_id=trading.id,
            ticker="AAPL",
            action="sell",
            quantity=10,
            create_log=True  # Explicitly request log creation
        )

        # Assert
        assert result["can_proceed"] is False, "Trading should be blocked"
        conflict_detector.conflict_log_repo.create.assert_called_once()

        # Verify log content
        log_call_args = conflict_detector.conflict_log_repo.create.call_args[1]
        assert log_call_args["ticker"] == "AAPL"
        assert log_call_args["action_attempted"] == "sell"
        assert log_call_args["action_blocked"] is True
        assert log_call_args["resolution"] == "blocked"
        assert log_call_args["conflicting_strategy_id"] == trading.id
        assert log_call_args["owning_strategy_id"] == long_term.id


# ====================================
# Run Tests (Expected to FAIL - RED state)
# ====================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
