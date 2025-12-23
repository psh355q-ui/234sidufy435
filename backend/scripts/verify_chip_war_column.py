"""
Verify chip_war_vote column exists in ai_debate_sessions table
"""

import psycopg2
import os
from dotenv import load_dotenv

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

# Check if column exists
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'ai_debate_sessions'
    AND column_name = 'chip_war_vote'
""")

result = cursor.fetchone()

if result:
    print(f"✅ chip_war_vote column EXISTS")
    print(f"   Column: {result[0]}")
    print(f"   Type: {result[1]}")
else:
    print("❌ chip_war_vote column NOT FOUND")

# Also check all columns in the table
print("\n📋 All columns in ai_debate_sessions:")
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'ai_debate_sessions'
    ORDER BY ordinal_position
""")

for row in cursor.fetchall():
    print(f"   - {row[0]}: {row[1]}")

cursor.close()
conn.close()
