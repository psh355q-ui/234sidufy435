import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Checking imports...")

try:
    print("[1] Importing yfinance...")
    import yfinance as yf
    print("✅ yfinance imported")
except ImportError as e:
    print(f"❌ yfinance import failed: {e}")

try:
    print("[2] Importing DailyBriefingService...")
    from backend.services.daily_briefing_service import DailyBriefingService
    print("✅ DailyBriefingService imported")
except Exception as e:
    print(f"❌ DailyBriefingService import failed: {e}")

try:
    print("[3] Importing briefing_router...")
    from backend.api.briefing_router import router
    print("✅ briefing_router imported")
except Exception as e:
    print(f"❌ briefing_router import failed: {e}")

try:
    print("[4] Importing EnhancedTradingAgent...")
    from backend.ai.enhanced_trading_agent import EnhancedTradingAgent
    print("✅ EnhancedTradingAgent imported")
except Exception as e:
    print(f"❌ EnhancedTradingAgent import failed: {e}")
