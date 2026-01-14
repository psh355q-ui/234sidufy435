
import sys
sys.path.insert(0, 'd:/code/ai-trading-system')

from dotenv import load_dotenv
load_dotenv('d:/code/ai-trading-system/.env')

from backend.database.repository import get_sync_session
from backend.database.repository_multi_strategy import StrategyRepository, PositionOwnershipRepository, ConflictLogRepository
from backend.execution.order_manager import OrderManager
from backend.services.ownership_service import OwnershipService

# Setup
db = get_sync_session()
repo_strat = StrategyRepository(db)
repo_own = PositionOwnershipRepository(db)
repo_conflict = ConflictLogRepository(db)
order_manager = OrderManager(db)

# 1. Get Strategies
# Priorities: long_term (100) > dividend (90) > trading (50) > aggressive (30)
strat_high = repo_strat.get_by_name("long_term") # 100
strat_med = repo_strat.get_by_name("trading")    # 50
strat_low = repo_strat.get_by_name("aggressive") # 30

print(f"High: {strat_high.name} ({strat_high.priority})")
print(f"Med:  {strat_med.name} ({strat_med.priority})")
print(f"Low:  {strat_low.name} ({strat_low.priority})")

TICKER = "CFT_TEST"

# Cleanup
existing_own = repo_own.get_primary_ownership(TICKER)
if existing_own:
    db.delete(existing_own)
    db.commit()

from backend.execution.state_machine import OrderState

# ==========================================
# Scenario 1: Block (Low tries to buy High's asset)
# ==========================================
print("\n=== Scenario 1: Block Test ===")
# Assign ownership to High
repo_own.create(strat_high.id, TICKER, "primary", reasoning="Initial High Own")
db.commit()

try:
    print(f"Low ({strat_low.name}) attempts to buy {TICKER} (owned by High)...")
    order = order_manager.create_order(TICKER, "BUY", 10, strategy_id=strat_low.id)
    
    if order.status == OrderState.REJECTED.value:
        print(f"✅ BLOCKED as expected: Status={order.status}")
        # print(f"Reason: {order.order_metadata}") # If implemented
    else:
        print(f"❌ FAILED: Order status is {order.status}, expected REJECTED")
        
except Exception as e:
    print(f"❌ FAILED with Exception: {e}")

# ==========================================
# Scenario 2: Override (High takes from Low)
# ==========================================
print("\n=== Scenario 2: Override Test ===")
# Cleanup & Assign ownership to Low
existing_own = repo_own.get_primary_ownership(TICKER)
if existing_own:
    db.delete(existing_own)
    db.commit()
    
repo_own.create(strat_low.id, TICKER, "primary", reasoning="Initial Low Own")
db.commit()

try:
    print(f"High ({strat_high.name}) attempts to buy {TICKER} (owned by Low)...")
    order = order_manager.create_order(TICKER, "BUY", 10, strategy_id=strat_high.id)
    print(f"Order Created: {order.id}, Status: {order.status}")
    
    if order.status == OrderState.ORDER_PENDING.value:
        print(f"✅ Order Accepted: Status={order.status}")
    else:
        print(f"❌ FAILED: Order status is {order.status}, expected ORDER_PENDING")
    
    # Verify Ownership Transferred
    new_own = repo_own.get_primary_ownership(TICKER)
    print(f"New Owner: {new_own.strategy_id}")
    
    assert new_own.strategy_id == strat_high.id
    print("✅ Ownership Transferred Successfully")
    
except Exception as e:
    with open("debug_conflict_final.txt", "w") as f:
        f.write(f"FAILED: Order blocked unexpectedly: {e}\n")
        import traceback
        traceback.print_exc(file=f)

# Cleanup
final_own = repo_own.get_primary_ownership(TICKER)
if final_own:
    db.delete(final_own)
    db.commit()
