
import psycopg2
from psycopg2 import sql
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Explicitly load .env
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

try:
    from backend.config.settings import settings
except ImportError as e:
    print(f"❌ Failed to import settings: {e}")
    sys.exit(1)

def fix_stock_prices_id():
    print(f"Connecting to database...")
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL not found in .env")
            sys.exit(1)
            
        if db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
            
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check if id column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='stock_prices' AND column_name='id';
        """)
        exists = cur.fetchone()
        
        if not exists:
            print("❌ 'id' column missing in 'stock_prices'. Adding it now...")
            
            try:
                # 1. Add column first and commit independent of PK constraint
                cur.execute("ALTER TABLE stock_prices ADD COLUMN id BIGSERIAL;")
                conn.commit()
                print("✅ Added 'id' column as BIGSERIAL.")
            except Exception as e:
                conn.rollback()
                print(f"⚠️ Failed to add 'id' column: {e}")
                return

            # 2. Try to set PRIMARY KEY (Optional but recommended)
            try:
                # Check if it's a hypertable (safely)
                try:
                   cur.execute("SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'stock_prices';")
                   is_hypertable = cur.fetchone()
                except Exception:
                   conn.rollback()
                   is_hypertable = False
                   print("ℹ️ Could not check hypertable status. Assuming standard table.")

                if is_hypertable:
                    print("ℹ️ Table is a Hypertable. Skipping PRIMARY KEY constraint on 'id'.")
                else:
                    print("ℹ️ Attempting to set 'id' as PRIMARY KEY...")
                    cur.execute("ALTER TABLE stock_prices ADD PRIMARY KEY (id);")
                    conn.commit()
                    print("✅ Set 'id' as PRIMARY KEY.")
                
            except Exception as e:
                conn.rollback()
                print(f"⚠️ Failed to set PRIMARY KEY (This is fine if table works): {e}")
        else:
            print("✅ 'id' column already exists.")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    fix_stock_prices_id()
