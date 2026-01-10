import requests
import json
import time

BASE_URL = "http://localhost:8001/api/briefing"

def test_briefing_api():
    print("🧪 Testing Daily Briefing API...")
    
    # 1. Trigger Generation
    print("\n[1] Triggering Generation (POST /generate)...")
    try:
        resp = requests.post(f"{BASE_URL}/generate")
        if resp.status_code == 200:
            print("✅ Generation triggered successfully!")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"❌ Failed: {resp.status_code}")
            print(resp.text)
            return
    except Exception as e:
        print(f"❌ connection error: {e}")
        return

    # 2. Get Latest
    print("\n[2] Fetching Latest Briefing (GET /latest)...")
    try:
        resp = requests.get(f"{BASE_URL}/latest")
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Briefing Fetched!")
            print(f"Date: {data.get('date')}")
            print(f"Metrics: {data.get('metrics')}")
            print(f"Content Length: {len(data.get('content', ''))}")
            # print("Content Preview:", data.get('content')[:200])
        else:
            print(f"❌ Failed: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"❌ connection error: {e}")

if __name__ == "__main__":
    test_briefing_api()
