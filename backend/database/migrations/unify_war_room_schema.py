"""
War Room Schema Unification Migration

목적: PM 출력과 DB 스키마를 consensus_action으로 통일
- votes JSONB 추가
- consensus_action 추가
- consensus_confidence 추가
- Phase 25.1 (price_tracking) 호환성 유지
"""

from sqlalchemy import create_engine, text
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
print(f"✓ Loaded .env from: {env_path}")

def get_db_url():
    """DB 연결 문자열 가져오기"""
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/ai_trading')
    # Convert asyncpg to psycopg2 for sync migration
    if 'postgresql+asyncpg://' in db_url:
        db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    return db_url

def run_migration():
    """War Room schema unification migration 실행"""
    engine = create_engine(get_db_url())
    
    print("="*80)
    print("War Room Schema Unification Migration")
    print("="*80)
    print()
    
    with engine.connect() as conn:
        try:
            # 1. votes JSONB 추가
            print("1. Adding votes JSONB column...")
            conn.execute(text("""
                ALTER TABLE ai_debate_sessions 
                ADD COLUMN IF NOT EXISTS votes JSONB
            """))
            conn.commit()
            print("   ✅ votes column added/verified")
            
            # 2. consensus_action 추가
            print("\n2. Adding consensus_action column...")
            conn.execute(text("""
                ALTER TABLE ai_debate_sessions 
                ADD COLUMN IF NOT EXISTS consensus_action VARCHAR(10)
            """))
            conn.commit()
            print("   ✅ consensus_action column added/verified")
            
            # 3. consensus_confidence 추가
            print("\n3. Adding consensus_confidence column...")
            conn.execute(text("""
                ALTER TABLE ai_debate_sessions 
                ADD COLUMN IF NOT EXISTS consensus_confidence FLOAT
            """))
            conn.commit()
            print("   ✅ consensus_confidence column added/verified")
            
            # 4. duration_seconds 추가
            print("\n4. Adding duration_seconds column...")
            conn.execute(text("""
                ALTER TABLE ai_debate_sessions 
                ADD COLUMN IF NOT EXISTS duration_seconds FLOAT
            """))
            conn.commit()
            print("   ✅ duration_seconds column added/verified")
            
            # 5. 인덱스 생성
            print("\n5. Creating indexes...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_consensus_action 
                ON ai_debate_sessions(consensus_action)
            """))
            conn.commit()
            print("   ✅ Indexes created")
            
            # 5. 검증
            print("\n5. Verifying schema...")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'ai_debate_sessions' 
                AND column_name IN ('votes', 'consensus_action', 'consensus_confidence', 'debate_id')
                ORDER BY column_name
            """))
            
            columns = result.fetchall()
            print("\n   Verified columns:")
            for col in columns:
                null_str = "NULL" if col[2] == 'YES' else "NOT NULL"
                print(f"   - {col[0]:25} {col[1]:25} {null_str}")
            
            print("\n" + "="*80)
            print("✅ Migration completed successfully!")
            print("="*80)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    run_migration()
