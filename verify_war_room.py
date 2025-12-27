import asyncio
import os
import sys
import json
from datetime import datetime

# 현재 파일의 상위 상위 상위 상위 폴더(프로젝트 루트)를 sys.path에 추가
# 이 파일 위치: project_root/verify_war_room.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir # root
sys.path.append(project_root)

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# .env 로드
load_dotenv(os.path.join(project_root, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL is not set in .env")
    sys.exit(1)

if "postgresql://" in DATABASE_URL and "asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def verify_war_room_data():
    print("="*80)
    print("🔍 War Room Data Verification")
    print("="*80)
    
    engine = create_async_engine(DATABASE_URL, echo=False)

    try:
        async with engine.begin() as conn:
            # 1. 최신 세션 조회
            result = await conn.execute(text("""
                SELECT * FROM ai_debate_sessions 
                ORDER BY created_at DESC 
                LIMIT 1
            """))
            session = result.mappings().first()

            if not session:
                print("❌ No War Room sessions found.")
            else:
                print(f"✅ Latest Session Found: ID {session.get('id')} ({session.get('ticker')})")
                print(f"   Created At: {session.get('created_at')}")
                
                # Check stored columns
                print(f"   consensus_action: {session.get('consensus_action')}")
                print(f"   consensus_confidence: {session.get('consensus_confidence')}")
                
                # Check VOTES column details
                votes = session.get('votes')
                print("-" * 40)
                print(f"   [VOTES COLUMN ANALYSIS]")
                print(f"   Type: {type(votes)}")
                
                if votes is None:
                    print("   ❌ Value: None (NULL in DB)")
                elif isinstance(votes, str):
                    print(f"   ⚠️ Value is STRING (Length: {len(votes)})")
                    print(f"   Content Preview: {votes[:100]}...")
                    try:
                        parsed = json.loads(votes)
                        print(f"   ℹ️ Can be parsed to JSON? YES")
                        print(f"   Parsed Type: {type(parsed)}")
                    except:
                        print(f"   ℹ️ Can be parsed to JSON? NO")
                elif isinstance(votes, list):
                    print(f"   ✅ Value is LIST (Length: {len(votes)})")
                    print(f"   Content: {json.dumps(votes, indent=2, ensure_ascii=False)}")
                elif isinstance(votes, dict):
                    print(f"   ℹ️ Value is DICT (Keys: {list(votes.keys())})")
                    print(f"   Content: {json.dumps(votes, indent=2, ensure_ascii=False)}")
                else:
                    print(f"   ❓ Unknown Type: {votes}")
                print("-" * 40)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_war_room_data())
