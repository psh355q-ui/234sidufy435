"""
Create price_tracking table

Phase 25.1: Agent Performance Tracking
Date: 2025-12-23

Usage:
    python backend/scripts/create_price_tracking.py
"""

import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# DB connection
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    database=os.getenv("POSTGRES_DB", "ai_trading"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD")
)

cursor = conn.cursor()

print("=" * 80)
print("Creating price_tracking table")
print("=" * 80)

# Read SQL file
sql_file = Path(__file__).parent.parent / "database" / "create_price_tracking_table.sql"

with open(sql_file, "r") as f:
    sql = f.read()

try:
    # Execute SQL
    cursor.execute(sql)
    conn.commit()

    print("\n✅ price_tracking table created successfully!")

    # Check table structure
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'price_tracking'
        ORDER BY ordinal_position
    """)

    columns = cursor.fetchall()

    print("\n📊 Table Structure:")
    print(f"{'Column':<25} {'Type':<20} {'Nullable'}")
    print("-" * 70)
    for col_name, data_type, is_nullable in columns:
        print(f"{col_name:<25} {data_type:<20} {is_nullable}")

    # Check indexes
    cursor.execute("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'price_tracking'
    """)

    indexes = cursor.fetchall()

    if indexes:
        print("\n🔍 Indexes:")
        for idx_name, idx_def in indexes:
            print(f"  • {idx_name}")

except Exception as e:
    print(f"\n❌ Error creating table: {e}")
    conn.rollback()
    raise

finally:
    cursor.close()
    conn.close()

print("\n" + "=" * 80)
print("✅ Done")
print("=" * 80)
