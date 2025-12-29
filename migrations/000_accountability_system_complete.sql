-- ====================================
-- Accountability System - Complete Migration
-- ====================================
-- Generated: 2025-12-29
-- Description: 6개 테이블 생성 + Foreign Key 제약 조건
-- Phase: 1 (Week 1-2) - Database Foundation
--
-- Tables:
--   1. macro_context_snapshots (독립 테이블 - 먼저 생성)
--   2. news_interpretations
--   3. news_market_reactions
--   4. news_decision_links
--   5. news_narratives
--   6. failure_analysis
-- ====================================

-- ====================================
-- 1. macro_context_snapshots (독립 테이블)
-- ====================================

CREATE TABLE IF NOT EXISTS macro_context_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL UNIQUE,
    regime VARCHAR(30) NOT NULL CHECK (regime IN ('RISK_ON', 'RISK_OFF', 'ROTATION', 'UNCERTAINTY')),
    fed_stance VARCHAR(20) NOT NULL CHECK (fed_stance IN ('HAWKISH', 'DOVISH', 'NEUTRAL')),
    vix_level FLOAT NOT NULL,
    vix_category VARCHAR(20) NOT NULL CHECK (vix_category IN ('LOW', 'NORMAL', 'ELEVATED', 'HIGH', 'EXTREME')),
    sector_rotation VARCHAR(50),
    dominant_narrative TEXT NOT NULL,
    geopolitical_risk VARCHAR(20) NOT NULL CHECK (geopolitical_risk IN ('HIGH', 'MEDIUM', 'LOW')),
    earnings_season BOOLEAN NOT NULL DEFAULT FALSE,
    market_sentiment VARCHAR(20) NOT NULL CHECK (market_sentiment IN ('EXTREME_FEAR', 'FEAR', 'NEUTRAL', 'GREED', 'EXTREME_GREED')),
    sp500_trend VARCHAR(20) NOT NULL CHECK (sp500_trend IN ('STRONG_UPTREND', 'UPTREND', 'SIDEWAYS', 'DOWNTREND', 'STRONG_DOWNTREND')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_macro_snapshot_date ON macro_context_snapshots(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_macro_regime ON macro_context_snapshots(regime, fed_stance);
CREATE INDEX IF NOT EXISTS idx_macro_vix ON macro_context_snapshots(vix_category);
CREATE INDEX IF NOT EXISTS idx_macro_sentiment ON macro_context_snapshots(market_sentiment);

COMMENT ON TABLE macro_context_snapshots IS '거시 경제 상황 스냅샷 - 매일 갱신되는 시장 체제 정보';
COMMENT ON COLUMN macro_context_snapshots.snapshot_date IS '스냅샷 날짜 (일별 unique)';
COMMENT ON COLUMN macro_context_snapshots.regime IS '시장 체제';
COMMENT ON COLUMN macro_context_snapshots.dominant_narrative IS '지배적 서사 (AI 생성)';

-- ====================================
-- 2. news_interpretations
-- ====================================

CREATE TABLE IF NOT EXISTS news_interpretations (
    id SERIAL PRIMARY KEY,
    news_article_id INTEGER NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    headline_bias VARCHAR(20) NOT NULL CHECK (headline_bias IN ('BULLISH', 'BEARISH', 'NEUTRAL')),
    expected_impact VARCHAR(20) NOT NULL CHECK (expected_impact IN ('HIGH', 'MEDIUM', 'LOW')),
    time_horizon VARCHAR(20) NOT NULL CHECK (time_horizon IN ('IMMEDIATE', 'INTRADAY', 'MULTI_DAY')),
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    reasoning TEXT NOT NULL,
    macro_context_id INTEGER,
    interpreted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_interpretation_news_article
        FOREIGN KEY (news_article_id) REFERENCES news_articles(id) ON DELETE CASCADE,
    CONSTRAINT fk_interpretation_macro_context
        FOREIGN KEY (macro_context_id) REFERENCES macro_context_snapshots(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_interpretation_news_article ON news_interpretations(news_article_id);
CREATE INDEX IF NOT EXISTS idx_interpretation_ticker ON news_interpretations(ticker);
CREATE INDEX IF NOT EXISTS idx_interpretation_date ON news_interpretations(interpreted_at);
CREATE INDEX IF NOT EXISTS idx_interpretation_impact ON news_interpretations(expected_impact, headline_bias);

COMMENT ON TABLE news_interpretations IS 'AI의 뉴스 해석 저장 - War Room 실행 중 News Agent가 생성';
COMMENT ON COLUMN news_interpretations.headline_bias IS '헤드라인 편향 (BULLISH/BEARISH/NEUTRAL)';
COMMENT ON COLUMN news_interpretations.expected_impact IS '예상 영향도 (HIGH/MEDIUM/LOW)';
COMMENT ON COLUMN news_interpretations.confidence IS '신뢰도 (0.0 ~ 1.0)';

-- ====================================
-- 3. news_market_reactions
-- ====================================

CREATE TABLE IF NOT EXISTS news_market_reactions (
    id SERIAL PRIMARY KEY,
    interpretation_id INTEGER NOT NULL UNIQUE,
    ticker VARCHAR(20) NOT NULL,
    price_at_news FLOAT NOT NULL,
    price_1h_after FLOAT,
    price_1d_after FLOAT,
    price_3d_after FLOAT,
    actual_price_change_1h FLOAT,
    actual_price_change_1d FLOAT,
    actual_price_change_3d FLOAT,
    interpretation_correct BOOLEAN,
    confidence_justified FLOAT CHECK (confidence_justified >= 0 AND confidence_justified <= 1),
    magnitude_accuracy FLOAT,
    verified_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_reaction_interpretation
        FOREIGN KEY (interpretation_id) REFERENCES news_interpretations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reaction_interpretation ON news_market_reactions(interpretation_id);
CREATE INDEX IF NOT EXISTS idx_reaction_ticker ON news_market_reactions(ticker);
CREATE INDEX IF NOT EXISTS idx_reaction_verified ON news_market_reactions(verified_at);
CREATE INDEX IF NOT EXISTS idx_reaction_correctness ON news_market_reactions(interpretation_correct, confidence_justified);

COMMENT ON TABLE news_market_reactions IS '뉴스 후 실제 시장 반응 검증 - AI 해석의 정확도 측정';
COMMENT ON COLUMN news_market_reactions.interpretation_correct IS '해석 정확 여부 (방향 일치)';
COMMENT ON COLUMN news_market_reactions.confidence_justified IS '신뢰도 적절성 점수 (0.0 ~ 1.0)';

-- ====================================
-- 4. news_decision_links
-- ====================================

CREATE TABLE IF NOT EXISTS news_decision_links (
    id SERIAL PRIMARY KEY,
    interpretation_id INTEGER NOT NULL,
    debate_session_id INTEGER,
    trading_signal_id INTEGER,
    ticker VARCHAR(20) NOT NULL,
    final_decision VARCHAR(10) NOT NULL CHECK (final_decision IN ('BUY', 'SELL', 'HOLD')),
    decision_outcome VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (decision_outcome IN ('SUCCESS', 'FAILURE', 'PENDING')),
    profit_loss FLOAT,
    news_influence_weight FLOAT CHECK (news_influence_weight >= 0 AND news_influence_weight <= 1),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    outcome_verified_at TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_link_interpretation
        FOREIGN KEY (interpretation_id) REFERENCES news_interpretations(id) ON DELETE CASCADE,
    CONSTRAINT fk_link_debate_session
        FOREIGN KEY (debate_session_id) REFERENCES ai_debate_sessions(id) ON DELETE SET NULL,
    CONSTRAINT fk_link_trading_signal
        FOREIGN KEY (trading_signal_id) REFERENCES trading_signals(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_link_interpretation ON news_decision_links(interpretation_id);
CREATE INDEX IF NOT EXISTS idx_link_debate_session ON news_decision_links(debate_session_id);
CREATE INDEX IF NOT EXISTS idx_link_trading_signal ON news_decision_links(trading_signal_id);
CREATE INDEX IF NOT EXISTS idx_link_ticker ON news_decision_links(ticker);
CREATE INDEX IF NOT EXISTS idx_link_outcome ON news_decision_links(decision_outcome, final_decision);

COMMENT ON TABLE news_decision_links IS '뉴스 → 해석 → 의사결정 → 결과 연결 - Accountability Chain';
COMMENT ON COLUMN news_decision_links.news_influence_weight IS '뉴스가 의사결정에 미친 영향도 (0.0 ~ 1.0)';

-- ====================================
-- 5. news_narratives
-- ====================================

CREATE TABLE IF NOT EXISTS news_narratives (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    report_type VARCHAR(20) NOT NULL CHECK (report_type IN ('DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'HALF_YEARLY', 'ANNUAL')),
    page_number INTEGER NOT NULL,
    section VARCHAR(50) NOT NULL,
    narrative_text TEXT NOT NULL,
    interpretation_id INTEGER,
    ticker VARCHAR(20),
    claim_type VARCHAR(30) NOT NULL CHECK (claim_type IN ('PREDICTION', 'ANALYSIS', 'OBSERVATION', 'RECOMMENDATION')),
    accuracy_score FLOAT CHECK (accuracy_score >= 0 AND accuracy_score <= 1),
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_narrative_interpretation
        FOREIGN KEY (interpretation_id) REFERENCES news_interpretations(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_narrative_report_date ON news_narratives(report_date, report_type);
CREATE INDEX IF NOT EXISTS idx_narrative_interpretation ON news_narratives(interpretation_id);
CREATE INDEX IF NOT EXISTS idx_narrative_ticker ON news_narratives(ticker);
CREATE INDEX IF NOT EXISTS idx_narrative_claim_type ON news_narratives(claim_type, verified);
CREATE INDEX IF NOT EXISTS idx_narrative_accuracy ON news_narratives(accuracy_score);

COMMENT ON TABLE news_narratives IS '리포트에 사용된 문장 추적 - 리포트 정확도 측정용';
COMMENT ON COLUMN news_narratives.claim_type IS '주장 유형 (PREDICTION/ANALYSIS/OBSERVATION/RECOMMENDATION)';

-- ====================================
-- 6. failure_analysis
-- ====================================

CREATE TABLE IF NOT EXISTS failure_analysis (
    id SERIAL PRIMARY KEY,
    interpretation_id INTEGER,
    decision_link_id INTEGER,
    ticker VARCHAR(20) NOT NULL,
    failure_type VARCHAR(50) NOT NULL CHECK (failure_type IN ('WRONG_DIRECTION', 'WRONG_MAGNITUDE', 'WRONG_TIMING', 'WRONG_CONFIDENCE', 'MISSED_SIGNAL', 'FALSE_POSITIVE')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    expected_outcome TEXT NOT NULL,
    actual_outcome TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    lesson_learned TEXT NOT NULL,
    recommended_fix TEXT NOT NULL,
    fix_applied BOOLEAN NOT NULL DEFAULT FALSE,
    fix_description TEXT,
    fix_effective BOOLEAN,
    rag_context_updated BOOLEAN NOT NULL DEFAULT FALSE,
    analyzed_by VARCHAR(50) NOT NULL DEFAULT 'failure_learning_agent',
    analyzed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_failure_interpretation
        FOREIGN KEY (interpretation_id) REFERENCES news_interpretations(id) ON DELETE SET NULL,
    CONSTRAINT fk_failure_decision_link
        FOREIGN KEY (decision_link_id) REFERENCES news_decision_links(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_failure_interpretation ON failure_analysis(interpretation_id);
CREATE INDEX IF NOT EXISTS idx_failure_decision_link ON failure_analysis(decision_link_id);
CREATE INDEX IF NOT EXISTS idx_failure_ticker ON failure_analysis(ticker);
CREATE INDEX IF NOT EXISTS idx_failure_type_severity ON failure_analysis(failure_type, severity);
CREATE INDEX IF NOT EXISTS idx_failure_fix_status ON failure_analysis(fix_applied, fix_effective);
CREATE INDEX IF NOT EXISTS idx_failure_analyzed_at ON failure_analysis(analyzed_at);

COMMENT ON TABLE failure_analysis IS '실패 분석 및 학습 저장소 - AI가 틀렸던 판단에 대한 사후 분석';
COMMENT ON COLUMN failure_analysis.failure_type IS '실패 유형 (WRONG_DIRECTION/WRONG_MAGNITUDE/WRONG_TIMING 등)';
COMMENT ON COLUMN failure_analysis.severity IS '심각도 (CRITICAL/HIGH/MEDIUM/LOW)';

-- ====================================
-- Migration Complete
-- ====================================

-- 실행 순서:
-- 1. macro_context_snapshots (독립 테이블)
-- 2. news_interpretations (news_articles, macro_context_snapshots 참조)
-- 3. news_market_reactions (news_interpretations 참조)
-- 4. news_decision_links (news_interpretations, ai_debate_sessions, trading_signals 참조)
-- 5. news_narratives (news_interpretations 참조)
-- 6. failure_analysis (news_interpretations, news_decision_links 참조)

-- 주의사항:
-- - news_articles, ai_debate_sessions, trading_signals 테이블이 먼저 존재해야 함
-- - SERIAL은 PostgreSQL의 auto_increment
-- - CHECK 제약 조건으로 enum 값 강제
-- - CASCADE/SET NULL로 데이터 무결성 보장
