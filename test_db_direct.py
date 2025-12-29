#!/usr/bin/env python
"""
Test Direct DB Connection
"""
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

# Test connection
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'ai_trading'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'Qkqhdi1!')
    )

    cursor = conn.cursor()

    # Test query
    cursor.execute("SELECT COUNT(*) FROM macro_context_snapshots;")
    count = cursor.fetchone()[0]

    print("="*60)
    print("✅ Direct DB Connection Successful")
    print("="*60)
    print(f"Database: {os.getenv('DB_NAME')}")
    print(f"Host: {os.getenv('DB_HOST')}")
    print(f"macro_context_snapshots row count: {count}")
    print("="*60)

    # List all tables
    cursor.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)
    tables = cursor.fetchall()

    print("\nAll tables:")
    for table in tables:
        print(f"  - {table[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Connection failed: {e}")
