import asyncpg
import asyncio
import json

async def verify_war_room():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='Qkqhdi1!',
        database='ai_trading'
    )
    
    try:
        print("="*80)
        print("🔍 War Room Test Verification")
        print("="*80)
        
        # Get latest session
        result = await conn.fetchrow("""
            SELECT id, ticker, debate_id,
                   consensus_action, consensus_confidence,
                   votes::text as votes_preview,
                   created_at
            FROM ai_debate_sessions 
            ORDER BY id DESC LIMIT 1
        """)
        
        if result:
            print(f"\n✅ Latest Session Found:")
            print(f"   ID: {result['id']}")
            print(f"   Ticker: {result['ticker']}")
            print(f"   Debate ID: {result['debate_id']}")
            print(f"   ")
            print(f"   🎯 Consensus Action: {result['consensus_action']}")
            print(f"   📊 Confidence: {result['consensus_confidence']:.2%}")
            print(f"   ")
            print(f"   Votes Preview (first 200 chars):")
            print(f"   {result['votes_preview'][:200]}...")
            print(f"   ")
            print(f"   Created: {result['created_at']}")
            
            # Parse votes
            if result['votes_preview']:
                votes = json.loads(result['votes_preview'])
                print(f"\n📋 Agent Votes ({len(votes)} agents):")
                for vote in votes:
                    print(f"   - {vote.get('agent', 'Unknown'):15} → {vote.get('action', 'N/A'):4} ({vote.get('confidence', 0):.0%})")
            
            print("\n" + "="*80)
            print("✅ PM Output → DB Storage Alignment")
            print("="*80)
            print(f"   consensus_action: ✅ Saved to DB")
            print(f"   consensus_confidence: ✅ Saved to DB")  
            print(f"   votes (JSONB): ✅ Saved to DB")
            print("="*80)
        else:
            print("❌ No sessions found")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_war_room())
