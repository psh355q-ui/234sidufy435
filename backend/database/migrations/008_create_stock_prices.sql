-- Migration 008: Create stock_prices table for Historical Price Data
-- Date: 2025-12-21
-- Purpose: Store OHLCV stock price data for backtesting

-- Create stock_prices table
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,

    -- OHLCV data
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL,
    adj_close DECIMAL(12, 4) NOT NULL,

    -- Metadata
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT stock_prices_unique UNIQUE (ticker, date),
    CONSTRAINT stock_prices_prices_valid CHECK (
        open > 0 AND high > 0 AND low > 0 AND close > 0 AND adj_close > 0
    ),
    CONSTRAINT stock_prices_high_low_valid CHECK (high >= low),
    CONSTRAINT stock_prices_volume_valid CHECK (volume >= 0)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker ON stock_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(date);
CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker_date ON stock_prices(ticker, date);
CREATE INDEX IF NOT EXISTS idx_stock_prices_created_at ON stock_prices(created_at);

-- Create TimescaleDB hypertable for time-series optimization
-- Note: Only run if TimescaleDB extension is installed
DO $$
BEGIN
    -- Check if TimescaleDB is available
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'
    ) THEN
        -- Convert to hypertable
        PERFORM create_hypertable(
            'stock_prices',
            'date',
            if_not_exists => TRUE,
            migrate_data => TRUE
        );

        RAISE NOTICE 'TimescaleDB hypertable created for stock_prices';
    ELSE
        RAISE NOTICE 'TimescaleDB not available, using regular table';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'TimescaleDB hypertable creation skipped: %', SQLERRM;
END $$;

-- Create view for latest prices
CREATE OR REPLACE VIEW latest_stock_prices AS
SELECT DISTINCT ON (ticker)
    ticker,
    date,
    close,
    adj_close,
    volume
FROM stock_prices
ORDER BY ticker, date DESC;

COMMENT ON TABLE stock_prices IS 'Historical OHLCV stock price data for backtesting';
COMMENT ON VIEW latest_stock_prices IS 'Latest price for each ticker';
