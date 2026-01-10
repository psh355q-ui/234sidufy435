import sys
import os
import asyncio
import logging
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.signal_executor import SignalExecutor, ExecutionResult
from backend.execution.safety_guard import get_safety_guard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_safety_guard_rejection():
    print("=== Testing Safety Guard Logic ===")
    
    # Mock KIS Client
    mock_kis = MagicMock()
    
    # Mock methods to allow execution to reach SafetyGuard check
    # 1. get_access_token -> True
    mock_kis.get_access_token.return_value = "mock_token"
    
    # 2. get_current_price -> $100
    # Note: SignalExecutor calls this via asyncio.to_thread wrapping the synchronous KIS method
    # The synchronous method returns an APIResponse object
    mock_price_response = MagicMock()
    mock_price_response.isOK.return_value = True
    mock_price_response.getBody.return_value.output.stck_prpr = "100" # $100
    mock_kis.get_current_price.return_value = mock_price_response
    
    # 3. get_balance -> $100,000 (Rich mock user)
    mock_balance_response = MagicMock()
    mock_balance_response.isOK.return_value = True
    mock_balance_response.getBody.return_value.output2 = [MagicMock(dnca_tot_amt="100000")]
    mock_kis.get_balance.return_value = mock_balance_response

    # Initialize Executor with mocked KIS
    executor = SignalExecutor(use_paper_trading=True, enable_auto_execute=True)
    executor._kis_client = mock_kis # Inject mock
    
    # Create a Dangerous Signal (High value)
    # Price $100 * Position Size 0.5 of $100k = $50,000 Order Value
    # This exceeds SafetyGuard limit of $1,000
    dangerous_signal = {
        "ticker": "NVDA",
        "action": "BUY",
        "position_size": 0.5, # 50% of portfolio
        "confidence": 0.9,
        "auto_execute": True
    }
    
    print(f"Sending Signal: {dangerous_signal}")
    print("Expected Result: REJECTED by SafetyGuard (Max Order Limit)")
    
    # Execute
    result = await executor.execute_signal(dangerous_signal)
    
    print("\n=== Execution Result ===")
    print(f"Success: {result.success}")
    print(f"Status: {result.status.value}")
    print(f"Message: {result.message}")
    print(f"Error: {result.error}")
    
    # Verification
    if result.status.value == "REJECTED" and "Safety Guard" in result.message:
        print("\n✅ TEST PASSED: Safety Guard correctly rejected the trade.")
    else:
        print("\n❌ TEST FAILED: Safety Guard did not catch the trade.")

if __name__ == "__main__":
    asyncio.run(test_safety_guard_rejection())
