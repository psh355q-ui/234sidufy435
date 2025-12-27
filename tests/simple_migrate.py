"""
simple_migrate.py - DividendAristocrat 테이블 생성

간단한 독립형 스크립트 - .env 자동 파싱
"""

import os
from pathlib import Path

def read_env_file():
    """Read DATABASE_URL from .env file"""
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        return None
    
    database_url = None
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('DATABASE_URL'):
                # Handle formats: DATABASE_URL=xxx or DATABASE_URL="xxx"
                if '=' in line:
                    value = line.split('=', 1)[1].strip()
                    # Remove quotes if present
                    database_url = value.strip('"').strip("'")
                    break
    
    return database_url

def create_table():
    """Create dividend_aristocrats table"""
    
    database_url = read_env_file()
    
    if not database_url:
        print("❌ .env 파일에서 DATABASE_URL을 찾을 수 없습니다.")
        print("\n.env 파일 예시:")
        print('DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/ai_trading"')
        return
    
    # Convert AsyncEngine URL to sync
    sync_url = database_url
    if 'asyncpg' in sync_url:
        sync_url = sync_url.replace('postgresql+asyncpg://', 'postgresql://')
    if '+psycopg' in sync_url:
        sync_url = sync_url.replace('+psycopg', '')
    
    # Extract host for display (hide password)
    try:
        host_part = sync_url.split('@')[1].split('/')[0] if '@' in sync_url else 'localhost'
        db_name = sync_url.split('/')[-1] if '/' in sync_url else 'unknown'
    except:
        host_part = 'localhost'
        db_name = 'ai_trading'
    
    print(f"📊 Database Connection")
    print(f"   Host: {host_part}")
    print(f"   Database: {db_name}")
    print()
    
    try:
        # Try psycopg2 first (more common)
        try:
            import psycopg2
            print("✓ Using psycopg2")
            conn = psycopg2.connect(sync_url)
        except ImportError:
            # Fall back to psycopg (v3)
            import psycopg
            print("✓ Using psycopg3")
            conn = psycopg.connect(sync_url)
        
        cursor = conn.cursor()
        
        print("\n🔧 Creating table: dividend_aristocrats...")
        
        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dividend_aristocrats (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR NOT NULL UNIQUE,
                company_name VARCHAR NOT NULL,
                sector VARCHAR,
                consecutive_years INTEGER NOT NULL DEFAULT 0,
                total_years INTEGER NOT NULL DEFAULT 0,
                current_yield FLOAT NOT NULL DEFAULT 0.0,
                growth_rate FLOAT NOT NULL DEFAULT 0.0,
                last_dividend FLOAT NOT NULL DEFAULT 0.0,
                analyzed_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create indexes
        print("🔧 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aristocrat_ticker ON dividend_aristocrats(ticker);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aristocrat_consecutive_years ON dividend_aristocrats(consecutive_years);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aristocrat_sector ON dividend_aristocrats(sector);")
        
        conn.commit()
        
        # Verify
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'dividend_aristocrats'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print(f"\n✅ Success! Created table with {len(columns)} columns:")
        for col_name, col_type in columns:
            print(f"      {col_name}: {col_type}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("🎉 Migration Complete!")
        print("="*70)
        print("\nNext Steps:")
        print("  1. Start backend:")
        print("     uvicorn backend.main:app --reload --port 8001")
        print()
        print("  2. Load dividend data (첫 실행, 30-60초 소요):")
        print("     http://localhost:8001/api/dividend/aristocrats?force_refresh=true")
        print()
        print("  3. View on frontend:")
        print("     http://localhost:3002/dividend → 배당 귀족주 탭")
        print("="*70)
        
    except ImportError:
        print("\n❌ Error: psycopg2 not installed")
        print("\nInstall with:")
        print("   pip install psycopg2-binary")
        print("   OR")
        print("   pip install psycopg")
        
    except Exception as e:
        print(f"\n❌ Database Error: {e}")
        print("\n문제 해결:")
        print("  1. PostgreSQL이 실행 중인지 확인")
        print("  2. .env 파일의 DATABASE_URL이 정확한지 확인")
        print("  3. 데이터베이스 ai_trading이 생성되어 있는지 확인")

if __name__ == "__main__":
    create_table()
