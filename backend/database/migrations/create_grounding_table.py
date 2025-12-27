import asyncio
import os
import sys
import traceback

# 현재 파일의 상위 상위 상위 상위 폴더(프로젝트 루트)를 sys.path에 추가
# 이 파일 위치: backend/database/migrations/create_grounding_table.py
# 프로젝트 루트: backend/..
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
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

# asyncpg 드라이버 사용 확인
if "postgresql://" in DATABASE_URL and "asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def create_tables():
    print(f"📡 Connecting to database...")
    engine = create_async_engine(DATABASE_URL, echo=True)

    try:
        async with engine.begin() as conn:
            print("🛠️ Creating grounding_search_logs table...")
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS grounding_search_logs (
                    id SERIAL PRIMARY KEY,
                    query TEXT NOT NULL,
                    result_count INTEGER NOT NULL DEFAULT 0,
                    search_date TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
                    estimated_cost DOUBLE PRECISION NOT NULL DEFAULT 0.0,
                    response_time_ms INTEGER,
                    metadata JSONB
                );
            """))
            
            print("🛠️ Creating indexes for grounding_search_logs...")
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_grounding_date ON grounding_search_logs (search_date);
            """))

            print("🛠️ Creating grounding_daily_usage table...")
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS grounding_daily_usage (
                    id SERIAL PRIMARY KEY,
                    date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                    search_count INTEGER NOT NULL DEFAULT 0,
                    total_cost DOUBLE PRECISION NOT NULL DEFAULT 0.0
                );
            """))

            print("🛠️ Creating indexes for grounding_daily_usage...")
            # 분리해서 실행하여 에러 위치 파악
            await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_grounding_daily_date_unique ON grounding_daily_usage (date);"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_grounding_daily_date ON grounding_daily_usage (date);"))

        print("✅ Tables created successfully.")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
