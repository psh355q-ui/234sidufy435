"""
Agent Test Runner - Generate Logs

Executes various agent endpoints to generate log data.
This creates both success and error logs for Debugging Agent analysis.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:8001"

async def test_endpoint(session, method, path, data=None, desc=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    
    print(f"📡 Testing: {method} {path}")
    if desc:
        print(f"   {desc}")
    
    try:
        if method == "GET":
            async with session.get(url, params=data, timeout=10) as response:
                status = response.status
                text = await response.text()
                print(f"   ✅ {status}: {text[:100]}...")
                return True
        elif method == "POST":
            async with session.post(url, json=data, timeout=10) as response:
                status = response.status
                text = await response.text()
                print(f"   ✅ {status}: {text[:100]}...")
                return True
    except asyncio.TimeoutError:
        print(f"   ⏱️  Timeout")
        return False
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {str(e)[:50]}")
        return False


async def run_tests():
    """Run all test scenarios"""
    
    print("🚀 Starting Agent Test Runner")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Signal Consolidation (should work)
        await test_endpoint(
            session, "GET", "/api/signals/consolidated-signals",
            {"ticker": "NVDA", "hours": 24},
            "Get consolidated signals"
        )
        
        # Test 2: FLE Calculator (might fail - no portfolio)
        await test_endpoint(
            session, "POST", "/api/portfolio/fle",
            {
                "user_id": "test_user",
                "positions": [
                    {"ticker": "AAPL", "quantity": 10, "current_price": 180, "cost_basis": 150}
                ],
                "cash": 1000
            },
            "Calculate FLE"
        )
        
        # Test 3: Dividend Intelligence
        await test_endpoint(
            session, "GET", "/api/dividend/ttm/AAPL",
            desc="Get AAPL dividend yield"
        )
        
        # Test 4: Gemini News (might fail - API key)
        await test_endpoint(
            session, "GET", "/api/news/gemini/search/ticker/NVDA",
            {"max_articles": 3},
            "Search NVDA news"
        )
        
        # Test 5: Log Statistics
        await test_endpoint(
            session, "GET", "/logs/statistics",
            {"days": 7},
            "Get log statistics"
        )
        
        # Test 6: War Room (likely to fail - complex)
        await test_endpoint(
            session, "POST", "/api/war-room/debate",
            {
                "ticker": "NVDA",
                "signal_type": "BUY",
                "confidence": 0.85,
                "reasoning": "Test debate"
            },
            "Trigger war room debate"
        )
        
        # Test 7: Auto Trade (likely to fail - permissions)
        await test_endpoint(
            session, "POST", "/api/auto-trade/execute",
            {
                "ticker": "AAPL",
                "action": "BUY",
                "quantity": 1
            },
            "Execute auto trade"
        )
        
        # Test 8: Deep Reasoning
        await test_endpoint(
            session, "POST", "/reasoning/analyze",
            {
                "ticker": "NVDA",
                "news_context": "NVIDIA announces new GPU",
                "technical_summary": "Price up 5%"
            },
            "Deep reasoning analysis"
        )
        
        # Test 9: Invalid endpoint (should error)
        await test_endpoint(
            session, "GET", "/api/invalid/endpoint",
            desc="Test error logging"
        )
        
        # Test 10: Backtest (complex, might timeout)
        await test_endpoint(
            session, "POST", "/backtest/run",
            {
                "name": "Test Backtest",
                "description": "Quick test",
                "config": {
                    "tickers": ["NVDA"],
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "initial_capital": 10000
                }
            },
            "Run backtest"
        )
    
    print("="*60)
    print("✅ Test run complete!")
    print("\n📄 Check logs in: backend/ai/skills/logs/")


async def main():
    print("\n⚠️  Make sure backend server is running on http://localhost:8001")
    print("   Start with: uvicorn backend.main:app --reload --port 8001\n")
    
    input("Press Enter to continue...")
    
    await run_tests()
    
    print("\n📊 Next steps:")
    print("1. python backend/ai/skills/system/debugging-agent/scripts/log_reader.py")
    print("2. python backend/ai/skills/system/debugging-agent/scripts/pattern_detector.py")
    print("3. python backend/ai/skills/system/debugging-agent/scripts/improvement_proposer.py")


if __name__ == "__main__":
    asyncio.run(main())
