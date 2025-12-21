
"""
Apply Migration 007 and Create Missing Tables.
"""
import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.repository import engine
from backend.database.models import Base

def apply_migration():
    print("Applying Migration 007...")
    
    # Read migration file
    migration_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend", "database", "migrations", "007_extend_news_articles.sql"
    )
    
    with open(migration_file, "r", encoding="utf-8") as f:
        sql = f.read()

    # Split by semicolon to handle multiple statements if driver doesn't support bulk
    # But often execute(text(sql)) works for multiple statements in Postgres with SQLAlchemy
    # However, sometimes it's safer to split.
    # Postgres usually supports multiple statements in one go.
    
    with engine.connect() as conn:
        try:
            # 0. Enable Vector Extension
            print("Enabling vector extension...")
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                print("✅ Vector extension enabled/verified.")
            except Exception as e:
                print(f"⚠️ Could not enable vector extension (might already exist or permission denied): {e}")

            # 1. Apply Migration SQL
            print("Executing SQL from 007_extend_news_articles.sql...")
            conn.execute(text(sql))
            conn.commit()
            print("✅ Migration 007 Applied.")
            
            # 2. Create StockPrices table (if not exists via create_all)
            # define StockPrice in models is assumed.
            # Base.metadata.create_all checks for existing tables and skips them.
            # Since stock_prices likely doesn't exist, this will create it.
            print("Creating any missing tables (e.g. stock_prices)...")
            Base.metadata.create_all(bind=engine)
            print("✅ Missing tables created.")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    apply_migration()
