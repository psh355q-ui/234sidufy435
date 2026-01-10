import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.models import DailyBriefing
from backend.database.repository import get_sync_session
from sqlalchemy import inspect

def check_table():
    print("Checking database for 'daily_briefings' table...")
    try:
        db = get_sync_session()
        inspector = inspect(db.get_bind())
        tables = inspector.get_table_names()
        
        if "daily_briefings" in tables:
            print("✅ Table 'daily_briefings' EXISTS.")
            
            # Check columns
            columns = [c['name'] for c in inspector.get_columns("daily_briefings")]
            print(f"Columns: {columns}")
            
            required = ['id', 'date', 'content', 'metrics']
            missing = [c for c in required if c not in columns]
            
            if missing:
                print(f"❌ Missing columns: {missing}")
            else:
                print("✅ Schema verification PASSED.")
                
        else:
            print("❌ Table 'daily_briefings' DOES NOT EXIST.")
            print("Attempting to create table...")
            # Create ONLY the new table
            DailyBriefing.__table__.create(bind=db.get_bind())
            print("✅ Table 'daily_briefings' created successfully.")
            
            # Commit not needed for DDL usually, but safe to do
            db.commit()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    check_table()
