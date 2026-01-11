
import sys
sys.path.insert(0, 'd:/code/ai-trading-system')

from dotenv import load_dotenv
load_dotenv('d:/code/ai-trading-system/.env')

from backend.database.repository import get_sync_session
from backend.database.repository_multi_strategy import StrategyRepository, PositionOwnershipRepository
from backend.services.ownership_service import OwnershipService
from datetime import datetime

# Setup
db = get_sync_session()
repo_strat = StrategyRepository(db)
repo_own = PositionOwnershipRepository(db)
service = OwnershipService(db)

# 1. Get strategies
s1 = repo_strat.get_by_name("trading")
s2 = repo_strat.get_by_name("long_term")

print(f"Strategy 1: {s1.name} ({s1.id})")
print(f"Strategy 2: {s2.name} ({s2.id})")

# 2. Create initial ownership (mimic T2.2)
ticker = "TRF_TEST"

# Cleanup previous run remnants
existing = repo_own.get_primary_ownership(ticker)
if existing:
    print("Found existing test ownership, deleting...")
    db.delete(existing)
    db.commit()

try:
    owner = repo_own.create(s1.id, ticker, "primary", reasoning="Initial Buy")
    db.commit()
    print(f"Created ownership: {ticker} -> {s1.name}")
except Exception as e:
    with open("debug_output.txt", "w") as f:
        f.write(f"FAILED to create ownership: {e}\n")
        import traceback
        traceback.print_exc(file=f)
    sys.exit(1)

# 3. Attempt Transfer
print("Attempting transfer...")
result = service.transfer_ownership(ticker, s1.id, s2.id, "Strategy Shift")
print(f"Result: {result}")

# 4. Verify
updated_owner = repo_own.get_primary_ownership(ticker)
print(f"New Owner ID: {updated_owner.strategy_id}")
print(f"Reasoning: {updated_owner.reasoning}")

assert updated_owner.strategy_id == s2.id
print("✅ Verification Successful")

# Cleanup
db.delete(updated_owner)
db.commit()
