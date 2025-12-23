"""
Agent Weight Manager

Phase 25.4: Self-Learning Feedback Loop
Date: 2025-12-23

Automatically adjusts agent weights based on their 24-hour performance tracking.
"""

import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy import text

logger = logging.getLogger(__name__)


class AgentWeightManager:
    """
    Manages agent voting weights based on performance metrics

    Weight Calculation Logic:
        - Accuracy >= 70%: weight = 1.2 (strong performer)
        - Accuracy >= 60%: weight = 1.0 (good performer)
        - Accuracy >= 50%: weight = 0.8 (weak performer)
        - Accuracy < 50%:  weight = 0.5 (poor performer)

    Confidence Gap Penalty:
        - If confidence >> accuracy: reduce weight (overconfident)
        - If confidence << accuracy: increase weight (underconfident)
    """

    # Weight thresholds
    ACCURACY_THRESHOLDS = {
        "strong": 0.70,    # >= 70%
        "good": 0.60,      # >= 60%
        "weak": 0.50,      # >= 50%
    }

    WEIGHT_VALUES = {
        "strong": 1.2,
        "good": 1.0,
        "weak": 0.8,
        "poor": 0.5,
    }

    # Minimum samples required for weight calculation
    MIN_SAMPLES = 20

    # Confidence gap threshold (overconfident/underconfident)
    CONFIDENCE_GAP_THRESHOLD = 0.15  # 15%

    def __init__(self, db):
        """
        Initialize Agent Weight Manager

        Args:
            db: Database session
        """
        self.db = db
        self.current_weights = self._load_default_weights()

    def _load_default_weights(self) -> Dict[str, float]:
        """Load default equal weights for all agents"""
        return {
            "trader": 1.0,
            "analyst": 1.0,
            "risk": 1.0,
            "macro": 1.0,
            "institutional": 1.0,
            "news": 1.0,
        }

    def calculate_agent_weights(self, lookback_days: int = 30) -> Dict[str, Dict]:
        """
        Calculate new weights for all agents based on recent performance

        Args:
            lookback_days: Number of days to look back for performance data

        Returns:
            Dictionary with agent names as keys and weight info as values:
            {
                "trader": {
                    "weight": 1.2,
                    "accuracy": 0.72,
                    "total_votes": 50,
                    "confidence_gap": 0.05,
                    "reason": "strong performer"
                }
            }
        """
        logger.info(f"🔄 Calculating agent weights (lookback: {lookback_days} days)")

        weights_info = {}

        # Get performance for each agent
        query = text("""
            SELECT
                agent_name,
                COUNT(*) as total_votes,
                AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as accuracy,
                AVG(vote_confidence) as avg_confidence,
                AVG(performance_score) as avg_performance_score
            FROM agent_vote_tracking
            WHERE status = 'COMPLETED'
                AND evaluated_at >= NOW() - INTERVAL ':lookback_days days'
            GROUP BY agent_name
        """)

        results = self.db.execute(query, {"lookback_days": lookback_days}).fetchall()

        for row in results:
            agent_name = row.agent_name
            total_votes = row.total_votes
            accuracy = float(row.accuracy) if row.accuracy else 0.0
            avg_confidence = float(row.avg_confidence) if row.avg_confidence else 0.5

            # Skip if insufficient data
            if total_votes < self.MIN_SAMPLES:
                weights_info[agent_name] = {
                    "weight": 1.0,
                    "accuracy": accuracy,
                    "total_votes": total_votes,
                    "confidence_gap": 0.0,
                    "reason": f"insufficient_data (need {self.MIN_SAMPLES})"
                }
                logger.warning(f"⚠️ {agent_name}: Insufficient data ({total_votes}/{self.MIN_SAMPLES})")
                continue

            # Calculate base weight from accuracy
            base_weight, reason = self._calculate_base_weight(accuracy)

            # Calculate confidence gap
            confidence_gap = avg_confidence - accuracy

            # Apply confidence gap adjustment
            final_weight = self._apply_confidence_adjustment(
                base_weight, confidence_gap
            )

            weights_info[agent_name] = {
                "weight": final_weight,
                "accuracy": accuracy,
                "total_votes": total_votes,
                "confidence_gap": confidence_gap,
                "reason": reason
            }

            logger.info(
                f"✅ {agent_name}: weight={final_weight:.2f}, "
                f"accuracy={accuracy:.1%}, votes={total_votes}, "
                f"gap={confidence_gap:+.1%}, reason={reason}"
            )

        # Update current weights
        for agent_name, info in weights_info.items():
            self.current_weights[agent_name] = info["weight"]

        return weights_info

    def _calculate_base_weight(self, accuracy: float) -> Tuple[float, str]:
        """
        Calculate base weight from accuracy

        Args:
            accuracy: Agent accuracy (0.0 to 1.0)

        Returns:
            (weight, reason) tuple
        """
        if accuracy >= self.ACCURACY_THRESHOLDS["strong"]:
            return self.WEIGHT_VALUES["strong"], "strong_performer"
        elif accuracy >= self.ACCURACY_THRESHOLDS["good"]:
            return self.WEIGHT_VALUES["good"], "good_performer"
        elif accuracy >= self.ACCURACY_THRESHOLDS["weak"]:
            return self.WEIGHT_VALUES["weak"], "weak_performer"
        else:
            return self.WEIGHT_VALUES["poor"], "poor_performer"

    def _apply_confidence_adjustment(
        self, base_weight: float, confidence_gap: float
    ) -> float:
        """
        Apply confidence gap adjustment to base weight

        Args:
            base_weight: Base weight from accuracy
            confidence_gap: avg_confidence - accuracy

        Returns:
            Adjusted weight
        """
        # Overconfident (confidence > accuracy by 15%+)
        if confidence_gap > self.CONFIDENCE_GAP_THRESHOLD:
            penalty = min(0.2, confidence_gap * 0.5)  # Max 0.2 penalty
            adjusted = base_weight * (1 - penalty)
            logger.warning(
                f"📉 Overconfident detected: gap={confidence_gap:+.1%}, "
                f"penalty={penalty:.2f}, weight={base_weight:.2f}→{adjusted:.2f}"
            )
            return adjusted

        # Underconfident (accuracy > confidence by 15%+)
        elif confidence_gap < -self.CONFIDENCE_GAP_THRESHOLD:
            bonus = min(0.1, abs(confidence_gap) * 0.3)  # Max 0.1 bonus
            adjusted = base_weight * (1 + bonus)
            logger.info(
                f"📈 Underconfident detected: gap={confidence_gap:+.1%}, "
                f"bonus={bonus:.2f}, weight={base_weight:.2f}→{adjusted:.2f}"
            )
            return adjusted

        # Confidence calibrated
        return base_weight

    def get_current_weights(self) -> Dict[str, float]:
        """
        Get current agent weights

        Returns:
            Dictionary of agent weights
        """
        return self.current_weights.copy()

    def detect_low_performers(
        self, threshold: float = 0.50, lookback_days: int = 30
    ) -> List[Dict]:
        """
        Detect agents with accuracy below threshold

        Args:
            threshold: Accuracy threshold (default 50%)
            lookback_days: Number of days to look back

        Returns:
            List of low-performing agents with details
        """
        logger.info(f"🔍 Detecting low performers (threshold={threshold:.0%})")

        query = text("""
            SELECT
                agent_name,
                COUNT(*) as total_votes,
                AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as accuracy,
                AVG(vote_confidence) as avg_confidence
            FROM agent_vote_tracking
            WHERE status = 'COMPLETED'
                AND evaluated_at >= NOW() - INTERVAL ':lookback_days days'
            GROUP BY agent_name
            HAVING AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) < :threshold
                AND COUNT(*) >= :min_samples
            ORDER BY accuracy ASC
        """)

        results = self.db.execute(query, {
            "lookback_days": lookback_days,
            "threshold": threshold,
            "min_samples": self.MIN_SAMPLES
        }).fetchall()

        low_performers = []
        for row in results:
            agent_info = {
                "agent_name": row.agent_name,
                "accuracy": float(row.accuracy),
                "total_votes": row.total_votes,
                "avg_confidence": float(row.avg_confidence),
                "severity": "critical" if row.accuracy < 0.45 else "warning"
            }
            low_performers.append(agent_info)

            logger.warning(
                f"⚠️ Low performer: {row.agent_name} "
                f"(accuracy={row.accuracy:.1%}, votes={row.total_votes})"
            )

        return low_performers

    def detect_overconfident_agents(
        self, gap_threshold: float = 0.20, lookback_days: int = 30
    ) -> List[Dict]:
        """
        Detect agents with high confidence but low accuracy

        Args:
            gap_threshold: Confidence gap threshold (default 20%)
            lookback_days: Number of days to look back

        Returns:
            List of overconfident agents
        """
        logger.info(f"🔍 Detecting overconfident agents (gap_threshold={gap_threshold:.0%})")

        query = text("""
            SELECT
                agent_name,
                COUNT(*) as total_votes,
                AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as accuracy,
                AVG(vote_confidence) as avg_confidence,
                (AVG(vote_confidence) - AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END)) as confidence_gap
            FROM agent_vote_tracking
            WHERE status = 'COMPLETED'
                AND evaluated_at >= NOW() - INTERVAL ':lookback_days days'
            GROUP BY agent_name
            HAVING (AVG(vote_confidence) - AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END)) > :gap_threshold
                AND COUNT(*) >= :min_samples
            ORDER BY confidence_gap DESC
        """)

        results = self.db.execute(query, {
            "lookback_days": lookback_days,
            "gap_threshold": gap_threshold,
            "min_samples": self.MIN_SAMPLES
        }).fetchall()

        overconfident = []
        for row in results:
            agent_info = {
                "agent_name": row.agent_name,
                "accuracy": float(row.accuracy),
                "avg_confidence": float(row.avg_confidence),
                "confidence_gap": float(row.confidence_gap),
                "total_votes": row.total_votes,
                "severity": "high" if row.confidence_gap > 0.30 else "medium"
            }
            overconfident.append(agent_info)

            logger.warning(
                f"🎭 Overconfident: {row.agent_name} "
                f"(confidence={row.avg_confidence:.1%}, accuracy={row.accuracy:.1%}, "
                f"gap={row.confidence_gap:+.1%})"
            )

        return overconfident

    def save_weights_history(self, weights_info: Dict[str, Dict]) -> None:
        """
        Save current weights to database history

        Args:
            weights_info: Weight calculation results
        """
        # TODO: Implement agent_weights_history table and insert
        logger.info("💾 Saving weights history to database...")

        for agent_name, info in weights_info.items():
            logger.info(
                f"  {agent_name}: weight={info['weight']:.2f}, "
                f"accuracy={info['accuracy']:.1%}, reason={info['reason']}"
            )

        # Placeholder for future DB save
        logger.warning("⚠️ agent_weights_history table not yet created")


# ============================================================================
# Standalone Functions
# ============================================================================

def calculate_weights(db, lookback_days: int = 30) -> Dict[str, float]:
    """
    Calculate agent weights (standalone function)

    Args:
        db: Database session
        lookback_days: Days to look back

    Returns:
        Dictionary of agent weights
    """
    manager = AgentWeightManager(db)
    weights_info = manager.calculate_agent_weights(lookback_days)
    return {name: info["weight"] for name, info in weights_info.items()}


def get_low_performers(db, threshold: float = 0.50) -> List[Dict]:
    """
    Get list of low-performing agents

    Args:
        db: Database session
        threshold: Accuracy threshold

    Returns:
        List of low performers
    """
    manager = AgentWeightManager(db)
    return manager.detect_low_performers(threshold)


if __name__ == "__main__":
    """Test weight calculation"""
    from backend.database.repository import get_sync_session

    logging.basicConfig(level=logging.INFO)

    db = get_sync_session()

    try:
        manager = AgentWeightManager(db)

        # Calculate weights
        print("\n" + "=" * 80)
        print("🔄 Calculating Agent Weights")
        print("=" * 80)
        weights_info = manager.calculate_agent_weights(lookback_days=30)

        # Print summary
        print("\n📊 Weight Summary:")
        print("-" * 80)
        for agent_name, info in weights_info.items():
            print(f"{agent_name:15} | Weight: {info['weight']:.2f} | "
                  f"Accuracy: {info['accuracy']:6.1%} | "
                  f"Votes: {info['total_votes']:3} | "
                  f"Gap: {info['confidence_gap']:+6.1%} | "
                  f"{info['reason']}")
        print("-" * 80)

        # Detect low performers
        print("\n⚠️ Low Performers (< 50% accuracy):")
        print("-" * 80)
        low_performers = manager.detect_low_performers()
        if low_performers:
            for agent in low_performers:
                print(f"{agent['agent_name']:15} | "
                      f"Accuracy: {agent['accuracy']:6.1%} | "
                      f"Severity: {agent['severity']}")
        else:
            print("✅ No low performers detected")
        print("-" * 80)

        # Detect overconfident agents
        print("\n🎭 Overconfident Agents (confidence >> accuracy):")
        print("-" * 80)
        overconfident = manager.detect_overconfident_agents()
        if overconfident:
            for agent in overconfident:
                print(f"{agent['agent_name']:15} | "
                      f"Confidence: {agent['avg_confidence']:6.1%} | "
                      f"Accuracy: {agent['accuracy']:6.1%} | "
                      f"Gap: {agent['confidence_gap']:+6.1%}")
        else:
            print("✅ No overconfident agents detected")
        print("-" * 80)

    finally:
        db.close()
