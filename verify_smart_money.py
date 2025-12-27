
import asyncio
import os
import sys

# 프로젝트 루트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from backend.data.collectors.smart_money_collector import SmartMoneyCollector

async def verify_smart_money():
    print("="*60)
    print("🔍 Smart Money Collector Verification (Real Data)")
    print("="*60)
    
    collector = SmartMoneyCollector()
    ticker = "PLTR"
    
    print(f"\n📊 Analyzing {ticker}...\n")
    
    # 1. Institutional Holders
    print("--- 1. Institutional Holders ---")
    holders = await collector.get_institutional_holders(ticker, limit=5)
    if not holders:
        print("❌ No institutional holders found.")
    else:
        for i, h in enumerate(holders, 1):
            print(f"{i}. {h.name}")
            print(f"   Shares: {h.shares:,}")
            print(f"   Value: ${h.value:,.0f}")
            print(f"   Pct: {h.percentage:.2%}")
    
    # 2. Insider Trades
    print("\n--- 2. Insider Trades ---")
    trades = await collector.get_insider_trades(ticker, days=90) # 90 days
    if not trades:
        print("❌ No insider trades found.")
    else:
        for i, t in enumerate(trades[:5], 1):
            print(f"{i}. {t.insider_name} ({t.position})")
            print(f"   Type: {t.transaction_type.value}")
            print(f"   Shares: {t.shares:,}")
            print(f"   Value: ${t.value:,.0f}")
            print(f"   Date: {t.date.strftime('%Y-%m-%d')}")

    # 3. Full Analysis
    print("\n--- 3. Full Analysis Signal ---")
    signal = await collector.analyze_smart_money(ticker)
    print(f"Signal: {signal.signal_strength.value}")
    print(f"Pressure: {signal.institution_buying_pressure:.2%}")
    print(f"Key Institutions: {signal.key_institutions}")
    print(f"Key Insiders: {signal.key_insiders}")
    print(f"Reasoning:\n{signal.analysis}")

if __name__ == "__main__":
    asyncio.run(verify_smart_money())
