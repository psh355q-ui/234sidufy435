"""
Check ai_debate_sessions table for saved War Room sessions

Phase 25.0: Verify 3 test sessions (AAPL, NVDA, GOOGL)
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# DB connection
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    database=os.getenv("POSTGRES_DB", "ai_trading"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD")
)

cursor = conn.cursor()

print("=" * 80)
print("📊 War Room Debate Sessions - Last 24 Hours")
print("=" * 80)

# Get sessions from last 24 hours
yesterday = datetime.now() - timedelta(days=1)

cursor.execute("""
    SELECT
        id,
        ticker,
        consensus_action,
        consensus_confidence,
        trader_vote,
        risk_vote,
        analyst_vote,
        macro_vote,
        institutional_vote,
        news_vote,
        chip_war_vote,
        created_at,
        signal_id
    FROM ai_debate_sessions
    WHERE created_at >= %s
    ORDER BY created_at DESC
""", (yesterday,))

sessions = cursor.fetchall()

if not sessions:
    print("\n⚠️  No sessions found in last 24 hours")
    print("\nℹ️  This might be normal if sessions weren't saved to DB yet.")
else:
    print(f"\n✅ Found {len(sessions)} session(s)\n")

    for session in sessions:
        (id, ticker, consensus_action, consensus_confidence,
         trader_vote, risk_vote, analyst_vote, macro_vote,
         institutional_vote, news_vote, chip_war_vote,
         created_at, signal_id) = session

        print(f"┌─ Session #{id} ───────────────────────────────────")
        print(f"│ 🎯 Ticker: {ticker}")
        print(f"│ 📅 Created: {created_at}")
        print(f"│ ")
        print(f"│ 🤝 Consensus:")
        print(f"│    Action: {consensus_action}")
        print(f"│    Confidence: {consensus_confidence:.1%}")
        print(f"│ ")
        print(f"│ 🗳️  Agent Votes:")
        print(f"│    - Trader: {trader_vote}")
        print(f"│    - Risk: {risk_vote}")
        print(f"│    - Analyst: {analyst_vote}")
        print(f"│    - Macro: {macro_vote}")
        print(f"│    - Institutional: {institutional_vote}")
        print(f"│    - News: {news_vote}")
        print(f"│    - ChipWar: {chip_war_vote or 'N/A'}")
        print(f"│ ")
        print(f"│ 🎲 Signal ID: {signal_id or 'None'}")
        print(f"└────────────────────────────────────────────────\n")

# Summary statistics
print("=" * 80)
print("📈 Summary Statistics")
print("=" * 80)

cursor.execute("""
    SELECT
        COUNT(*) as total_sessions,
        COUNT(DISTINCT ticker) as unique_tickers,
        COUNT(CASE WHEN consensus_action = 'BUY' THEN 1 END) as buy_count,
        COUNT(CASE WHEN consensus_action = 'SELL' THEN 1 END) as sell_count,
        COUNT(CASE WHEN consensus_action = 'HOLD' THEN 1 END) as hold_count,
        AVG(consensus_confidence) as avg_confidence,
        COUNT(chip_war_vote) as chip_war_participated
    FROM ai_debate_sessions
    WHERE created_at >= %s
""", (yesterday,))

stats = cursor.fetchone()

if stats and stats[0] > 0:
    (total, unique_tickers, buy, sell, hold, avg_conf, chip_war_count) = stats

    print(f"\n📊 Sessions: {total}")
    print(f"🎯 Unique Tickers: {unique_tickers}")
    print(f"\n📈 Consensus Distribution:")
    print(f"   BUY:  {buy} ({buy/total*100:.0f}%)")
    print(f"   SELL: {sell} ({sell/total*100:.0f}%)")
    print(f"   HOLD: {hold} ({hold/total*100:.0f}%)")
    print(f"\n🎲 Average Confidence: {avg_conf:.1%}")
    print(f"💎 ChipWar Participated: {chip_war_count}/{total} ({chip_war_count/total*100:.0f}%)")

# Check for today's test tickers (AAPL, NVDA, GOOGL)
print("\n" + "=" * 80)
print("🔍 Today's Test Tickers (AAPL, NVDA, GOOGL)")
print("=" * 80)

test_tickers = ['AAPL', 'NVDA', 'GOOGL']
today = datetime.now().date()

for ticker in test_tickers:
    cursor.execute("""
        SELECT COUNT(*), MAX(created_at)
        FROM ai_debate_sessions
        WHERE ticker = %s
        AND DATE(created_at) = %s
    """, (ticker, today))

    count, last_created = cursor.fetchone()

    if count > 0:
        print(f"✅ {ticker}: {count} session(s), last at {last_created}")
    else:
        print(f"❌ {ticker}: No sessions today")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ Check complete")
print("=" * 80)
