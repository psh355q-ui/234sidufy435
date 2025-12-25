"""
Database Module

SQLAlchemy models and repository layer for persistent storage.
"""

from backend.database.models import (
    Base,
    NewsArticle,
    AnalysisResult,
    TradingSignal,
    BacktestRun,
    BacktestTrade,
    SignalPerformance,
    AIDebateSession,
    GroundingSearchLog,
    GroundingDailyUsage,
    StockPrice,
    DataCollectionProgress,
    NewsSource,
    Order,
    DividendAristocrat
)

from backend.database.repository import (
    NewsRepository,
    AnalysisRepository,
    SignalRepository,
    BacktestRepository,
    PerformanceRepository,
    get_db_session,
    get_sync_session
)

__all__ = [
    # Models
    'Base',
    'NewsArticle',
    'AnalysisResult',
    'TradingSignal',
    'BacktestRun',
    'BacktestTrade',
    'SignalPerformance',
    'AIDebateSession',
    'GroundingSearchLog',
    'GroundingDailyUsage',
    'StockPrice',
    'DataCollectionProgress',
    'NewsSource',
    'Order',
    'DividendAristocrat',

    # Repositories
    'NewsRepository',
    'AnalysisRepository',
    'SignalRepository',
    'BacktestRepository',
    'PerformanceRepository',
    'get_db_session',
    'get_sync_session',
]
