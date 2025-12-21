"""
Database Migration - Add Grounding Cost Tracking Tables

Run this script to add the new tables:
- grounding_search_log
- grounding_daily_usage

Usage:
    python tools/migrate_grounding_tables.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from backend.database.models import Base, GroundingSearchLog, GroundingDailyUsage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_grounding_tables():
    """Create grounding cost tracking tables"""
    try:
        # Create engine directly
        # Note: Update this connection string for your environment
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_trading")
        engine = create_engine(db_url)
        
        logger.info("Creating Grounding cost tracking tables...")
        logger.info(f"Database: {db_url}")
        
        # Create only the new tables
        GroundingSearchLog.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created: grounding_search_log")
        
        GroundingDailyUsage.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created: grounding_daily_usage")
        
        logger.info("\n🎉 Migration complete!")
        logger.info("New tables:")
        logger.info("  - grounding_search_log (tracks every Grounding API search)")
        logger.info("  - grounding_daily_usage (daily usage summary)")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        logger.info("\nNote: Make sure PostgreSQL is running and DATABASE_URL is correct")
        logger.info("You can also create tables manually or skip this step for now")
        raise


if __name__ == "__main__":
    migrate_grounding_tables()
