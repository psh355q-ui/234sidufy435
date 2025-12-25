"""
models.py - SQLAlchemy 데이터베이스 모델

📊 Data Sources:
    - PostgreSQL (TimescaleDB): 시계열 최적화 DB
        - Hypertables: news_articles, trading_signals, backtest_runs, etc.
        - pgvector: 임베딩 검색 (뉴스 semantic search)
    - 외부 시스템 연동:
        - News: RSS crawler, NewsAPI → NewsArticle
        - Signals: War Room, Deep Reasoning → TradingSignal
        - Orders: KIS Broker → Order
        - Backtest: SignalBacktestEngine → BacktestRun, BacktestTrade

🔗 External Dependencies:
    - SQLAlchemy: ORM 프레임워크
    - pgvector: 벡터 유사도 검색
    - TimescaleDB: 시계열 데이터 압축 및 집계

📤 Database Models (15 classes):
    1. NewsArticle: RSS 뉴스 (embedding, sentiment, tickers)
    2. AnalysisResult: Deep Reasoning 분석 (bull/bear case)
    3. TradingSignal: 매매 시그널 (PRIMARY/HIDDEN/LOSER, 출처 추적)
    4. BacktestRun: 백테스트 실행 (Sharpe, Max DD, 수익률)
    5. BacktestTrade: 백테스트 개별 거래
    6. SignalPerformance: 실제 시그널 성과 (alpha, outcome)
    7. AIDebateSession: War Room 토론 기록 (9 agents vote)
    8. GroundingSearchLog: Grounding API 비용 추적
    9. GroundingDailyUsage: 일일 Grounding 사용량
    10. StockPrice: OHLCV 주가 데이터
    11. DataCollectionProgress: 데이터 수집 작업 진행률
    12. NewsSource: 뉴스 소스 설정
    13. Order: 실제 주문 실행 기록 (KIS Broker)
    14. (배당 모델들은 별도 파일에 정의)

🔄 Imported By (참조가 가장 많음):
    - backend/api/*.py: 모든 API 라우터
    - backend/services/*.py: 모든 서비스
    - backend/data/*.py: 데이터 수집기
    - backend/scripts/*.py: 마이그레이션 스크립트
    - backend/analysis/*.py: 분석 엔진

📝 Notes:
    - TimescaleDB Hypertables: 시계열 데이터 자동 파티션닝
    - pgvector Vector(1536): OpenAI embedding 차원
    - JSONB: 메타데이터 유연한 저장
    - Relationships: SQLAlchemy ORM 관계 설정
    - Indexes: 쿼리 성능 최적화 (GIN, BTREE)
    - Phase 16+: 지속적 확장 중

Database: TimescaleDB (PostgreSQL with time-series extensions)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from pgvector.sqlalchemy import Vector
from datetime import datetime
from typing import Optional

Base = declarative_base()


class NewsArticle(Base):
    """RSS 크롤링된 뉴스 기사"""
    __tablename__ = 'news_articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    source = Column(String(100), nullable=False)  # TechCrunch, Reuters, etc.
    published_date = Column(DateTime, nullable=False)
    crawled_at = Column(DateTime, nullable=False, default=datetime.now)
    content_hash = Column(String(64), nullable=False, unique=True, index=True)

    # NLP & Embedding Fields (Added in Phase 17)
    embedding = Column(ARRAY(Float), nullable=True)  # Fallback: ARRAY(Float)
    tags = Column(ARRAY(String), nullable=True)
    tickers = Column(ARRAY(String), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(20), nullable=True)
    source_category = Column(String(50), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True) # mapped to 'metadata' column
    processed_at = Column(DateTime, nullable=True)
    embedding_model = Column(String(100), nullable=True)

    # Relationships
    analyses = relationship("AnalysisResult", back_populates="article", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_news_published_date', 'published_date'),
        Index('idx_news_source', 'source'),
        Index('idx_news_crawled_at', 'crawled_at'),
        Index('idx_news_tickers', 'tickers', postgresql_using='gin'),
        Index('idx_news_tags', 'tags', postgresql_using='gin'),
        # Vector index would be created via migration, rarely defined in model for basic sync usage
        # Index('idx_news_embedding', 'embedding', postgresql_using='ivfflat', postgresql_ops={'embedding': 'vector_cosine_ops'}, postgresql_with={'lists': 100}),
    )

    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"


class AnalysisResult(Base):
    """Deep Reasoning 분석 결과"""
    __tablename__ = 'analysis_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('news_articles.id'), nullable=False)

    # Analysis metadata
    analyzed_at = Column(DateTime, nullable=False, default=datetime.now)
    model_name = Column(String(50), nullable=False)  # gemini-2.5-pro
    analysis_duration_seconds = Column(Float, nullable=True)

    # Deep Reasoning outputs
    theme = Column(String(200), nullable=False)
    bull_case = Column(Text, nullable=False)
    bear_case = Column(Text, nullable=False)

    # Reasoning trace (3-step CoT)
    step1_direct_impact = Column(Text, nullable=True)
    step2_secondary_impact = Column(Text, nullable=True)
    step3_conclusion = Column(Text, nullable=True)

    # Relationships
    article = relationship("NewsArticle", back_populates="analyses")
    signals = relationship("TradingSignal", back_populates="analysis", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_analysis_analyzed_at', 'analyzed_at'),
        Index('idx_analysis_article_id', 'article_id'),
    )

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, theme='{self.theme}', signals={len(self.signals)})>"


class TradingSignal(Base):
    """생성된 트레이딩 시그널"""
    __tablename__ = 'trading_signals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey('analysis_results.id'), nullable=True)  # 🔄 CHANGED: nullable

    # Signal details
    ticker = Column(String(10), nullable=False, index=True)
    action = Column(String(10), nullable=False)  # BUY, SELL, TRIM, HOLD
    signal_type = Column(String(20), nullable=False, index=True)  # PRIMARY, HIDDEN, LOSER, CONSENSUS
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)
    
    # 🆕 NEW: Source tracking
    source = Column(String(50), nullable=True, index=True)  # war_room, deep_reasoning, manual_analysis, news_analysis

    # Timestamps
    generated_at = Column(DateTime, nullable=False, default=datetime.now)

    # Alert status
    alert_sent = Column(Boolean, default=False)
    alert_sent_at = Column(DateTime, nullable=True)

    # Outcome tracking
    entry_price = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    actual_return_pct = Column(Float, nullable=True)
    outcome_recorded_at = Column(DateTime, nullable=True)

    # Relationships
    analysis = relationship("AnalysisResult", back_populates="signals")

    # Indexes
    __table_args__ = (
        Index('idx_signal_generated_at', 'generated_at'),
        Index('idx_signal_ticker', 'ticker'),
        Index('idx_signal_type', 'signal_type'),
        Index('idx_signal_confidence', 'confidence'),
        Index('idx_signal_ticker_generated', 'ticker', 'generated_at'),
    )

    def __repr__(self):
        return f"<TradingSignal(id={self.id}, ticker='{self.ticker}', action='{self.action}', confidence={self.confidence:.0%})>"


class BacktestRun(Base):
    """백테스트 실행 기록"""
    __tablename__ = 'backtest_runs'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Backtest metadata
    strategy_name = Column(String(100), nullable=False)  # Keyword-Only, CoT+RAG
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    executed_at = Column(DateTime, nullable=False, default=datetime.now)

    # Performance metrics
    total_trades = Column(Integer, nullable=False)
    winning_trades = Column(Integer, nullable=False)
    losing_trades = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)  # %

    avg_return = Column(Float, nullable=False)  # %
    total_return = Column(Float, nullable=False)  # %
    sharpe_ratio = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)  # %

    # Special metrics
    hidden_beneficiaries_found = Column(Integer, default=0)

    # Relationships
    trades = relationship("BacktestTrade", back_populates="backtest_run", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_backtest_executed_at', 'executed_at'),
        Index('idx_backtest_strategy', 'strategy_name'),
        Index('idx_backtest_period', 'start_date', 'end_date'),
    )

    def __repr__(self):
        return f"<BacktestRun(id={self.id}, strategy='{self.strategy_name}', return={self.total_return:.1f}%)>"


class BacktestTrade(Base):
    """백테스트 개별 거래 기록"""
    __tablename__ = 'backtest_trades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    backtest_run_id = Column(Integer, ForeignKey('backtest_runs.id'), nullable=False)

    # Trade details
    ticker = Column(String(10), nullable=False)
    action = Column(String(10), nullable=False)  # BUY, SELL, TRIM
    signal_type = Column(String(20), nullable=False)  # PRIMARY, HIDDEN, LOSER

    # Prices and returns
    entry_date = Column(DateTime, nullable=False)
    exit_date = Column(DateTime, nullable=True)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    return_pct = Column(Float, nullable=True)

    # Context
    reason = Column(Text, nullable=False)
    news_headline = Column(String(500), nullable=True)

    # Relationships
    backtest_run = relationship("BacktestRun", back_populates="trades")

    # Indexes
    __table_args__ = (
        Index('idx_backtest_trade_ticker', 'ticker'),
        Index('idx_backtest_trade_entry_date', 'entry_date'),
        Index('idx_backtest_trade_signal_type', 'signal_type'),
    )

    def __repr__(self):
        return f"<BacktestTrade(id={self.id}, ticker='{self.ticker}', return={self.return_pct:.1f}%)>"


class SignalPerformance(Base):
    """시그널 실제 성과 추적 (Production)"""
    __tablename__ = 'signal_performance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey('trading_signals.id'), nullable=False)

    # Performance tracking
    evaluation_date = Column(DateTime, nullable=False)  # When we checked the outcome
    days_held = Column(Integer, nullable=False)  # How long we held the position

    actual_return_pct = Column(Float, nullable=False)

    # Market context
    spy_return_pct = Column(Float, nullable=True)  # S&P 500 benchmark
    sector_return_pct = Column(Float, nullable=True)  # Sector benchmark

    # Alpha calculation
    alpha = Column(Float, nullable=True)  # Outperformance vs SPY

    # Classification
    outcome = Column(String(20), nullable=False)  # WIN, LOSS, NEUTRAL

    # Indexes
    __table_args__ = (
        Index('idx_signal_perf_signal_id', 'signal_id'),
        Index('idx_signal_perf_evaluation_date', 'evaluation_date'),
        Index('idx_signal_perf_outcome', 'outcome'),
    )

    def __repr__(self):
        return f"<SignalPerformance(signal_id={self.signal_id}, return={self.actual_return_pct:.1f}%, outcome='{self.outcome}')>"


class AIDebateSession(Base):
    """War Room AI Debate 세션 기록 (8 agents)"""
    __tablename__ = 'ai_debate_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Debate context
    ticker = Column(String(10), nullable=False, index=True)

    # Consensus result
    consensus_action = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    consensus_confidence = Column(Float, nullable=False)  # 0.0-1.0

    # Individual agent votes
    trader_vote = Column(String(10), nullable=True)
    risk_vote = Column(String(10), nullable=True)
    analyst_vote = Column(String(10), nullable=True)
    macro_vote = Column(String(10), nullable=True)
    institutional_vote = Column(String(10), nullable=True)
    news_vote = Column(String(10), nullable=True)  # 7th agent
    chip_war_vote = Column(String(10), nullable=True)  # 🆕 8th agent (Phase 24)
    pm_vote = Column(String(10), nullable=True)
    
    # Debate details
    debate_transcript = Column(Text, nullable=True)  # JSON-encoded votes
    
    # Constitutional validation
    constitutional_valid = Column(Boolean, default=True)
    
    # Signal linkage
    signal_id = Column(Integer, ForeignKey('trading_signals.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_debate_ticker', 'ticker'),
        Index('idx_debate_created_at', 'created_at'),
        Index('idx_debate_consensus_action', 'consensus_action'),
    )

    def __repr__(self):
        return f"<AIDebateSession(id={self.id}, ticker='{self.ticker}', consensus='{self.consensus_action}' @ {self.consensus_confidence:.0%})>"


class GroundingSearchLog(Base):
    """Grounding API 검색 비용 추적"""
    __tablename__ = 'grounding_search_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Search details
    ticker = Column(String(10), nullable=False, index=True)
    search_query = Column(Text, nullable=True)
    results_count = Column(Integer, default=0)
    
    # Cost tracking
    cost_usd = Column(Float, default=0.035, nullable=False)
    
    # Emergency context
    emergency_trigger = Column(String(100), nullable=True)
    was_emergency = Column(Boolean, default=False)
    
    # User tracking
    user_id = Column(Integer, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Indexes
    __table_args__ = (
        Index('idx_grounding_created_at', 'created_at'),
        Index('idx_grounding_ticker', 'ticker'),
    )

    def __repr__(self):
        return f"<GroundingSearchLog(id={self.id}, ticker='{self.ticker}', cost=${self.cost_usd})>"


class GroundingDailyUsage(Base):
    """Grounding API 일일 사용량 요약"""
    __tablename__ = 'grounding_daily_usage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    
    # Usage stats
    search_count = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    unique_tickers = Column(Integer, default=0)
    emergency_searches = Column(Integer, default=0)
    
    # Updated timestamp
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Indexes
    __table_args__ = (
        Index('idx_daily_usage_date', 'date'),
    )

    def __repr__(self):
        return f"<GroundingDailyUsage(date={self.date.date()}, searches={self.search_count}, cost=${self.total_cost_usd})>"


# ============================================
# Utility Functions
# ============================================

def create_all_tables(engine):
    """모든 테이블 생성"""
    Base.metadata.create_all(engine)
    print("[DB] All tables created successfully")


def drop_all_tables(engine):
    """모든 테이블 삭제 (주의: 데이터 손실!)"""
    Base.metadata.drop_all(engine)
    print("[DB] All tables dropped")


# TimescaleDB Hypertable 설정
TIMESCALEDB_HYPERTABLES = [
    ("news_articles", "crawled_at"),
    ("analysis_results", "analyzed_at"),
    ("trading_signals", "generated_at"),
    ("backtest_runs", "executed_at"),
    ("signal_performance", "evaluation_date"),
]


def setup_timescaledb_hypertables(connection):
    """
    TimescaleDB hypertable 변환

    Note: TimescaleDB extension이 활성화된 PostgreSQL 필요
    """
    for table_name, time_column in TIMESCALEDB_HYPERTABLES:
        try:
            sql = f"SELECT create_hypertable('{table_name}', '{time_column}', if_not_exists => TRUE);"
            connection.execute(sql)
            print(f"[TimescaleDB] Created hypertable: {table_name} (time_column: {time_column})")
        except Exception as e:
            print(f"[WARNING] Failed to create hypertable {table_name}: {e}")
            print("  This is normal if TimescaleDB extension is not installed")


class StockPrice(Base):
    """Historical Stock Prices (OHLCV)"""
    __tablename__ = 'stock_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column("time", DateTime, nullable=False) # Map 'date' attribute to 'time' column
    
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    adj_close = Column("adjusted_close", Float, nullable=True) # Map attribute to column
    
    source = Column(String(50), default="yfinance")
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_stock_prices_ticker_date', 'ticker', 'time', unique=True),
        Index('idx_stock_prices_date', 'time'),
    )

    def __repr__(self):
        return f"<StockPrice({self.ticker}, {self.date}, {self.close})>"


class DataCollectionProgress(Base):
    """historical data collection job progress"""
    __tablename__ = 'data_collection_progress'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)
    collection_type = Column(String(50), nullable=False) # 'news', 'prices', 'embeddings'
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    status = Column(String(20), default='pending') # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    job_metadata = Column("metadata", JSONB, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index('idx_collection_status', 'status'),
        Index('idx_collection_source', 'source'),
    )


class NewsSource(Base):
    """News Source Configuration"""
    __tablename__ = 'news_sources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    source_type = Column(String(50), nullable=False) # newsapi, rss, scraper
    category = Column(String(50), nullable=True)
    priority = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, nullable=True) # req/day
    config = Column(JSONB, nullable=True)
    
    last_crawled_at = Column(DateTime, nullable=True)
    total_articles = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Order(Base):
    """Trading Orders (KIS Broker Integration)
    
    Phase 26: REAL MODE - 실제 주문 실행 기록
    """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Order details
    ticker = Column(String(10), nullable=False, index=True)
    action = Column(String(10), nullable=False)  # BUY, SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Execution price
    
    # Order type and status
    order_type = Column(String(20), default="MARKET")  # MARKET, LIMIT
    status = Column(String(20), default="PENDING")  # PENDING, FILLED, CANCELLED, REJECTED
    
    # Broker information
    broker = Column(String(50), default="KIS")
    order_id = Column(String(100), nullable=True)  # Broker order ID
    
    # Signal linkage
    signal_id = Column(Integer, ForeignKey('trading_signals.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.now)
    filled_at = Column(DateTime, nullable=True)  # When order was executed
    
    # Execution details
    filled_quantity = Column(Integer, nullable=True)
    filled_price = Column(Float, nullable=True)
    commission = Column(Float, default=0.0)
    
    # Rejection reason (if any)
    reject_reason = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_orders_ticker', 'ticker'),
        Index('idx_orders_status', 'status'),
        Index('idx_orders_created_at', 'created_at'),
        Index('idx_orders_signal_id', 'signal_id'),
    )

    def __repr__(self):
        return f"<Order(id={self.id}, ticker='{self.ticker}', action='{self.action}', quantity={self.quantity}, status='{self.status}')>"


