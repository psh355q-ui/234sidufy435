import asyncpg
import asyncio
import json

async def compare_pm_and_db():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='Qkqhdi1!',
        database='ai_trading'
    )
    
    try:
        print("="*80)
        print("PM OUTPUT vs DB SCHEMA COMPARISON")
        print("="*80)
        
        # Get DB columns
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'ai_debate_sessions' 
            ORDER BY ordinal_position
        """)
        
        print("\n📊 CURRENT DB SCHEMA (ai_debate_sessions):")
        print("-"*80)
        for col in columns:
            null_str = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  {col['column_name']:30} {col['data_type']:25} {null_str}")
        
        print("\n"*2)
        print("🎯 PM AGENT OUTPUT (_pm_arbitrate):")
        print("-"*80)
        print("""
  return {
      "consensus_action": "BUY/SELL/HOLD",
      "consensus_confidence": 0.72,
      "summary": "War Room 합의: ...",
      "vote_distribution": {"BUY": 0.55, "SELL": 0.08, "HOLD": 0.13}
  }
        """)
        
        print("\n"*2)
        print("💾 WAR_ROOM_ROUTER SAVES:")
        print("-"*80)
        print("""
  session = AIDebateSession(
      ticker=ticker,
      debate_id=debate_id,
      votes=json.dumps(votes),              # ← 8개 agent 투표 전체
      weighted_result=pm_decision["consensus_action"],
      consensus_confidence=pm_decision["consensus_confidence"]
  )
        """)
        
        print("\n"*2)
        print("❌ MISMATCH DETECTED:")
        print("-"*80)
        
        db_columns = {col['column_name'] for col in columns}
        
        code_expects = {
            'votes': 'JSONB',
            'weighted_result': 'VARCHAR',
            'consensus_confidence': 'FLOAT'
        }
        
        for col, dtype in code_expects.items():
            if col in db_columns:
                print(f"  ✅ {col:30} EXISTS in DB")
            else:
                print(f"  ❌ {col:30} MISSING in DB (code expects {dtype})")
        
        print("\n")
        print("  DB has but code doesn't use:")
        code_uses = {'ticker', 'debate_id', 'votes', 'weighted_result', 'consensus_confidence', 
                    'created_at', 'completed_at', 'duration_seconds', 'id'}
        for col in ['chip_war_vote', 'trader_vote', 'consensus_action']:
            if col in db_columns:
                if col not in code_uses:
                    print(f"  ⚠️  {col:30} in DB but not in INSERT")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(compare_pm_and_db())
