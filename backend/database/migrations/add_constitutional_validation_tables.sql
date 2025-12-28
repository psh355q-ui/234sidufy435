-- Migration: Add Constitutional Validation Tables
-- Date: 2025-12-27
-- Purpose: Track constitutional validation results for War Room debates

-- Drop existing tables if they exist (for clean re-run)
DROP TABLE IF EXISTS constitutional_violations CASCADE;
DROP TABLE IF EXISTS constitutional_validations CASCADE;

-- Constitutional validations table
CREATE TABLE constitutional_validations (
    id SERIAL PRIMARY KEY,

    -- Debate reference
    debate_id VARCHAR(100),
    article_id INTEGER,  -- Foreign key removed (news_articles may not exist yet)

    -- Signal details
    ticker VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL,  -- BUY, SELL, HOLD
    confidence FLOAT NOT NULL,

    -- Validation result
    is_constitutional BOOLEAN NOT NULL,
    validation_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Violation summary
    violation_count INTEGER DEFAULT 0,
    violation_severity VARCHAR(20),  -- CRITICAL, HIGH, MODERATE, LOW, NONE

    -- Market context
    market_regime VARCHAR(20),  -- RISK_ON, RISK_OFF, NEUTRAL
    portfolio_state JSONB,

    -- Metadata
    debate_duration_ms FLOAT,
    model_votes JSONB
);

-- Indexes for performance
CREATE INDEX idx_const_val_ticker ON constitutional_validations(ticker);
CREATE INDEX idx_const_val_is_constitutional ON constitutional_validations(is_constitutional);
CREATE INDEX idx_const_val_timestamp ON constitutional_validations(validation_timestamp DESC);
CREATE INDEX idx_const_val_debate_id ON constitutional_validations(debate_id);
CREATE INDEX idx_const_val_article_id ON constitutional_validations(article_id);

-- Constitutional violations table
CREATE TABLE constitutional_violations (
    id SERIAL PRIMARY KEY,

    -- Parent validation
    validation_id INTEGER NOT NULL REFERENCES constitutional_validations(id) ON DELETE CASCADE,

    -- Violation details
    article_number VARCHAR(20) NOT NULL,  -- e.g., "Article 1.1"
    article_title VARCHAR(200) NOT NULL,
    violation_type VARCHAR(50) NOT NULL,  -- e.g., "position_size_exceeded"
    severity VARCHAR(20) NOT NULL,  -- CRITICAL, HIGH, MODERATE, LOW

    -- Violation specifics
    description TEXT NOT NULL,
    expected_value VARCHAR(100),
    actual_value VARCHAR(100),

    -- Remediation
    was_auto_fixed BOOLEAN DEFAULT FALSE,
    fix_description TEXT,

    -- Timestamp
    detected_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_const_vio_validation_id ON constitutional_violations(validation_id);
CREATE INDEX idx_const_vio_article_number ON constitutional_violations(article_number);
CREATE INDEX idx_const_vio_type ON constitutional_violations(violation_type);
CREATE INDEX idx_const_vio_severity ON constitutional_violations(severity);

-- Comments
COMMENT ON TABLE constitutional_validations IS 'Constitutional validation results for War Room debates';
COMMENT ON TABLE constitutional_violations IS 'Specific constitutional violations detected during validation';

COMMENT ON COLUMN constitutional_validations.debate_id IS 'Optional debate tracking ID';
COMMENT ON COLUMN constitutional_validations.is_constitutional IS 'True if signal passed all constitutional checks';
COMMENT ON COLUMN constitutional_validations.violation_severity IS 'Highest severity among all violations';
COMMENT ON COLUMN constitutional_validations.portfolio_state IS 'Snapshot of portfolio at validation time';
COMMENT ON COLUMN constitutional_validations.model_votes IS 'AI model votes in JSON format';

COMMENT ON COLUMN constitutional_violations.article_number IS 'Constitution article number (e.g., Article 1.1)';
COMMENT ON COLUMN constitutional_violations.violation_type IS 'Type of violation (e.g., position_size_exceeded)';
COMMENT ON COLUMN constitutional_violations.was_auto_fixed IS 'Whether violation was automatically remediated';

-- Sample queries for validation

-- Get recent validations
-- SELECT * FROM constitutional_validations ORDER BY validation_timestamp DESC LIMIT 100;

-- Get pass rate by ticker
-- SELECT
--     ticker,
--     COUNT(*) as total,
--     SUM(CASE WHEN is_constitutional THEN 1 ELSE 0 END) as passed,
--     ROUND(SUM(CASE WHEN is_constitutional THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 1) as pass_rate
-- FROM constitutional_validations
-- GROUP BY ticker
-- ORDER BY total DESC;

-- Get most common violations
-- SELECT
--     violation_type,
--     COUNT(*) as count,
--     severity
-- FROM constitutional_violations
-- GROUP BY violation_type, severity
-- ORDER BY count DESC
-- LIMIT 20;

-- Get validation stats for last 7 days
-- SELECT
--     DATE(validation_timestamp) as date,
--     COUNT(*) as total_validations,
--     SUM(CASE WHEN is_constitutional THEN 1 ELSE 0 END) as passed,
--     SUM(CASE WHEN NOT is_constitutional THEN 1 ELSE 0 END) as failed,
--     ROUND(SUM(CASE WHEN is_constitutional THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 1) as pass_rate
-- FROM constitutional_validations
-- WHERE validation_timestamp >= NOW() - INTERVAL '7 days'
-- GROUP BY DATE(validation_timestamp)
-- ORDER BY date DESC;
