"""
Test Phase 25.4: Agent Weight Auto-Adjustment & Alert System

Date: 2025-12-23
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.repository import get_sync_session
from backend.ai.learning.agent_weight_manager import AgentWeightManager
from backend.ai.learning.alert_system import AgentAlertSystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_weight_calculation():
    """Test agent weight calculation"""
    logger.info("=" * 80)
    logger.info("Testing Agent Weight Calculation")
    logger.info("=" * 80)

    db = get_sync_session()
    try:
        manager = AgentWeightManager(db)

        # Calculate weights for last 30 days
        logger.info("\n📊 Calculating agent weights (30-day lookback)...")
        weights_info = manager.calculate_agent_weights(lookback_days=30)

        logger.info("\n✅ Weight Calculation Results:")
        logger.info("-" * 80)
        for agent_name, info in weights_info.items():
            logger.info(f"\n🤖 Agent: {agent_name}")
            logger.info(f"  Accuracy: {info['accuracy']:.1%}")
            logger.info(f"  Confidence: {info['avg_confidence']:.1%}")
            logger.info(f"  Gap: {info['confidence_gap']:+.1%}")
            logger.info(f"  Total Votes: {info['total_votes']}")
            logger.info(f"  Old Weight: {info['old_weight']:.2f}")
            logger.info(f"  New Weight: {info['new_weight']:.2f}")
            logger.info(f"  Change: {info['weight_change']:+.2f}")
        logger.info("-" * 80)

        return weights_info

    except Exception as e:
        logger.error(f"❌ Weight calculation failed: {e}", exc_info=True)
        return None
    finally:
        db.close()


def test_low_performer_detection():
    """Test low performer detection"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Low Performer Detection")
    logger.info("=" * 80)

    db = get_sync_session()
    try:
        manager = AgentWeightManager(db)

        # Detect low performers (< 50% accuracy)
        logger.info("\n🔍 Detecting low performers (threshold: 50%)...")
        low_performers = manager.detect_low_performers(threshold=0.50, lookback_days=30)

        if low_performers:
            logger.info(f"\n⚠️ Found {len(low_performers)} low performer(s):")
            logger.info("-" * 80)
            for agent in low_performers:
                logger.info(f"\n🤖 Agent: {agent['agent_name']}")
                logger.info(f"  Accuracy: {agent['accuracy']:.1%}")
                logger.info(f"  Total Votes: {agent['total_votes']}")
                logger.info(f"  Severity: {agent['severity'].upper()}")
        else:
            logger.info("\n✅ No low performers found!")
        logger.info("-" * 80)

        return low_performers

    except Exception as e:
        logger.error(f"❌ Low performer detection failed: {e}", exc_info=True)
        return []
    finally:
        db.close()


def test_overconfident_detection():
    """Test overconfident agent detection"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Overconfident Agent Detection")
    logger.info("=" * 80)

    db = get_sync_session()
    try:
        manager = AgentWeightManager(db)

        # Detect overconfident agents (gap > 20%)
        logger.info("\n🔍 Detecting overconfident agents (gap threshold: 20%)...")
        overconfident = manager.detect_overconfident_agents(gap_threshold=0.20, lookback_days=30)

        if overconfident:
            logger.info(f"\n🎭 Found {len(overconfident)} overconfident agent(s):")
            logger.info("-" * 80)
            for agent in overconfident:
                logger.info(f"\n🤖 Agent: {agent['agent_name']}")
                logger.info(f"  Confidence: {agent['avg_confidence']:.1%}")
                logger.info(f"  Accuracy: {agent['accuracy']:.1%}")
                logger.info(f"  Gap: {agent['confidence_gap']:+.1%}")
                logger.info(f"  Severity: {agent['severity'].upper()}")
        else:
            logger.info("\n✅ No overconfident agents found!")
        logger.info("-" * 80)

        return overconfident

    except Exception as e:
        logger.error(f"❌ Overconfident detection failed: {e}", exc_info=True)
        return []
    finally:
        db.close()


def test_alert_system(low_performers, overconfident):
    """Test alert system"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Alert System")
    logger.info("=" * 80)

    try:
        alert_system = AgentAlertSystem()

        # Send alerts
        logger.info("\n📢 Sending performance alerts...")
        alerts = alert_system.check_and_send_alerts(low_performers, overconfident)

        # Get summary
        summary = alert_system.get_alerts_summary()

        logger.info("\n📊 Alert Summary:")
        logger.info("-" * 80)
        logger.info(f"Total Alerts: {summary['total_alerts']}")
        logger.info(f"By Type: {summary['by_type']}")
        logger.info(f"By Severity: {summary['by_severity']}")
        logger.info("-" * 80)

        return alerts

    except Exception as e:
        logger.error(f"❌ Alert system failed: {e}", exc_info=True)
        return []


def main():
    """Run all tests"""
    logger.info("\n" + "=" * 80)
    logger.info("🚀 Phase 25.4 - Testing Agent Weight Auto-Adjustment & Alert System")
    logger.info("=" * 80)

    # Test 1: Weight calculation
    weights_info = test_weight_calculation()

    # Test 2: Low performer detection
    low_performers = test_low_performer_detection()

    # Test 3: Overconfident detection
    overconfident = test_overconfident_detection()

    # Test 4: Alert system
    alerts = test_alert_system(low_performers, overconfident)

    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("✅ Phase 25.4 Testing Complete!")
    logger.info("=" * 80)
    logger.info(f"\n📊 Results:")
    logger.info(f"  - Agents analyzed: {len(weights_info) if weights_info else 0}")
    logger.info(f"  - Low performers: {len(low_performers)}")
    logger.info(f"  - Overconfident agents: {len(overconfident)}")
    logger.info(f"  - Alerts sent: {len(alerts)}")
    logger.info("=" * 80 + "\n")


if __name__ == "__main__":
    main()
