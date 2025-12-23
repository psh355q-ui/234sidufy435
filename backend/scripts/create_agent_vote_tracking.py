"""
Create agent_vote_tracking table

Phase 25.3: Self-Learning Feedback Loop
Date: 2025-12-23

Creates the agent_vote_tracking table for tracking individual agent votes
and their 24-hour performance evaluation.
"""

import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.repository import get_sync_session
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_agent_vote_tracking_table():
    """Create agent_vote_tracking table from SQL file"""

    logger.info("=" * 80)
    logger.info("Creating agent_vote_tracking table...")
    logger.info("=" * 80)

    db = get_sync_session()

    try:
        # Read SQL file
        sql_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "database",
            "create_agent_vote_tracking_table.sql"
        )

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        # Execute SQL
        logger.info("📝 Executing SQL from: %s", sql_file)
        db.execute(text(sql))
        db.commit()

        logger.info("✅ agent_vote_tracking table created successfully!")

        # Verify table creation
        result = db.execute(text("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'agent_vote_tracking'
            ORDER BY ordinal_position
        """))

        columns = result.fetchall()

        logger.info("\n📊 Table Structure:")
        logger.info("-" * 80)
        for col in columns:
            logger.info(f"  {col.column_name:30} {col.data_type}")
        logger.info("-" * 80)

        # Verify indexes
        result = db.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'agent_vote_tracking'
        """))

        indexes = result.fetchall()

        logger.info("\n🔍 Indexes:")
        logger.info("-" * 80)
        for idx in indexes:
            logger.info(f"  ✓ {idx.indexname}")
        logger.info("-" * 80)

        logger.info("\n✅ agent_vote_tracking table is ready!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Failed to create table: {e}", exc_info=True)
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_agent_vote_tracking_table()
