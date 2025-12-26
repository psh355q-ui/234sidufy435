"""
Comprehensive Agent Test - Call ALL endpoints

자동으로 모든 router의 주요 endpoints를 호출합니다.
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8001"

# 모든 router의 주요 endpoints 목록
ENDPOINTS_TO_TEST = [
    # System routers
    ("GET", "/auth/status", {}, "Auth status"),
    ("GET", "/auth/health", {}, "Auth health"),
    ("GET", "/logs/statistics", {"days": 7}, "Log statistics"),
    ("GET", "/api/portfolio/fle-history", {"user_id": "test", "days": 30}, "FLE history"),
    ("GET", "/orders/test-order-123", {}, "Get order (should 404)"),
    
    # Analysis routers  
    ("GET", "/api/dividend/ttm/AAPL", {}, "Dividend TTM"),
    ("GET", "/news/analyze-stream", {"max_count": 1}, "News analysis stream"),
    ("GET", "/api/ceo/health", {}, "CEO analysis health"),
    ("GET", "/api/tendency/sample", {}, "Tendency sample"),
    
    # Trading routers
    ("GET", "/api/consensus/health", {}, "Consensus health"),
    ("GET", "/api/auto-trade/health", {}, "Auto trade health"),
    
    # War Room
    ("GET", "/api/war-room/health", {}, "War room health"),
    
    # System advanced
    ("GET", "/api/monitoring/health", {}, "Monitoring health"),
    ("GET", "/api/emergency/status", {}, "Emergency status"),
    ("GET", "/api/notifications/health", {}, "Notifications health"),
    
    # Backtest
    ("GET", "/backtest/results", {}, "Backtest results"),
    
    # More endpoints
    ("GET", "/api/position/health", {}, "Position health"),
    ("GET", "/api/screener/health", {}, "Screener health"),
    ("GET", "/api/global-macro/health", {}, "Global macro health"),
    ("GET", "/api/phase/health", {}, "Phase health"),
    ("GET", "/api/kis/health", {}, "KIS health"),
    ("GET", "/api/ai-signals/health", {}, "AI signals health"),
    ("GET", "/api/reports/health", {}, "Reports health"),
    ("GET", "/api/performance/health", {}, "Performance health"),
    ("GET", "/api/feeds/health", {}, "Feeds health"),
    ("GET", "/api/data-backfill/health", {}, "Data backfill health"),
    
    # POST endpoints (더 많은 로그 생성)
    ("POST", "/api/portfolio/fle", {
        "user_id": "test",
        "positions": [{"ticker": "AAPL", "quantity": 10, "current_price": 180, "cost_basis": 150}],
        "cash": 1000
    }, "FLE calculation"),
    
    ("GET", "/api/signals/consolidated-signals", {"hours": 24}, "Consolidated signals"),
]

async def test_endpoint(session, method, path, data, desc):
    """Test single endpoint"""
    url = f"{BASE_URL}{path}"
    
    try:
        if method == "GET":
            async with session.get(url, params=data, timeout=5) as response:
                return (path, response.status, "success")
        else:
            async with session.post(url, json=data, timeout=5) as response:
                return (path, response.status, "success")
    except asyncio.TimeoutError:
        return (path, 0, "timeout")
    except Exception as e:
        return (path, 0, f"error: {type(e).__name__}")

async def main():
    print(f"🚀 Testing {len(ENDPOINTS_TO_TEST)} endpoints...")
    print("="*70)
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            test_endpoint(session, method, path, data, desc)
            for method, path, data, desc in ENDPOINTS_TO_TEST
        ]
        
        results = await asyncio.gather(*tasks)
    
    # Summary
    success_count = sum(1 for _, status, _ in results if 200 <= status < 300)
    error_count = sum(1 for _, status, _ in results if status >= 400 or status == 0)
    
    print("\n" + "="*70)
    print(f"✅ Success: {success_count}")
    print(f"⚠️  Errors: {error_count}")
    print(f"📊 Total: {len(results)}")
    
    # Show some results
    print("\n샘플 결과:")
    for path, status, result in results[:10]:
        emoji = "✅" if 200 <= status < 300 else ("⚠️" if status >= 400 else "❌")
        print(f"  {emoji} {path}: {status} {result}")
    
    print(f"\n📄 로그 파일 확인:")
    print("   backend/ai/skills/logs/*/execution-*.jsonl")

if __name__ == "__main__":
    asyncio.run(main())
