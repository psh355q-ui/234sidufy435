import asyncio
import logging
import sys
import os
import json
from datetime import datetime, timedelta

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ai.learning.feedback_loop_service import FeedbackLoopService, FEEDBACK_FILE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_feedback_loop():
    print("🔄 Testing Feedback Loop Service...")
    
    # 1. Initialize
    service = FeedbackLoopService()
    
    # 2. Mock a past vote (Fake History) to simulate validation
    # Assume we voted BUY on NVDA 3 days ago at a low price
    past_vote = {
        "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
        "ticker": "NVDA",
        "agent": "Trader",
        "vote": "BUY",
        "entry_price": 10.0, # Unrealistically low to ensure profit
        "confidence": 0.9,
        "validated": False,
        "outcome": None
    }
    
    # Inject into history
    service.history.append(past_vote)
    service._save_history()
    print("Created mock past vote for NVDA (BUY @ $10.0)")
    
    # 3. Trigger Update
    print("Running update_scores()... (Fetching real NVDA price)")
    await service.update_scores()
    
    # 4. Check Results
    validated_vote = service.history[-1]
    print(f"Vote Validated? {validated_vote.get('validated')}")
    print(f"Outcome: {validated_vote.get('outcome')}")
    print(f"Current Price: {validated_vote.get('exit_price')}")
    
    # 5. Check Bias
    bias = service.get_agent_bias("Trader")
    print(f"Trader Agent Bias: {bias}")
    
    if validated_vote.get('outcome') == "SUCCESS" and bias > 1.0:
        print("\n✅ SUCCESS: Feedback Loop correctly validated a profitable trade and increased trust (Bias > 1.0).")
    else:
        print("\n❌ FAILURE: Feedback Loop failed to validate or adjust bias correctly.")

if __name__ == "__main__":
    asyncio.run(test_feedback_loop())
