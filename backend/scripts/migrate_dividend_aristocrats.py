"""
migrate_dividend_aristocrats.py - DividendAristocrat 테이블 생성 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from backend.database.models import Base, DividendAristocrat
from backend.core.config import settings

def create_dividend_aristocrats_table():
    """DividendAristocrat 테이블 생성"""
    
    # 동기식 엔진 생성 (AsyncEngine → 동기식 Engine)
    sync_database_url = settings.database_url.replace('postgresql+asyncpg://', 'postgresql://')
    sync_database_url = sync_database_url.replace('+psycopg', '')  # psycopg 제거
    
    print(f"📊 Connecting to database...")
    print(f"   URL: {sync_database_url.split('@')[1] if '@' in sync_database_url else 'localhost'}")  # 비밀번호 숨김
    
    engine = create_engine(sync_database_url)
    
    print("\n🔧 Creating dividend_aristocrats table...")
    
    try:
        # DividendAristocrat 테이블만 생성 (이미 있으면 건너뜀)
        DividendAristocrat.__table__.create(engine, checkfirst=True)
        
        print("✅ dividend_aristocrats table created successfully!")
        print(f"\n   Table: {DividendAristocrat.__tablename__}")
        print(f"   Columns:")
        for column in DividendAristocrat.__table__.columns:
            print(f"      - {column.name}: {column.type}")
        
        print(f"\n   Indexes:")
        for index in DividendAristocrat.__table__.indexes:
            print(f"      - {index.name}")
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        raise
    finally:
        engine.dispose()
    
    print("\n🎉 Migration completed!")
    print("\nNext steps:")
    print("1. Load data: http://localhost:8001/api/dividend/aristocrats?force_refresh=true")
    print("2. Check frontend: http://localhost:3002/dividend")

if __name__ == "__main__":
    create_dividend_aristocrats_table()
