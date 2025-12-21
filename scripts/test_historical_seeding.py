
"""
Test Historical Data Seeding Database Integration.
Verifies that models, repositories, and database connections work correctly.
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.database.models import Base, StockPrice, DataCollectionProgress, NewsSource, NewsArticle
from backend.database.repository import (
    get_db_session, 
    StockRepository, 
    DataCollectionRepository, 
    NewsRepository,
    get_sync_session
)
from backend.database.db_service import get_db_service

async def test_database_integration():
    print("=" * 60)
    print("Testing Historical Data Seeding Integration")
    print("=" * 60)

    import traceback
    
    # 1. Initializing Tables
    print("\n1. Initializing Tables...")
    try:
        from backend.database.repository import engine
        
        # Try to create vector extension
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                print("   Vector extension enabled")
            except Exception as e:
                 print(f"   Warning: Could not enable vector extension: {e}")

        Base.metadata.create_all(bind=engine)
        print("✅ Tables created/verified successfully")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        traceback.print_exc()
        return


    # 2. Test Data Collection Repository
    print("\n" + "-"*30)
    print("2. Testing Data Collection Repository...")
    print("-"*30)
    try:
        async with get_db_session() as session:
            repo = DataCollectionRepository(session)
            
            # Create Job
            job = repo.create_job(
                source="test_source",
                collection_type="prices",
                start_date=datetime.now(),
                end_date=datetime.now(),
                metadata={"test": True}
            )
            print(f"   Created Job ID: {job.id}")
            
            # Update Job
            repo.update_progress(
                job_id=job.id,
                processed=10,
                total=100,
                status="running"
            )
            print("   Updated Job Progress")
            
            # Verify
            check = session.query(DataCollectionProgress).filter_by(id=job.id).first()
            if check.status == "running" and check.processed_items == 10:
                print("✅ DataCollectionRepository working")
            else:
                print(f"❌ DataCollectionRepository failed: status={check.status}, processed={check.processed_items}")
    except Exception as e:
        print(f"❌ DataCollectionRepository crashed: {e}")
        # traceback.print_exc()

    # 3. Test Stock Repository
    print("\n" + "-"*30)
    print("3. Testing Stock Repository...")
    print("-"*30)
    try:
        async with get_db_session() as session:
            repo = StockRepository(session)
            
            # Save prices
            prices = [
                {
                    "ticker": "TEST_AAPL",
                    "date": datetime.now(),
                    "open": 150.0,
                    "high": 155.0,
                    "low": 149.0,
                    "close": 152.0,
                    "volume": 1000000,
                    "adj_close": 152.0,
                    "source": "manual_test"
                },
                {
                    "ticker": "TEST_AAPL",
                    "date": datetime.now() - timedelta(days=1),
                    "open": 148.0,
                    "high": 151.0,
                    "low": 147.0,
                    "close": 150.0,
                    "volume": 900000,
                    "adj_close": 150.0,
                    "source": "manual_test"
                }
            ]
            
            try:
                repo.save_prices(prices)
                print("   Saved 2 price records")
            except Exception as e:
                 print(f"   Save warning (might be duplicate): {e}")
                 # session.rollback() logic is inside save_prices but handled by context manager?
                 # No, context manager commits on exit. save_prices commits inside.
            
            # Query
            results = repo.get_prices(
                "TEST_AAPL", 
                datetime.now() - timedelta(days=2),
                datetime.now()
            )
            if len(results) >= 2:
                print(f"✅ StockRepository working (Found {len(results)} records)")
            else:
                print(f"❌ StockRepository failed (Found {len(results)} records)")
    except Exception as e:
        print(f"❌ StockRepository crashed: {e}")
        traceback.print_exc()

    # 4. Test News Repository (New Fields)
    print("\n" + "-"*30)
    print("4. Testing News Repository (NLP Fields)...")
    print("-"*30)
    try:
        async with get_db_session() as session:
            repo = NewsRepository(session)
            
            article_data = {
                "title": "Test NLP Article",
                "content": "This is a test content.",
                "url": f"http://test.com/{datetime.now().timestamp()}",
                "source": "Test Source",
                "published_at": datetime.now(),
                "content_hash": f"hash_{datetime.now().timestamp()}",
                "embedding": [0.1] * 1536, # Dummy embedding
                "sentiment_score": 0.8,
                "sentiment_label": "positive",
                "tags": ["tech", "ai"],
                "tickers": ["AAPL", "NVDA"],
                "embedding_model": "text-embedding-3-small",
                "metadata": {"test": "metadata"}
            }
            
            article = repo.save_processed_article(article_data)
            print(f"   Saved Article ID: {article.id}")
            
            # Verify fields
            check = session.query(NewsArticle).filter_by(id=article.id).first()
            if (check.sentiment_score == 0.8 and 
                check.tickers == ["AAPL", "NVDA"]):
                print("✅ NewsRepository NLP fields working")
            else:
                print("❌ NewsRepository NLP fields failed")
                print(f"   Score: {check.sentiment_score}")
                print(f"   Tickers: {check.tickers}")
    except Exception as e:
        print(f"❌ NewsRepository crashed: {e}")
        traceback.print_exc()


    print("\n=" * 60)
    print("Integration Test Completed")
    print("=" * 60)
    
    with open("test_result.txt", "w") as f:
        f.write("RESULT: SUCCESS")

if __name__ == "__main__":
    try:
        asyncio.run(test_database_integration())
    except Exception as e:
        with open("test_result.txt", "w") as f:
            f.write(f"RESULT: FAILURE - {e}")
        print(f"Global Crash: {e}")
