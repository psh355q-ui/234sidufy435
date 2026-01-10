import sys
import os
import asyncio
import logging
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ai.enhanced_trading_agent import EnhancedTradingAgent
from backend.models.trading_decision import TradingDecision
from collections import namedtuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simulate_small_cap_strategy():
    print("=== Simulating Small Cap Strategy ===")
    
    agent = EnhancedTradingAgent(enable_skeptic=False, enable_macro_check=False)
    
    # Mock analysis result structure
    AnalysisResult = namedtuple('AnalysisResult', ['current_price', 'market_cap', 'spread_pct'])
    
    # Mock internal methods to isolate strategy logic
    # We want to test _analyze_enhanced flow but it's hard to mock everything inside.
    # Instead, we will directly inspect the code modification by mocking the parts BEFORE the new logic
    # OR we can mock the entire `super().analyze(...)` but EnhancedTradingAgent overrides it?
    # looking at previous file view, analyze_enhanced is the main method.
    
    # Let's mock the `_scan_and_analyze` or whatever provides `analysis_result`
    # Since I cannot easily run the full analysis chain without real data/API, 
    # I will patch `agent.analyze_stock` (from parent) if it returns the base object.
    
    # WAIT: I modified `analyze_enhanced`. Let's assume I can trigger it. 
    # But `analyze_enhanced` calls many things. 
    # Let's try to mock the `TradingAgent.analyze` which presumably returns `analysis_result`.
    
    # Mocking `TradingAgent.analyze` to return a controlled result
    with patch('backend.ai.trading_agent.TradingAgent.analyze') as mock_analyze:
        
        # Setup Mock Return for Base Analysis
        mock_decision = MagicMock(spec=TradingDecision)
        mock_decision.ticker = "TEST_SMALL"
        mock_decision.action = "BUY"
        mock_decision.conviction = 0.5 # Start low to see boost
        mock_decision.reasoning = "Base Analysis"
        # Inject features so our logic picks them up
        mock_decision.features_used = {
            'market_cap': 500_000_000, # $500M
            'spread_pct': 0.5,         # 0.5%
            'current_price': 100.0
        }
        
        mock_analyze.return_value = mock_decision
        
        print("\n--- Case 1: Small Cap ($500M) + Low Spread ---")
        # We need to mock feedback_loop on the instance because it's called after our logic
        agent.feedback_loop = MagicMock()
        agent.feedback_loop.get_agent_bias.return_value = 1.0 # No bias
        
        await agent.analyze_enhanced("TEST_SMALL")
        
        # Verification: Check if conviction increased
        # Since mock_decision is modified in place
        if mock_decision.conviction > 0.5:
            print(f"✅ SUCCESS: Conviction boosted to {mock_decision.conviction:.2f}")
        else:
            print(f"❌ FAILURE: Conviction did not increase (remained {mock_decision.conviction:.2f})")
            
        
        # --- Case 2: High Spread ---
        print("\n--- Case 2: High Spread (2.5%) ---")
        mock_decision.conviction = 0.5 # Reset
        mock_decision.action = "BUY"
        mock_decision.features_used['spread_pct'] = 2.5
        
        await agent.analyze_enhanced("TEST_SMALL")
        
        if mock_decision.action == "HOLD" and mock_decision.conviction == 0.0:
            print(f"✅ SUCCESS: High spread rejected (Action: {mock_decision.action})")
        else:
            print(f"❌ FAILURE: High spread NOT rejected (Action: {mock_decision.action})")

if __name__ == "__main__":
    asyncio.run(simulate_small_cap_strategy())
