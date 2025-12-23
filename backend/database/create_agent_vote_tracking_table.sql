-- ============================================================================
-- Agent Vote Tracking Table
--
-- Phase 25.3: Self-Learning Feedback Loop
-- Date: 2025-12-23
--
-- Purpose:
--   개별 에이전트의 투표별 성과를 추적하여 자기학습 피드백 제공
--
-- Features:
--   - 에이전트별 투표 기록 (BUY/SELL/HOLD)
--   - 24시간 후 성과 평가
--   - 에이전트별 정확도 및 성과 스코어 계산
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_vote_tracking (
    id SERIAL PRIMARY KEY,

    -- Session reference
    session_id INTEGER NOT NULL REFERENCES ai_debate_sessions(id),
    price_tracking_id INTEGER REFERENCES price_tracking(id),

    -- Agent info
    agent_name VARCHAR(50) NOT NULL,  -- trader, analyst, risk, macro, institutional, news

    -- Vote details (at debate time)
    vote_action VARCHAR(10) NOT NULL,  -- BUY, SELL, HOLD
    vote_confidence NUMERIC(5, 4) NOT NULL,  -- 0.0000 to 1.0000
    vote_reasoning TEXT,  -- Agent's reasoning for the vote

    -- Ticker info
    ticker VARCHAR(20) NOT NULL,
    initial_price NUMERIC(10, 2) NOT NULL,
    initial_timestamp TIMESTAMP NOT NULL,

    -- 24h evaluation results
    final_price NUMERIC(10, 2),
    final_timestamp TIMESTAMP,
    return_pct NUMERIC(10, 4),  -- Actual return percentage

    -- Performance metrics
    is_correct BOOLEAN,  -- Was the vote correct?
    performance_score NUMERIC(5, 4),  -- Weighted score: return_pct * confidence

    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',  -- PENDING, COMPLETED, FAILED
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    evaluated_at TIMESTAMP,

    -- Constraints
    CONSTRAINT check_vote_action CHECK (vote_action IN ('BUY', 'SELL', 'HOLD')),
    CONSTRAINT check_vote_confidence CHECK (vote_confidence >= 0 AND vote_confidence <= 1),
    CONSTRAINT check_status CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED'))
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Index for agent-specific queries
CREATE INDEX IF NOT EXISTS idx_agent_vote_tracking_agent_name
ON agent_vote_tracking(agent_name);

-- Index for status filtering (PENDING evaluations)
CREATE INDEX IF NOT EXISTS idx_agent_vote_tracking_status
ON agent_vote_tracking(status);

-- Index for time-based queries
CREATE INDEX IF NOT EXISTS idx_agent_vote_tracking_created_at
ON agent_vote_tracking(created_at);

-- Index for session lookups
CREATE INDEX IF NOT EXISTS idx_agent_vote_tracking_session_id
ON agent_vote_tracking(session_id);

-- Index for ticker-based analysis
CREATE INDEX IF NOT EXISTS idx_agent_vote_tracking_ticker
ON agent_vote_tracking(ticker);

-- Composite index for agent performance queries
CREATE INDEX IF NOT EXISTS idx_agent_vote_tracking_agent_status
ON agent_vote_tracking(agent_name, status);

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE agent_vote_tracking IS 'Tracks individual agent votes and their 24-hour performance for self-learning feedback';
COMMENT ON COLUMN agent_vote_tracking.agent_name IS 'Name of the agent who cast the vote (trader, analyst, risk, etc.)';
COMMENT ON COLUMN agent_vote_tracking.vote_action IS 'Agent vote: BUY, SELL, or HOLD';
COMMENT ON COLUMN agent_vote_tracking.vote_confidence IS 'Agent confidence level (0.0 to 1.0)';
COMMENT ON COLUMN agent_vote_tracking.is_correct IS 'Whether the agent vote was correct based on 24h performance';
COMMENT ON COLUMN agent_vote_tracking.performance_score IS 'Weighted performance score: return_pct * confidence';

-- ============================================================================
-- Sample Query Examples
-- ============================================================================

-- Get agent accuracy
-- SELECT
--     agent_name,
--     COUNT(*) as total_votes,
--     SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_votes,
--     ROUND(AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) * 100, 2) as accuracy_pct
-- FROM agent_vote_tracking
-- WHERE status = 'COMPLETED'
-- GROUP BY agent_name
-- ORDER BY accuracy_pct DESC;

-- Get agent performance by action
-- SELECT
--     agent_name,
--     vote_action,
--     COUNT(*) as total,
--     AVG(return_pct) as avg_return,
--     AVG(performance_score) as avg_score
-- FROM agent_vote_tracking
-- WHERE status = 'COMPLETED'
-- GROUP BY agent_name, vote_action
-- ORDER BY agent_name, avg_score DESC;

-- Find low-performing agents (accuracy < 50%)
-- SELECT
--     agent_name,
--     COUNT(*) as total_votes,
--     ROUND(AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) * 100, 2) as accuracy_pct
-- FROM agent_vote_tracking
-- WHERE status = 'COMPLETED'
-- GROUP BY agent_name
-- HAVING AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) < 0.5
-- ORDER BY accuracy_pct ASC;
