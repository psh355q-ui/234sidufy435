"""
Comprehensive Endpoint Test - Call ALL 333 endpoints

Automatically generates appropriate test data for each endpoint type.
"""

import asyncio
import aiohttp
import json
from pathlib import Path

BASE_URL = "http://localhost:8001"

# Read all endpoints
endpoints_file = Path("all_endpoints.txt")
all_endpoints = []

with open(endpoints_file, 'r') as f:
    for line in f:
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.strip().split()
        if len(parts) >= 2:
            method = parts[0]
            path = parts[1]
            all_endpoints.append((method, path))

print(f"Loaded {len(all_endpoints)} endpoints")

# Test data generators
def get_test_data(method, path):
    """Generate appropriate test data based on endpoint"""
    
    # GET endpoints - use query params
    if method == "GET":
        if "/health" in path or "/status" in path:
            return {}
        elif "{" in path:  # Path parameters
            # Replace {param} with test value
            test_path = path.replace("{ticker}", "AAPL")
            test_path = test_path.replace("{id}", "test-123")
            test_path = test_path.replace("{order_id}", "order-123")
            test_path = test_path.replace("{chat_id}", "chat-123")
            test_path = test_path.replace("{signal_id}", "123")
            test_path = test_path.replace("{job_id}", "job-123")
            test_path = test_path.replace("{report_id}", "report-123")
            return (test_path, {})
        else:
            return {}
    
    # POST endpoints - use JSON body
    elif method == "POST":
        if "chat" in path:
            return {"message": "test", "user_id": "test"}
        elif "fle" in path:
            return {
                "user_id": "test",
                "positions": [{"ticker": "AAPL", "quantity": 10, "current_price": 180, "cost_basis": 150}],
                "cash": 1000
            }
        elif "analyze" in path or "reasoning" in path:
            return {"ticker": "NVDA", "news_context": "test", "technical_summary": "test"}
        elif "backtest" in path or "run" in path:
            return {
                "name": "Test",
                "config": {"tickers": ["NVDA"], "start_date": "2024-01-01", "end_date": "2024-01-31"}
            }
        elif "trade" in path or "execute" in path:
            return {"ticker": "AAPL", "action": "BUY", "quantity": 1}
        elif "debate" in path or "war-room" in path:
            return {"ticker": "NVDA", "signal_type": "BUY", "confidence": 0.85}
        else:
            return {"test": "data"}
    
    return {}

async def test_endpoint(session, method, path):
    """Test single endpoint"""
    
    status = 0  # Initialize
    
    # Get test data
    test_data = get_test_data(method, path)
    
    # Handle path parameters
    if isinstance(test_data, tuple):
        path, params = test_data
    else:
        params = test_data if method == "GET" else {}
    
    url = f"{BASE_URL}{path}"
    
    try:
        if method == "GET":
            async with session.get(url, params=params, timeout=3) as response:
                status = response.status
                return (path, status, "ok")
        elif method == "POST":
            async with session.post(url, json=test_data, timeout=3) as response:
                status = response.status
                return (path, status, "ok")
        elif method == "PUT":
            async with session.put(url, json=test_data, timeout=3) as response:
                status = response.status
                return (path, status, "ok")
        elif method == "DELETE":
            async with session.delete(url, timeout=3) as response:
                status = response.status
                return (path, status, "ok")
        else:
            return (path, 0, "unsupported_method")
            
    except asyncio.TimeoutError:
        return (path, 0, "timeout")
    except Exception as e:
        return (path, 0, f"error:{type(e).__name__}")

async def main():
    print(f"\n🚀 Testing {len(all_endpoints)} endpoints...")
    print("="*70)
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Test in batches to avoid overwhelming server
        batch_size = 20
        
        for i in range(0, len(all_endpoints), batch_size):
            batch = all_endpoints[i:i+batch_size]
            
            tasks = [
                test_endpoint(session, method, path)
                for method, path in batch
            ]
            
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
            print(f"Progress: {len(results)}/{len(all_endpoints)}")
            await asyncio.sleep(0.5)  # Small delay between batches
    
    # Analyze results
    success = sum(1 for _, status, _ in results if 200 <= status < 300)
    client_error = sum(1 for _, status, _ in results if 400 <= status < 500)
    server_error = sum(1 for _, status, _ in results if status >= 500)
    timeout = sum(1 for _, status, _ in results if status == 0)
    
    print("\n" + "="*70)
    print("📊 Results Summary")
    print("="*70)
    print(f"✅ Success (2xx):        {success:3d}")
    print(f"⚠️  Client Error (4xx):  {client_error:3d}")
    print(f"❌ Server Error (5xx):  {server_error:3d}")
    print(f"⏱️  Timeout:             {timeout:3d}")
    print(f"📊 Total:               {len(results):3d}")
    
    # Show some examples
    print(f"\n샘플 성공 endpoints:")
    for path, status, result in [r for r in results if 200 <= status < 300][:10]:
        print(f"  ✅ {status} {path}")
    
    print(f"\n📄 로그 확인:")
    print("   backend/ai/skills/logs/*/execution-*.jsonl")
    
    # Check logs
    from pathlib import Path
    try:
        log_files = list(Path("backend/ai/skills/logs").rglob("execution-*.jsonl"))
        total_logs = 0
        for f in log_files:
            if f.exists():
                total_logs += f.read_text(encoding='utf-8', errors='ignore').count('\n')
        print(f"\n✅ Total log entries: {total_logs}")
    except Exception as e:
        print(f"\n⚠️  Could not count logs: {e}")

if __name__ == "__main__":
    asyncio.run(main())
