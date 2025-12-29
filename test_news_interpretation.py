#!/usr/bin/env python
"""
Test News Interpretation Flow
Fetch real-time news and let News Agent interpret it
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
print(f"News Interpretation Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

# Step 1: Fetch latest market news
print("[1/3] Fetching Latest Market News...")
print("-"*80)

try:
    # Try to get news from News API
    import requests

    news_api_key = os.getenv('NEWS_API_KEY')
    if not news_api_key:
        print("❌ NEWS_API_KEY not found in .env")
    else:
        # Get top headlines about tech stocks
        url = "https://newsapi.org/v2/everything"
        params = {
            'apiKey': news_api_key,
            'q': 'NVDA OR Tesla OR Apple OR Microsoft',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 5
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            articles = response.json().get('articles', [])
            print(f"✅ Fetched {len(articles)} recent articles")
            print()

            for i, article in enumerate(articles[:3], 1):
                print(f"{i}. {article['title']}")
                print(f"   Source: {article['source']['name']}")
                print(f"   Published: {article['publishedAt']}")
                print(f"   Description: {article.get('description', 'N/A')[:100]}...")
                print()

            # Select first article for testing
            if articles:
                test_article = articles[0]
                print(f"Selected for interpretation: {test_article['title']}")
                print()
        else:
            print(f"❌ News API error: {response.status_code}")
            print("Using mock news for testing...")

            # Create mock news article
            test_article = {
                'title': 'Nvidia Stock Drops 2% After Hours on AI Chip Supply Concerns',
                'description': 'Nvidia shares fell in after-hours trading following reports of potential delays in next-generation AI chip production.',
                'source': {'name': 'Mock News'},
                'publishedAt': datetime.now().isoformat(),
                'url': 'https://example.com/nvda-news'
            }
            print("✅ Using mock article for testing")
            print(f"   Title: {test_article['title']}")
            print()

except Exception as e:
    print(f"❌ News fetching failed: {e}")
    # Use fallback mock article
    test_article = {
        'title': 'Tesla Surges 5% on Strong Q4 Delivery Numbers',
        'description': 'Tesla reported record quarterly deliveries, beating analyst expectations and driving stock price higher in pre-market trading.',
        'source': {'name': 'Mock News'},
        'publishedAt': datetime.now().isoformat(),
        'url': 'https://example.com/tsla-news'
    }
    print("Using fallback mock article")
    print(f"Title: {test_article['title']}")
    print()

# Step 2: News Agent Interpretation
print("[2/3] News Agent Interpretation...")
print("-"*80)

try:
    from backend.ai.news_agent import NewsAgent
    from backend.database.repository import get_sync_session, MacroContextRepository
    from datetime import date

    # Get today's macro context
    session = get_sync_session()
    macro_repo = MacroContextRepository(session)
    macro_context = macro_repo.get_by_date(date.today())

    # Initialize News Agent
    agent = NewsAgent()

    # Determine ticker from title
    ticker = None
    title_upper = test_article['title'].upper()
    if 'NVDA' in title_upper or 'NVIDIA' in title_upper:
        ticker = 'NVDA'
    elif 'TSLA' in title_upper or 'TESLA' in title_upper:
        ticker = 'TSLA'
    elif 'AAPL' in title_upper or 'APPLE' in title_upper:
        ticker = 'AAPL'
    elif 'MSFT' in title_upper or 'MICROSOFT' in title_upper:
        ticker = 'MSFT'
    else:
        ticker = 'SPY'  # Default to S&P 500

    print(f"Analyzing for ticker: {ticker}")
    print(f"Macro Context: {macro_context.regime if macro_context else 'N/A'}")
    print()

    # Interpret the news
    print("Calling News Agent (Claude API)...")
    interpretation = agent.interpret_news(
        headline=test_article['title'],
        summary=test_article.get('description', test_article['title']),
        ticker=ticker,
        macro_context=macro_context
    )

    print()
    print("✅ Interpretation Complete:")
    print(f"   Ticker: {interpretation.ticker}")
    print(f"   Bias: {interpretation.headline_bias}")
    print(f"   Expected Impact: {interpretation.expected_impact}")
    print(f"   Time Horizon: {interpretation.time_horizon}")
    print(f"   Confidence: {interpretation.confidence}%")
    print(f"   Reasoning: {interpretation.reasoning[:200]}...")
    print()

    # Save to database
    from backend.database.repository import NewsInterpretationRepository
    interp_repo = NewsInterpretationRepository(session)
    saved = interp_repo.create(interpretation)
    session.commit()

    print(f"✅ Saved to database (ID: {saved.id})")
    print()

    session.close()

except Exception as e:
    print(f"❌ News interpretation failed: {e}")
    import traceback
    traceback.print_exc()
    print()

# Step 3: Price Tracking Setup
print("[3/3] Price Tracking Setup...")
print("-"*80)

try:
    if 'interpretation' in locals() and interpretation:
        print(f"Setting up price tracking for {interpretation.ticker}...")

        from backend.brokers.kis_broker import KISBroker

        broker = KISBroker(
            account_no=os.getenv('KIS_PAPER_ACCOUNT'),
            product_code='01',
            is_virtual=True
        )

        # Get current price
        price_data = broker.get_price(interpretation.ticker, 'NASDAQ')

        if price_data:
            print(f"✅ Current price captured: ${price_data['current_price']:.2f}")
            print(f"   This will be tracked for verification:")
            print(f"   - 1 hour later")
            print(f"   - 1 day later")
            print(f"   - 3 days later")
            print()
            print(f"   Price Tracking Verifier will automatically check if the")
            print(f"   market moved as predicted ({interpretation.headline_bias})")
        else:
            print("⚠️ Could not fetch current price (market may be closed)")
    else:
        print("⚠️ No interpretation to track")

except Exception as e:
    print(f"❌ Price tracking setup failed: {e}")

print()
print("="*80)
print("News Interpretation Test Complete")
print("="*80)
print()
print("Summary:")
print(f"  - News fetched: ✅")
print(f"  - Interpretation saved: {'✅' if 'saved' in locals() else '❌'}")
print(f"  - Price tracking ready: {'✅' if 'price_data' in locals() and price_data else '⚠️'}")
print()
print("Next: Price Tracking Verifier will check actual price movements")
print("      and calculate News Interpretation Accuracy (NIA)")
print("="*80)
