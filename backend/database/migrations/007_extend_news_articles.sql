-- Migration 007: Extend news_articles for Historical Data Seeding
-- Date: 2025-12-21
-- Purpose: Add embedding, metadata, and NLP fields

-- Add new columns to news_articles
ALTER TABLE news_articles
ADD COLUMN IF NOT EXISTS embedding FLOAT8[], -- Fallback from VECTOR(1536)
ADD COLUMN IF NOT EXISTS tags TEXT [],
ADD COLUMN IF NOT EXISTS tickers TEXT [],
ADD COLUMN IF NOT EXISTS sentiment_score FLOAT,
ADD COLUMN IF NOT EXISTS sentiment_label VARCHAR(20),
ADD COLUMN IF NOT EXISTS source_category VARCHAR(50),
ADD COLUMN IF NOT EXISTS metadata JSONB,
ADD COLUMN IF NOT EXISTS processed_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(100);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_news_articles_tickers ON news_articles USING GIN (tickers);

CREATE INDEX IF NOT EXISTS idx_news_articles_tags ON news_articles USING GIN (tags);

CREATE INDEX IF NOT EXISTS idx_news_articles_sentiment ON news_articles (sentiment_score);

CREATE INDEX IF NOT EXISTS idx_news_articles_source_category ON news_articles (source_category);

CREATE INDEX IF NOT EXISTS idx_news_articles_processed_at ON news_articles (processed_at);

-- Create vector similarity index (Disabled: pgvector not installed)
-- CREATE INDEX IF NOT EXISTS idx_news_articles_embedding ON news_articles
-- USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create table for tracking data collection progress
CREATE TABLE IF NOT EXISTS data_collection_progress (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    collection_type VARCHAR(50) NOT NULL, -- 'news', 'prices', 'embeddings'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_data_collection_source ON data_collection_progress (source);

CREATE INDEX IF NOT EXISTS idx_data_collection_status ON data_collection_progress (status);

CREATE INDEX IF NOT EXISTS idx_data_collection_dates ON data_collection_progress (start_date, end_date);

-- Create table for news sources configuration
CREATE TABLE IF NOT EXISTS news_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'newsapi', 'rss', 'scraper'
    category VARCHAR(50), -- 'financial', 'tech', 'general'
    priority INTEGER DEFAULT 5, -- 1-10, higher = more important
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER, -- requests per day
    config JSONB, -- source-specific configuration
    last_crawled_at TIMESTAMPTZ,
    total_articles INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default news sources
INSERT INTO
    news_sources (
        name,
        source_type,
        category,
        priority,
        rate_limit,
        config
    )
VALUES (
        'NewsAPI',
        'newsapi',
        'financial',
        9,
        100,
        '{"endpoint": "https://newsapi.org/v2/everything"}'
    ),
    (
        'Google News RSS',
        'rss',
        'general',
        7,
        1000,
        '{"url": "https://news.google.com/rss"}'
    ),
    (
        'Yahoo Finance News',
        'scraper',
        'financial',
        8,
        500,
        '{"base_url": "https://finance.yahoo.com"}'
    ),
    (
        'Reuters RSS',
        'rss',
        'financial',
        9,
        1000,
        '{"url": "https://www.reuters.com/markets/rss"}'
    ),
    (
        'Bloomberg RSS',
        'rss',
        'financial',
        10,
        1000,
        '{"url": "https://www.bloomberg.com/feed/podcast/market-news.xml"}'
    )
ON CONFLICT (name) DO NOTHING;

COMMENT ON TABLE news_articles IS 'Enhanced news articles with NLP processing and embeddings';

COMMENT ON TABLE data_collection_progress IS 'Tracks progress of historical data collection jobs';

COMMENT ON TABLE news_sources IS 'Configuration for news crawling sources';