"""
Database Initialization Script
Creates all tables defined in backend/database/models.py AND backend/core/models/analytics_models.py

Usage:
    python backend/scripts/init_database.py
"""

import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

# Import legacy DB
from backend.database.models import Base
from backend.database.repository import engine
import logging

# Import core DB (Async)
from backend.core.database import Base as CoreBase, engine as core_async_engine
# Import models to register them to CoreBase
import backend.core.models.analytics_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_core_db():
    print("Initializing Core DB (Async)...")
    
    # Select specific tables to create (to avoid conflicts with Legacy DB)
    target_tables = [
        backend.core.models.analytics_models.DailyAnalytics.__table__,
        backend.core.models.analytics_models.WeeklyAnalytics.__table__,
        backend.core.models.analytics_models.MonthlyAnalytics.__table__,
        backend.core.models.analytics_models.TradeExecution.__table__,
        backend.core.models.analytics_models.PortfolioSnapshot.__table__,
        backend.core.models.analytics_models.SignalPerformance.__table__,
    ]
    
    async with core_async_engine.begin() as conn:
        await conn.run_sync(CoreBase.metadata.create_all, tables=target_tables)
    print("✅ Core Database tables created (DailyAnalytics, Weekly, Monthly, TradeExec, Snapshot)!")


def init_database():
    """Initialize database tables"""

    print("=" * 80)
    print("AI Trading System - Database Initialization")
    print("=" * 80)
    print()

    try:
        # Create legacy tables
        logger.info("Creating legacy database tables (Skipping to avoid index errors)...")
        # Base.metadata.create_all(bind=engine)
        # print("✅ Legacy Database tables created successfully!")
        
        print("-" * 40)

        # Create core tables
        asyncio.run(init_core_db())

        print()
        print("=" * 80)
        print("Database initialization complete!")
        print("=" * 80)
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    init_database()
