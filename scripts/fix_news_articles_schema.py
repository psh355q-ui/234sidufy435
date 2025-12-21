
import psycopg2
import os
import sys

# Explicitly load .env
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def fix_news_schema():
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
        
        # Define missing columns and their types
        # Note: using FLOAT8[] for embedding instead of VECTOR for compatibility
        columns_to_add = [
            ("content_hash", "VARCHAR(64)"),
            ("embedding", "FLOAT8[]"),  # Fallback type
            ("tags", "TEXT[]"),
            ("tickers", "TEXT[]"),
            ("sentiment_score", "FLOAT"),
            ("sentiment_label", "VARCHAR(20)"),
            ("source_category", "VARCHAR(50)"),
            ("metadata", "JSONB"),
            ("processed_at", "TIMESTAMP"),
            ("embedding_model", "VARCHAR(50)")
        ]
        
        # Also need detailed indexes if possible, but let's stick to columns first
        
        for col_name, col_type in columns_to_add:
            try:
                # Check if column exists
                cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='news_articles' AND column_name='{col_name}';")
                if not cur.fetchone():
                    print(f"➕ Adding column: {col_name} ({col_type})")
                    cur.execute(f"ALTER TABLE news_articles ADD COLUMN {col_name} {col_type};")
                    conn.commit()
                else:
                    print(f"✅ Column {col_name} already exists.")
            except Exception as e:
                conn.rollback()
                print(f"⚠️ Failed to add column {col_name}: {e}")
        
        # Add index for content_hash
        try:
            print("➕ Adding index for content_hash...")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_news_articles_content_hash ON news_articles(content_hash);")
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"⚠️ Failed to add index: {e}")

        print("✅ Schema update completed.")
        cur.close()
        conn.close()
    
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    fix_news_schema()
