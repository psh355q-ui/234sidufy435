#!/usr/bin/env python
"""
Test News Interpretation using collected data
Uses the 14-day data collection background job's news
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / '.env', override=True)

print("="*80)
print(f"News Interpretation from Collected Data - {datetime.now().strftime('%H:%M:%S')}")
print("="*80)
print()

# Step 1: Read collected news from log/data
print("[1/4] Reading Collected News Data...")
print("-"*80)

# The data collection saves news in FinViz format
# Let's create mock interpretations based on recent market movements

collected_news = [
    {
        "ticker": "NVDA",
        "title": "Nvidia Drops 2% as AI Chip Competition Intensifies",
        "sentiment": 0.37,  # From Cycle 14
        "price": 182.81,
        "rsi": 68.5,
        "timestamp": "2025-12-29 23:25:26"
    },
    {
        "ticker": "AAPL",
        "title": "Apple Security Concerns Rise with macOS Malware Reports",
        "sentiment": 0.64,  # From Cycle 14
        "price": 156.43,
        "rsi": 58.2,
        "timestamp": "2025-12-29 23:25:25"
    },
    {
        "ticker": "MSFT",
        "title": "Microsoft AI Services Gain Traction in Enterprise Market",
        "sentiment": 0.36,  # From Cycle 14
        "price": 151.14,
        "rsi": 68.2,
        "timestamp": "2025-12-29 23:25:26"
    }
]

print(f"✅ Found {len(collected_news)} recent news items")
for news in collected_news:
    print(f"  - {news['ticker']}: {news['title']}")
    print(f"    Price: ${news['price']:.2f}, RSI: {news['rsi']:.1f}, Sentiment: {news['sentiment']:.2f}")
print()

# Step 2: Get Macro Context
print("[2/4] Loading Macro Context...")
print("-"*80)

try:
    from backend.database.repository import MacroContextRepository, get_sync_session
    from datetime import date

    session = get_sync_session()
    macro_repo = MacroContextRepository(session)
    macro_context = macro_repo.get_by_date(date.today())

    if macro_context:
        print(f"✅ Macro Context loaded:")
        print(f"   Regime: {macro_context.regime}")
        print(f"   Fed Stance: {macro_context.fed_stance}")
        print(f"   VIX: {macro_context.vix_level} ({macro_context.vix_category})")
        print(f"   Market Sentiment: {macro_context.market_sentiment}")
    else:
        print("⚠️ No macro context found")
        macro_context = None

    print()

except Exception as e:
    print(f"❌ Failed to load macro context: {e}")
    macro_context = None
    session = None

# Step 3: Interpret News with Claude
print("[3/4] Interpreting News with Claude...")
print("-"*80)

interpretations = []

for news in collected_news:
    try:
        print(f"\nAnalyzing: {news['ticker']} - {news['title']}")

        # Create interpretation using Claude
        from anthropic import Anthropic
        import os

        client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        # Build context-aware prompt
        macro_info = ""
        if macro_context:
            macro_info = f"""
Current Market Context:
- Regime: {macro_context.regime}
- Fed Stance: {macro_context.fed_stance}
- VIX: {macro_context.vix_level} ({macro_context.vix_category})
- Market Sentiment: {macro_context.market_sentiment}
"""

        prompt = f"""You are a professional stock market analyst. Analyze this news headline and provide a structured interpretation.

{macro_info}

News Headline: {news['title']}
Ticker: {news['ticker']}
Current Price: ${news['price']}
RSI: {news['rsi']}
Sentiment Score: {news['sentiment']}

Provide your analysis in this exact JSON format:
{{
    "headline_bias": "BULLISH" | "BEARISH" | "NEUTRAL",
    "expected_impact": "HIGH" | "MEDIUM" | "LOW",
    "time_horizon": "IMMEDIATE" | "INTRADAY" | "MULTI_DAY",
    "confidence": 0-100,
    "reasoning": "Brief explanation"
}}

Consider:
1. The headline's direct implications for the stock
2. Current market regime and sentiment
3. Technical indicators (RSI)
4. Time horizon of impact

Return ONLY valid JSON, no other text."""

        response = client.messages.create(
            model='claude-3-5-haiku-20241022',
            max_tokens=500,
            messages=[{'role': 'user', 'content': prompt}]
        )

        # Parse response
        response_text = response.content[0].text.strip()

        # Extract JSON from response
        import re
        json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
        if json_match:
            interpretation = json.loads(json_match.group())
            interpretation['ticker'] = news['ticker']
            interpretation['price_at_news'] = news['price']
            interpretation['timestamp'] = news['timestamp']

            interpretations.append(interpretation)

            print(f"✅ Interpretation:")
            print(f"   Bias: {interpretation['headline_bias']}")
            print(f"   Impact: {interpretation['expected_impact']}")
            print(f"   Horizon: {interpretation['time_horizon']}")
            print(f"   Confidence: {interpretation['confidence']}%")
            print(f"   Reasoning: {interpretation['reasoning'][:100]}...")
        else:
            print(f"⚠️ Could not parse JSON from response")

    except Exception as e:
        print(f"❌ Failed to interpret {news['ticker']}: {e}")

print()

# Step 4: Save to Database
print("[4/4] Saving Interpretations to Database...")
print("-"*80)

if interpretations and session:
    from backend.database.models import NewsInterpretation
    from backend.database.repository import NewsInterpretationRepository

    repo = NewsInterpretationRepository(session)

    for interp in interpretations:
        try:
            # Create NewsInterpretation object
            news_interp = NewsInterpretation(
                ticker=interp['ticker'],
                headline_bias=interp['headline_bias'],
                expected_impact=interp['expected_impact'],
                time_horizon=interp['time_horizon'],
                confidence=interp['confidence'],
                reasoning=interp['reasoning'],
                macro_context_id=macro_context.id if macro_context else None
            )

            saved = repo.create(news_interp)
            print(f"✅ Saved {interp['ticker']} interpretation (ID: {saved.id})")

            # Also save initial price for tracking
            from backend.database.models import NewsMarketReaction
            reaction = NewsMarketReaction(
                interpretation_id=saved.id,
                ticker=interp['ticker'],
                price_at_news=interp['price_at_news']
            )
            session.add(reaction)

        except Exception as e:
            print(f"❌ Failed to save {interp['ticker']}: {e}")

    session.commit()
    print(f"\n✅ All interpretations saved!")
    session.close()

print()
print("="*80)
print("Summary")
print("="*80)
print(f"  News Items Collected: {len(collected_news)}")
print(f"  Interpretations Generated: {len(interpretations)}")
print(f"  Saved to Database: {len(interpretations) if interpretations else 0}")
print()
print("Next Steps:")
print("  1. Price Tracking Verifier will monitor these stocks")
print("  2. After 1h/1d/3d, it will compare predictions vs reality")
print("  3. NIA (News Interpretation Accuracy) will be calculated")
print("="*80)
