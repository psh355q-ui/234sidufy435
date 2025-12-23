-- Price Tracking Table for 24-hour Performance Measurement
-- Phase 25.1: Agent Performance Tracking
-- Date: 2025-12-23

CREATE TABLE IF NOT EXISTS price_tracking (
    id SERIAL PRIMARY KEY,

    -- Reference to debate session
    session_id INTEGER NOT NULL REFERENCES ai_debate_sessions(id) ON DELETE CASCADE,
    ticker VARCHAR(20) NOT NULL,

    -- Initial price (at debate time)
    initial_price NUMERIC(10, 2) NOT NULL,
    initial_timestamp TIMESTAMP NOT NULL,

    -- 24-hour later price
    final_price NUMERIC(10, 2),
    final_timestamp TIMESTAMP,

    -- Return calculation
    price_change NUMERIC(10, 2),
    return_pct NUMERIC(10, 4),

    -- Consensus from debate
    consensus_action VARCHAR(10) NOT NULL,  -- BUY, SELL, HOLD
    consensus_confidence NUMERIC(5, 4) NOT NULL,

    -- Performance metrics
    is_correct BOOLEAN,  -- Did the action align with price movement?
    performance_score NUMERIC(5, 4),  -- Weighted by confidence

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',  -- PENDING, COMPLETED, FAILED

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    evaluated_at TIMESTAMP,

    -- Metadata
    notes TEXT,

    -- Indexes
    CONSTRAINT unique_session_tracking UNIQUE(session_id)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_price_tracking_ticker ON price_tracking(ticker);
CREATE INDEX IF NOT EXISTS idx_price_tracking_status ON price_tracking(status);
CREATE INDEX IF NOT EXISTS idx_price_tracking_created_at ON price_tracking(created_at);
CREATE INDEX IF NOT EXISTS idx_price_tracking_session_id ON price_tracking(session_id);

-- Comments
COMMENT ON TABLE price_tracking IS 'Track price changes 24 hours after War Room debates for performance measurement';
COMMENT ON COLUMN price_tracking.session_id IS 'Reference to ai_debate_sessions.id';
COMMENT ON COLUMN price_tracking.is_correct IS 'TRUE if BUY → price up, SELL → price down, HOLD → price stable';
COMMENT ON COLUMN price_tracking.performance_score IS 'return_pct * consensus_confidence (weighted performance)';
COMMENT ON COLUMN price_tracking.status IS 'PENDING (waiting for 24h), COMPLETED (evaluated), FAILED (error)';
