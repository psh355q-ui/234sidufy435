"""
Quick Production Validation Test

Tests the 6 fixed critical agents to verify they work correctly.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_agent(name, method, endpoint, **kwargs):
    """Test a single agent endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=kwargs.get('params'), timeout=10)
        elif method == "POST":
            response = requests.post(url, json=kwargs.get('json'), timeout=10)
        
        status = response.status_code
        
        if status == 200:
            print(f"✅ SUCCESS ({status})")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"Response: {response.text[:200]}...")
            return True
        else:
            print(f"⚠️  Status: {status}")
            print(f"Response: {response.text[:300]}")
            return False
            
    except requests.Timeout:
        print(f"⏱️  TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)[:100]}")
        return False

def main():
    print("\n" + "="*60)
    print("🎯 PRODUCTION VALIDATION TEST")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    
    results = {}
    
    # Test 1: Global Macro - Market Map (actual working endpoint)
    results['global_macro'] = test_agent(
        "Global Macro - Market Map",
        "GET",
        "/api/global-macro/market-map"
    )
    
    # Test 2: War Room Sessions (fixed: votes JSONB)
    results['war_room'] = test_agent(
        "War Room Sessions",
        "GET",
        "/api/war-room/sessions",
        params={"limit": 1}
    )
    
    # Test 3: Reports Health (actual endpoint)
    results['reports'] = test_agent(
        "Reports Health Check",
        "GET",
        "/reports/health"
    )
    
    # Test 4: Notifications Settings (actual endpoint - no /api prefix)
    results['notifications'] = test_agent(
        "Notifications Settings",
        "GET",
        "/notifications/settings"
    )
    
    # Test 5: Backfill Jobs
    results['backfill'] = test_agent(
        "Backfill Jobs",
        "GET",
        "/api/backfill/jobs"
    )
    
    # Test 6: Gemini Status (actual endpoint - no /api prefix)
    results['gemini'] = test_agent(
        "Gemini Status",
        "GET",
        "/gemini-free/status"
    )
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for agent, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{agent:20s}: {status}")
    
    print(f"\nSuccess Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
