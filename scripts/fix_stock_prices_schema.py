
import sys
import os
from sqlalchemy import text

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.repository import engine

def fix_schema():
    print("Fixing stock_prices schema...")
    with engine.connect() as conn:
        try:
            # Check existing columns
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='stock_prices'")).fetchall()
            existing_columns = [r[0] for r in result]
            
            print(f"Existing columns: {existing_columns}")
            
            # Add 'source' column if not exists
            if 'source' not in existing_columns:
                print("Adding 'source' column...")
                conn.execute(text("ALTER TABLE stock_prices ADD COLUMN source VARCHAR(50) DEFAULT 'yfinance'"))
            else:
                print("'source' column already exists.")

            # Add 'created_at' column if not exists
            if 'created_at' not in existing_columns:
                print("Adding 'created_at' column...")
                conn.execute(text("ALTER TABLE stock_prices ADD COLUMN created_at TIMESTAMP DEFAULT NOW()"))
            else:
                print("'created_at' column already exists.")
                
            conn.commit()
            print("✅ Schema fix applied successfully.")
            
        except Exception as e:
            print(f"❌ Schema fix failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_schema()
