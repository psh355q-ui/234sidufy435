"""
Test Script for Orders API Conflict Checking Endpoint

Phase 5, Task T5.1

Tests the POST /api/orders/check-conflict endpoint with various scenarios.

Prerequisites:
    - FastAPI server running (python -m uvicorn backend.main:app --reload)
    - PostgreSQL with seed strategies loaded
    - Strategies: long_term (100), dividend (90), trading (50), aggressive (30)

Run:
    python backend/tests/test_orders_api_conflict.py
"""

import sys
sys.path.insert(0, 'd:/code/ai-trading-system')

import requests
from dotenv import load_dotenv
load_dotenv('d:/code/ai-trading-system/.env')

from backend.database.repository import get_sync_session
from backend.database.repository_multi_strategy import StrategyRepository, PositionOwnershipRepository

# FastAPI server URL
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/orders/check-conflict"

# Setup: Get strategy IDs
db = get_sync_session()
strategy_repo = StrategyRepository(db)
ownership_repo = PositionOwnershipRepository(db)

long_term = strategy_repo.get_by_name("long_term")    # Priority: 100
trading = strategy_repo.get_by_name("trading")        # Priority: 50
aggressive = strategy_repo.get_by_name("aggressive")  # Priority: 30

print("=== Strategy IDs ===")
print(f"Long Term: {long_term.id} (Priority: {long_term.priority})")
print(f"Trading: {trading.id} (Priority: {trading.priority})")
print(f"Aggressive: {aggressive.id} (Priority: {aggressive.priority})")

TICKER = "TEST_API_AAPL"

# Cleanup existing ownership
existing_own = ownership_repo.get_primary_ownership(TICKER)
if existing_own:
    db.delete(existing_own)
    db.commit()

print(f"\n=== Testing POST {API_URL} ===\n")

# ============================================================================
# Test 1: No Ownership - Should be ALLOWED
# ============================================================================
print("--- Test 1: No Ownership (Should be ALLOWED) ---")
payload = {
    "strategy_id": trading.id,
    "ticker": TICKER,
    "action": "BUY",
    "quantity": 100
}

response = requests.post(API_URL, json=payload)
print(f"Status Code: {response.status_code}")
result = response.json()
print(f"Response: {result}")

assert response.status_code == 200
assert result["has_conflict"] == False
assert result["resolution"] == "allowed"
assert result["can_proceed"] == True
print("✅ Test 1 PASSED\n")

# ============================================================================
# Test 2: Assign Ownership to Long-Term, Trading tries to buy (BLOCKED)
# ============================================================================
print("--- Test 2: Long-Term owns, Trading attempts (Should be BLOCKED) ---")

# Assign ownership to long_term
ownership_repo.create(long_term.id, TICKER, "primary", reasoning="Long-term hold")
db.commit()
print(f"Ownership assigned to: {long_term.name}")

payload = {
    "strategy_id": trading.id,
    "ticker": TICKER,
    "action": "BUY",
    "quantity": 100
}

response = requests.post(API_URL, json=payload)
print(f"Status Code: {response.status_code}")
result = response.json()
print(f"Response: {result}")

assert response.status_code == 200
assert result["has_conflict"] == True
assert result["resolution"] == "blocked"
assert result["can_proceed"] == False
assert result["conflict_detail"] is not None
assert result["conflict_detail"]["owning_strategy_name"] == "long_term"
print("✅ Test 2 PASSED\n")

# ============================================================================
# Test 3: Long-Term owns, Long-Term tries to buy (ALLOWED - Same Strategy)
# ============================================================================
print("--- Test 3: Long-Term owns, Long-Term attempts (Should be ALLOWED) ---")

payload = {
    "strategy_id": long_term.id,
    "ticker": TICKER,
    "action": "BUY",
    "quantity": 50
}

response = requests.post(API_URL, json=payload)
print(f"Status Code: {response.status_code}")
result = response.json()
print(f"Response: {result}")

assert response.status_code == 200
assert result["has_conflict"] == False
assert result["resolution"] == "allowed"
assert result["can_proceed"] == True
print("✅ Test 3 PASSED\n")

# ============================================================================
# Test 4: Change ownership to Aggressive, Long-Term tries (PRIORITY_OVERRIDE)
# ============================================================================
print("--- Test 4: Aggressive owns, Long-Term attempts (Should be PRIORITY_OVERRIDE) ---")

# Cleanup and assign to aggressive
existing_own = ownership_repo.get_primary_ownership(TICKER)
if existing_own:
    db.delete(existing_own)
    db.commit()

ownership_repo.create(aggressive.id, TICKER, "primary", reasoning="Aggressive trade")
db.commit()
print(f"Ownership assigned to: {aggressive.name}")

payload = {
    "strategy_id": long_term.id,
    "ticker": TICKER,
    "action": "BUY",
    "quantity": 200
}

response = requests.post(API_URL, json=payload)
print(f"Status Code: {response.status_code}")
result = response.json()
print(f"Response: {result}")

assert response.status_code == 200
assert result["has_conflict"] == True
assert result["resolution"] == "priority_override"
assert result["can_proceed"] == True
assert result["conflict_detail"] is not None
assert result["conflict_detail"]["owning_strategy_name"] == "aggressive"
print("✅ Test 4 PASSED\n")

# ============================================================================
# Test 5: Invalid Strategy ID (Should be 404)
# ============================================================================
print("--- Test 5: Invalid Strategy ID (Should be 404) ---")

payload = {
    "strategy_id": "00000000-0000-0000-0000-000000000000",
    "ticker": TICKER,
    "action": "BUY",
    "quantity": 100
}

response = requests.post(API_URL, json=payload)
print(f"Status Code: {response.status_code}")
result = response.json()
print(f"Response: {result}")

assert response.status_code == 404
assert "not found" in result["detail"].lower()
print("✅ Test 5 PASSED\n")

# ============================================================================
# Cleanup
# ============================================================================
print("--- Cleanup ---")
existing_own = ownership_repo.get_primary_ownership(TICKER)
if existing_own:
    db.delete(existing_own)
    db.commit()
    print("Ownership cleaned up")

db.close()

print("\n" + "="*60)
print("✅ All Tests PASSED! Phase 5, T5.1 is complete.")
print("="*60)
