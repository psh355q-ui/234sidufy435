
import psycopg2
import os
import sys

# Explicitly load .env
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def debug_news_schema():
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
        
        table_name = 'news_articles'
        print(f"[{table_name} Columns]")
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}';
        """)
        rows = cur.fetchall()
        
        found_columns = []
        for row in rows:
            print(f" - {row[0]}: {row[1]}")
            found_columns.append(row[0])
            
        required_columns = ['embedding', 'sentiment_score', 'metadata', 'content_hash']
        missing = [col for col in required_columns if col not in found_columns]
        
        if missing:
            print(f"❌ Missing columns: {missing}")
        else:
            print("✅ All required columns are present.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_news_schema()
