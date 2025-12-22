"""
Chip Intelligence Daily Updater - Cron Job

Runs daily at 6 AM to:
1. Update chip specifications from latest intelligence
2. Process new rumors and confirm/deny old ones
3. Generate/update future scenarios
4. Learn from past War Room debates
5. Adjust scenario probabilities

Usage:
    python -m backend.schedulers.chip_intelligence_updater

Or add to crontab:
    0 6 * * * cd /path/to/ai-trading-system && python -m backend.schedulers.chip_intelligence_updater

Author: AI Trading System
Date: 2025-12-23
Phase: 24.5 (Self-Learning Scheduler)
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.ai.economics.chip_intelligence_engine import ChipIntelligenceOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/chip_intelligence_updater.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def daily_chip_intelligence_update():
    """
    Main daily update routine

    Called by cron every day at 6 AM
    """
    logger.info("="  * 80)
    logger.info("🧠 CHIP INTELLIGENCE DAILY UPDATE")
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    try:
        # Initialize orchestrator
        orchestrator = ChipIntelligenceOrchestrator()

        # Run daily update
        report = orchestrator.daily_update()

        logger.info("\n✅ Daily update completed successfully")
        logger.info(f"Report Summary:")
        logger.info(f"  - Learning Accuracy: {report.get('learning_accuracy', 0):.0%}")
        logger.info(f"  - Active Scenarios: {report.get('active_scenarios', 0)}")
        logger.info(f"  - High-Credibility Rumors: {report.get('high_credibility_rumors', 0)}")
        logger.info(f"  - Improvements: {len(report.get('improvements_suggested', []))}")

        return report

    except Exception as e:
        logger.error(f"❌ Daily update failed: {e}", exc_info=True)
        raise


async def example_add_rumor():
    """
    Example: Add a new rumor to the system

    This would normally be triggered by news monitoring systems
    """
    orchestrator = ChipIntelligenceOrchestrator()

    # Example: Add Nvidia Rubin rumor
    orchestrator.rumor_tracker.add_rumor_from_source(
        chip_vendor="Nvidia",
        chip_name="Rubin Ultra",
        rumor_type="release_date",
        content="Supply chain sources suggest Rubin Ultra pushed to Q4 2027 (was Q2 2027)",
        source="digitimes_taiwan",
        credibility_score=0.80
    )

    logger.info("✅ Rumor added successfully")


async def example_generate_scenarios():
    """
    Example: Generate future scenarios

    This would be run monthly or when major news breaks
    """
    orchestrator = ChipIntelligenceOrchestrator()

    scenarios = orchestrator.scenario_gen.generate_scenarios_for_next_year()

    logger.info(f"✅ Generated {len(scenarios)} scenarios:")
    for s in scenarios:
        logger.info(f"  - {s.name}: {s.probability:.0%} probability")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "add-rumor":
            # Example: python -m backend.schedulers.chip_intelligence_updater add-rumor
            asyncio.run(example_add_rumor())

        elif command == "generate-scenarios":
            # Example: python -m backend.schedulers.chip_intelligence_updater generate-scenarios
            asyncio.run(example_generate_scenarios())

        elif command == "update":
            # Example: python -m backend.schedulers.chip_intelligence_updater update
            asyncio.run(daily_chip_intelligence_update())

        else:
            print(f"Unknown command: {command}")
            print("Usage: python -m backend.schedulers.chip_intelligence_updater [update|add-rumor|generate-scenarios]")

    else:
        # Default: Run daily update
        asyncio.run(daily_chip_intelligence_update())
