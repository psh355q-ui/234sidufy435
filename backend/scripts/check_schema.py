
import sys
sys.path.insert(0, 'd:/code/ai-trading-system')
from dotenv import load_dotenv
load_dotenv('d:/code/ai-trading-system/.env')
from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL.startswith('postgresql+asyncpg://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
engine = create_engine(DATABASE_URL)

inspector = inspect(engine)
tables = ['position_ownership', 'conflict_logs']
columns_to_check = ['ticker', 'action_attempted']

print("=== DB SCHEMA MANAGER REPORT ===")
for table in tables:
    cols = inspector.get_columns(table)
    print(f"\nTable: {table}")
    found = False
    for col in cols:
        if col['name'] in columns_to_check:
            print(f"  - Column: {col['name']:<20} | Type: {col['type']}")
            found = True
    if not found:
        print("  (Target columns not found)")
print("================================")
