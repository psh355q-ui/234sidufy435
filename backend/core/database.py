"""
database.py - DB 연결 및 세션 관리

📊 Data Sources:
    - PostgreSQL Database: asyncpg 드라이버 사용
        - URL: postgresql+asyncpg://...
        - Extensions: pgvector (embedding 검색)
        - Connection Pool: NullPool (async 최적화)

🔗 External Dependencies:
    - SQLAlchemy 2.0+: 비동기 ORM
    - asyncpg: PostgreSQL async 드라이버
    - pgvector: 벡터 유사도 검색 extension

📤 Functions & Classes:
    - get_db(): FastAPI Dependency Injection용 세션 생성기
    - init_db(): 테이블 초기화 (dev only, prod는 Alembic)
    - close_db(): 연결 풀 종료
    - DatabaseSession: async context manager

🔄 Used By (전체 시스템에서 사용):
    - backend/api/*.py: 모든 API 엔드포인트
    - backend/services/*.py: 모든 비즈니스 로직
    - backend/data/*.py: 데이터 수집기
    - backend/scripts/*.py: 초기화 스크립트

📝 Notes:
    - SQLAlchemy 2.0 async API 사용
    - pool_pre_ping=True: 연결 health check
    - NullPool: async에서 커넥션 풀 비활성화
    - expire_on_commit=False: 성능 최적화
    - Alembic migrations for production

Uses SQLAlchemy 2.0+ async API with PostgreSQL + pgvector.
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_trading"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool  # Disable connection pooling for async
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for database sessions.

    Usage:
        async with get_db() as db:
            result = await db.execute(query)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database (create tables).

    Note: This should only be used for development.
    Use Alembic migrations for production.
    """
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized successfully")


async def close_db():
    """Close database connection pool."""
    await engine.dispose()
    logger.info("Database connections closed")


# Context manager for database sessions
class DatabaseSession:
    """Context manager for database sessions."""

    def __init__(self):
        self.session = None

    async def __aenter__(self) -> AsyncSession:
        self.session = AsyncSessionLocal()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()
        return False
