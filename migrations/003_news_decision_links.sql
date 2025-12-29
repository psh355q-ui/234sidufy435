-- Migration for table: news_decision_links
-- Generated: 2025-12-29 22:12:31
-- Description: 뉴스 → 해석 → 의사결정 → 결과 연결 - Accountability Chain

-- ====================================
-- Create Table
-- ====================================

CREATE TABLE IF NOT EXISTS news_decision_links (
    id INTEGER NOT NULL,
    interpretation_id INTEGER NOT NULL,
    debate_session_id INTEGER,
    trading_signal_id INTEGER,
    ticker VARCHAR(20) NOT NULL,
    final_decision VARCHAR(10) NOT NULL,
    decision_outcome VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    profit_loss FLOAT,
    news_influence_weight FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    outcome_verified_at TIMESTAMP,
    PRIMARY KEY (id)
);

-- ====================================
-- Create Indexes
-- ====================================

CREATE INDEX IF NOT EXISTS idx_link_interpretation ON news_decision_links(interpretation_id);
CREATE INDEX IF NOT EXISTS idx_link_debate_session ON news_decision_links(debate_session_id);
CREATE INDEX IF NOT EXISTS idx_link_trading_signal ON news_decision_links(trading_signal_id);
CREATE INDEX IF NOT EXISTS idx_link_ticker ON news_decision_links(ticker);
CREATE INDEX IF NOT EXISTS idx_link_outcome ON news_decision_links(decision_outcome, final_decision);

-- ====================================
-- Column Comments
-- ====================================

COMMENT ON COLUMN news_decision_links.id IS '고유 ID';
COMMENT ON COLUMN news_decision_links.interpretation_id IS '뉴스 해석 ID (Foreign Key)';
COMMENT ON COLUMN news_decision_links.debate_session_id IS 'War Room 토론 세션 ID (Foreign Key)';
COMMENT ON COLUMN news_decision_links.trading_signal_id IS '트레이딩 시그널 ID (Foreign Key)';
COMMENT ON COLUMN news_decision_links.ticker IS '종목 코드';
COMMENT ON COLUMN news_decision_links.final_decision IS '최종 의사결정';
COMMENT ON COLUMN news_decision_links.decision_outcome IS '의사결정 결과';
COMMENT ON COLUMN news_decision_links.profit_loss IS '손익 (%)';
COMMENT ON COLUMN news_decision_links.news_influence_weight IS '뉴스가 의사결정에 미친 영향도 (0.0 ~ 1.0)';
COMMENT ON COLUMN news_decision_links.created_at IS '링크 생성 시각';
COMMENT ON COLUMN news_decision_links.outcome_verified_at IS '결과 검증 시각';

-- Migration complete for news_decision_links

