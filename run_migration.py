"""
Execute DB Migration for State Machine columns
"""
import psycopg2
from psycopg2 import sql

# Database connection parameters
DB_CONFIG = {
    'dbname': 'ai_trading',
    'user': 'postgres',
    'password': 'Qkqhdi1!',
    'host': 'localhost',
    'port': 5433
}

# Read migration SQL
with open('backend/database/migrations/add_state_machine_columns.sql', 'r', encoding='utf-8') as f:
    migration_sql = f.read()

print("🔄 Connecting to database...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    print("🔄 Executing migration...")
    cur.execute(migration_sql)

    print("✅ Migration executed successfully!")

    # Verify columns exist
    print("\n🔍 Verifying columns...")
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'orders'
        AND column_name IN ('filled_quantity', 'order_metadata', 'needs_manual_review', 'updated_at')
        ORDER BY column_name;
    """)

    columns = cur.fetchall()
    if columns:
        print("✅ New columns verified:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
    else:
        print("⚠️  Warning: Could not verify new columns")

    cur.close()
    conn.close()

    print("\n✅ Migration complete! You can now restart the backend.")

except psycopg2.Error as e:
    print(f"❌ Database error: {e}")
    print(f"   SQLSTATE: {e.pgcode}")
    print(f"   Details: {e.pgerror}")
except Exception as e:
    print(f"❌ Error: {e}")
