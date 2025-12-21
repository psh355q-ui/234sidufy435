import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.repository import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='stock_prices'")).fetchall()
        print("Columns in stock_prices:")
        for row in result:
            print(f" - {row[0]} ({row[1]})")
            
        print("\nChecking if 'date' or 'time' exists:")
        cols = [r[0] for r in result]
        if 'date' in cols:
            print("✅ 'date' column exists.")
        if 'time' in cols:
            print("✅ 'time' column exists.")
        if 'date' not in cols and 'time' not in cols:
            print("❌ Neither 'date' nor 'time' column found!")

    except Exception as e:
        print(f"Error: {e}")
