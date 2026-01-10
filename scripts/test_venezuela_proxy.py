import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ai.reasoning.deep_reasoning_agent import DeepReasoningAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_venezuela_proxy():
    print("🇻🇪 Testing Venezuela Deep Reasoning Proxy...")
    
    agent = DeepReasoningAgent()
    
    # Simulate a Venezuela event
    event_type = "GEOPOLITICS"
    keywords = ["venezuela", "sanctions", "maduro"]
    base_info = {"ticker": "CVX", "news_title": "US considers easing sanctions on Venezuela"}
    
    # Run analysis
    result = await agent.analyze_event(event_type, keywords, base_info)
    
    print("\n🔍 Analysis Result:")
    print(f"Status: {result.get('status')}")
    
    simulation = result.get('simulation', {})
    proxy_data = simulation.get('venezuela_proxy_data', {})
    
    print("\n🛢️ Proxy Market Data Fetched:")
    print(f"WTI Oil (CL=F): ${proxy_data.get('WTI')}")
    print(f"Valero (VLO):   ${proxy_data.get('VLO')}")
    print(f"Chevron (CVX):  ${proxy_data.get('CVX')}")
    
    if proxy_data.get('WTI', 0) > 0 and proxy_data.get('VLO', 0) > 0:
        print("\n✅ SUCCESS: Real market data fetched successfully.")
    else:
        print("\n❌ FAILURE: Failed to fetch market data.")

if __name__ == "__main__":
    asyncio.run(test_venezuela_proxy())
