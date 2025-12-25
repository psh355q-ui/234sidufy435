"""
Script to trigger multiple agents and generate logs

This script calls various API endpoints to generate real log data:
1. War Room debate
2. Deep Reasoning analysis
3. Signal consolidation
4. Analysis endpoints

Run this to populate logs before building debugging-agent.
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def print_section(title):
    print("\n" + "="*70)
    print(f"🚀 {title}")
    print("="*70)

def call_api(endpoint, method="GET", **kwargs):
    """Call API and return response"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=30, **kwargs)
        elif method == "POST":
            response = requests.post(url, timeout=30, **kwargs)
        
        print(f"   {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"   ✅ Success")
            return data
        else:
            print(f"   ❌ Error: {response.text[:100]}")
            return None
    
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  Server not running (http://localhost:8222)")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

# ============================================================================
# Test 1: Signal Consolidation
# ============================================================================
print_section("Signal Consolidation")

# Get consolidated signals
call_api("/api/consolidated-signals", params={"hours": 24, "limit": 10})
time.sleep(1)

# Get stats
call_api("/api/consolidated-signals/stats", params={"hours": 24})
time.sleep(1)

# ============================================================================
# Test 2: War Room (if available)
# ============================================================================
print_section("War Room Debate")

# Trigger War Room debate
result = call_api(
    "/api/war-room/debate",
    method="POST",
    json={"ticker": "AAPL"}
)
time.sleep(2)

# ============================================================================
# Test 3: Deep Reasoning (if available)
# ============================================================================
print_section("Deep Reasoning Analysis")

result = call_api("/api/deep-reasoning/latest", params={"limit": 5})
time.sleep(1)

# ============================================================================
# Test 4: Dividend (if available)
# ============================================================================
print_section("Dividend Intelligence")

call_api("/api/dividend/aristocrats", params={"limit": 10})
time.sleep(1)

# ============================================================================
# Test 5: News (if available)
# ============================================================================
print_section("News Intelligence")

call_api("/api/news/latest", params={"limit": 10})
time.sleep(1)

# ============================================================================
# Test 6: Analysis (if available)
# ============================================================================
print_section("Quick Analysis")

# Trigger analysis if endpoint exists
result = call_api("/api/analyze", params={"ticker": "MSFT"})
time.sleep(1)

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*70)
print("✅ API calls complete!")
print("="*70)
print("\n📁 Check logs in:")
print("   backend/ai/skills/logs/")
print("\nTo view logs:")
print("   cd backend/ai/skills/logs")
print("   cat system/signal-consolidation/execution-*.jsonl")
print("   cat system/war-room-debate/execution-*.jsonl")
