#!/usr/bin/env python
"""
Test Macro Context-Based Portfolio Adjustment
Uses current macro context to recommend portfolio allocation
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / '.env', override=True)

print("="*80)
print(f"Macro Context-Based Portfolio Adjustment - {datetime.now().strftime('%H:%M:%S')}")
print("="*80)
print()

# Step 1: Load Current Macro Context
print("[1/3] Loading Current Macro Context...")
print("-"*80)

from backend.database.repository import MacroContextRepository, get_sync_session
from datetime import date

session = get_sync_session()
macro_repo = MacroContextRepository(session)
macro_context = macro_repo.get_by_date(date.today())

if macro_context:
    print(f"✅ Current Market Regime:")
    print(f"   Regime: {macro_context.regime}")
    print(f"   Fed Stance: {macro_context.fed_stance}")
    print(f"   VIX: {macro_context.vix_level} ({macro_context.vix_category})")
    print(f"   Market Sentiment: {macro_context.market_sentiment}")
    print(f"   S&P 500 Trend: {macro_context.sp500_trend}")
    print(f"   Geopolitical Risk: {macro_context.geopolitical_risk}")
    print()
    print(f"   Narrative: {macro_context.dominant_narrative[:150]}...")
else:
    print("❌ No macro context found")
    exit(1)

print()

# Step 2: Generate Portfolio Recommendation with Claude
print("[2/3] Generating Portfolio Recommendation...")
print("-"*80)

from anthropic import Anthropic

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

prompt = f"""You are a professional portfolio manager. Based on the current macro economic context, recommend a portfolio allocation strategy.

Current Market Context:
- Regime: {macro_context.regime}
- Fed Stance: {macro_context.fed_stance} (likely to keep rates high)
- VIX: {macro_context.vix_level} ({macro_context.vix_category}) - market volatility
- Market Sentiment: {macro_context.market_sentiment}
- S&P 500 Trend: {macro_context.sp500_trend}
- Geopolitical Risk: {macro_context.geopolitical_risk}

Market Narrative:
{macro_context.dominant_narrative}

Available Stock Universe: AAPL, NVDA, TSLA, GOOGL, MSFT, AMD, META, AMZN

Provide a portfolio recommendation in this exact JSON format:
{{
    "strategy": "Brief strategy description",
    "allocation": [
        {{"ticker": "SYMBOL", "weight": 0.XX, "rationale": "Why this stock fits the regime"}},
        ...
    ],
    "risk_level": "LOW" | "MEDIUM" | "HIGH",
    "rebalance_frequency": "DAILY" | "WEEKLY" | "MONTHLY",
    "key_risks": ["risk1", "risk2"],
    "expected_volatility": "LOW" | "MEDIUM" | "HIGH"
}}

Guidelines:
1. Allocate to 3-5 stocks (weights must sum to 1.0)
2. Consider Fed hawkish stance (favor value over growth if needed)
3. Account for current market sentiment
4. Align with S&P 500 trend
5. Consider geopolitical risks

Return ONLY valid JSON."""

response = client.messages.create(
    model='claude-3-5-haiku-20241022',
    max_tokens=1000,
    messages=[{'role': 'user', 'content': prompt}]
)

# Parse response
import json
import re
response_text = response.content[0].text.strip()
json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL | re.MULTILINE)

if not json_match:
    # Try to find nested JSON
    json_match = re.search(r'\{.*"strategy".*\}', response_text, re.DOTALL)

if json_match:
    portfolio = json.loads(json_match.group())

    print(f"✅ Portfolio Strategy: {portfolio['strategy']}")
    print(f"   Risk Level: {portfolio['risk_level']}")
    print(f"   Expected Volatility: {portfolio['expected_volatility']}")
    print(f"   Rebalance: {portfolio['rebalance_frequency']}")
    print()
    print("   Allocation:")

    for stock in portfolio['allocation']:
        print(f"   - {stock['ticker']:6s}: {stock['weight']*100:5.1f}% - {stock['rationale'][:60]}...")

    print()
    print("   Key Risks:")
    for risk in portfolio['key_risks']:
        print(f"   - {risk}")
else:
    print("❌ Could not parse portfolio recommendation")
    print(f"Response: {response_text}")
    portfolio = None

print()

# Step 3: Get Current Prices for Recommended Stocks
if portfolio:
    print("[3/3] Fetching Current Prices...")
    print("-"*80)

    from backend.brokers.kis_broker import KISBroker

    broker = KISBroker(
        account_no=os.getenv('KIS_PAPER_ACCOUNT'),
        product_code='01',
        is_virtual=True
    )

    print()
    for stock in portfolio['allocation']:
        try:
            price_data = broker.get_price(stock['ticker'], 'NASDAQ')
            if price_data:
                stock['current_price'] = price_data['current_price']
                stock['change_pct'] = price_data['change_rate']
                print(f"   {stock['ticker']:6s}: ${price_data['current_price']:8.2f} ({price_data['change_rate']:+6.2f}%) - Weight: {stock['weight']*100:5.1f}%")
        except Exception as e:
            print(f"   {stock['ticker']:6s}: Price unavailable - {e}")

    print()

    # Calculate portfolio value for $10,000 investment
    print("   Sample Portfolio ($10,000 total):")
    print("   " + "="*60)
    total_value = 10000

    for stock in portfolio['allocation']:
        if 'current_price' in stock:
            allocation_value = total_value * stock['weight']
            shares = int(allocation_value / stock['current_price'])
            actual_value = shares * stock['current_price']
            print(f"   {stock['ticker']:6s}: {shares:3d} shares @ ${stock['current_price']:7.2f} = ${actual_value:8.2f} ({stock['weight']*100:5.1f}%)")

session.close()

print()
print("="*80)
print("Portfolio Recommendation Complete")
print("="*80)
print()
print("This portfolio is optimized for:")
if macro_context:
    print(f"  - Market Regime: {macro_context.regime}")
    print(f"  - Fed Policy: {macro_context.fed_stance}")
    print(f"  - Market Sentiment: {macro_context.market_sentiment}")
print()
print("Next: Generate trading signals for these allocations")
print("="*80)
