
import psycopg2
import os
import sys
from datetime import datetime

# Explicitly load .env
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def verify_news_data():
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
        
        print("Fetching latest 5 collected news articles...", flush=True)
        cur.execute("""
            SELECT id, title, source, published_date, sentiment_score, sentiment_label, tickers 
            FROM news_articles 
            ORDER BY crawled_at DESC 
            LIMIT 5;
        """)
        
        rows = cur.fetchall()
        
        if not rows:
            print("❌ No news articles found in the database.", flush=True)
        else:
            print(f"✅ Found {len(rows)} recent articles:", flush=True)
            print("-" * 100, flush=True)
            print(f"{'ID':<5} | {'Source':<15} | {'Date':<12} | {'Label':<8} | {'Tickers':<20} | {'Title'}", flush=True)
            print("-" * 100, flush=True)
            for row in rows:
                id_ = row[0]
                title = row[1][:40] + "..." if len(row[1]) > 40 else row[1]
                source = row[2]
                date = row[3].strftime("%Y-%m-%d") if row[3] else "N/A"
                # Handle possible None
                score = row[4] if row[4] is not None else 0.0
                label = row[5] if row[5] else "N/A"
                tickers = str(row[6]) if row[6] else "[]"
                
                print(f"{id_:<5} | {source:<15} | {date:<12} | {label:<8} | {tickers:<20} | {title}", flush=True)
            print("-" * 100, flush=True)
            
        # Also count total
        cur.execute("SELECT count(*) FROM news_articles;")
        count = cur.fetchone()[0]
        print(f"\nTotal articles in DB: {count}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_news_data()
