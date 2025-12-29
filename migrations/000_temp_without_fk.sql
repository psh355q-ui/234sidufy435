-- Temporary migration: Create accountability tables WITHOUT foreign keys
-- This allows testing without dependent tables (news_articles, ai_debate_sessions, trading_signals)

-- 1. macro_context_snapshots (이미 생성됨, 스킵)

-- 2. news_interpretations (WITHOUT FK to news_articles)
CREATE TABLE IF NOT EXISTS news_interpretations (
    id SERIAL PRIMARY KEY,
    news_article_id INTEGER,  -- FK removed temporarily
    ticker VARCHAR(20) NOT NULL,
    headline_bias VARCHAR(20) CHECK (headline_bias IN ('BULLISH', 'BEARISH', 'NEUTRAL')) NOT NULL,
    expected_impact VARCHAR(20) CHECK (expected_impact IN ('HIGH', 'MEDIUM', 'LOW')) NOT NULL,
    time_horizon VARCHAR(20) CHECK (time_horizon IN ('IMMEDIATE', 'INTRADAY', 'MULTI_DAY')) NOT NULL,
    confidence INTEGER CHECK (confidence >= 0 AND confidence <= 100) NOT NULL,
    reasoning TEXT NOT NULL,
    macro_context_id INTEGER,
    interpreted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (macro_context_id) REFERENCES macro_context_snapshots(id) ON DELETE SET NULL
);

CREATE INDEX idx_news_interpretations_ticker ON news_interpretations(ticker);
CREATE INDEX idx_news_interpretations_interpreted_at ON news_interpretations(interpreted_at);
CREATE INDEX idx_news_interpretations_headline_bias ON news_interpretations(headline_bias);
CREATE INDEX idx_news_interpretations_macro_context_id ON news_interpretations(macro_context_id);

-- 3. news_market_reactions
CREATE TABLE IF NOT EXISTS news_market_reactions (
    id SERIAL PRIMARY KEY,
    interpretation_id INTEGER UNIQUE NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    price_at_news NUMERIC(12, 2),
    price_1h_after NUMERIC(12, 2),
    price_1d_after NUMERIC(12, 2),
    price_3d_after NUMERIC(12, 2),
    actual_price_change_1h NUMERIC(8, 4),
    actual_price_change_1d NUMERIC(8, 4),
    actual_price_change_3d NUMERIC(8, 4),
    interpretation_correct BOOLEAN,
    confidence_justified BOOLEAN,
    magnitude_accuracy NUMERIC(4, 2),
    verified_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interpretation_id) REFERENCES news_interpretations(id) ON DELETE CASCADE
);

CREATE INDEX idx_news_market_reactions_ticker ON news_market_reactions(ticker);
CREATE INDEX idx_news_market_reactions_verified_at ON news_market_reactions(verified_at);
CREATE INDEX idx_news_market_reactions_interpretation_correct ON news_market_reactions(interpretation_correct);

-- 4. news_decision_links (WITHOUT FKs to ai_debate_sessions, trading_signals)
CREATE TABLE IF NOT EXISTS news_decision_links (
    id SERIAL PRIMARY KEY,
    interpretation_id INTEGER NOT NULL,
    debate_session_id INTEGER,  -- FK removed temporarily
    trading_signal_id INTEGER,  -- FK removed temporarily
    ticker VARCHAR(20) NOT NULL,
    final_decision VARCHAR(20),
    decision_outcome VARCHAR(20) CHECK (decision_outcome IN ('SUCCESS', 'FAILURE', 'PENDING')),
    profit_loss NUMERIC(12, 2),
    news_influence_weight NUMERIC(4, 2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    outcome_verified_at TIMESTAMP,
    FOREIGN KEY (interpretation_id) REFERENCES news_interpretations(id) ON DELETE CASCADE
);

CREATE INDEX idx_news_decision_links_ticker ON news_decision_links(ticker);
CREATE INDEX idx_news_decision_links_decision_outcome ON news_decision_links(decision_outcome);

-- 5. news_narratives
CREATE TABLE IF NOT EXISTS news_narratives (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    report_type VARCHAR(20) CHECK (report_type IN ('DAILY', 'WEEKLY', 'MONTHLY', 'ANNUAL')) NOT NULL,
    page_number INTEGER,
    section VARCHAR(100),
    narrative_text TEXT NOT NULL,
    interpretation_id INTEGER,
    ticker VARCHAR(20),
    claim_type VARCHAR(50),
    accuracy_score NUMERIC(4, 2),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    FOREIGN KEY (interpretation_id) REFERENCES news_interpretations(id) ON DELETE SET NULL
);

CREATE INDEX idx_news_narratives_report_date ON news_narratives(report_date);
CREATE INDEX idx_news_narratives_report_type ON news_narratives(report_type);
CREATE INDEX idx_news_narratives_verified ON news_narratives(verified);

-- 6. failure_analysis
CREATE TABLE IF NOT EXISTS failure_analysis (
    id SERIAL PRIMARY KEY,
    interpretation_id INTEGER,
    decision_link_id INTEGER,
    ticker VARCHAR(20) NOT NULL,
    failure_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('CRITICAL', 'MAJOR', 'MINOR')) NOT NULL,
    expected_outcome TEXT,
    actual_outcome TEXT,
    root_cause TEXT NOT NULL,
    lesson_learned TEXT NOT NULL,
    recommended_fix TEXT NOT NULL,
    fix_applied BOOLEAN DEFAULT FALSE,
    fix_description TEXT,
    fix_effective BOOLEAN,
    rag_context_updated BOOLEAN DEFAULT FALSE,
    analyzed_by VARCHAR(100),
    analyzed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (interpretation_id) REFERENCES news_interpretations(id) ON DELETE SET NULL,
    FOREIGN KEY (decision_link_id) REFERENCES news_decision_links(id) ON DELETE SET NULL
);

CREATE INDEX idx_failure_analysis_ticker ON failure_analysis(ticker);
CREATE INDEX idx_failure_analysis_severity ON failure_analysis(severity);
CREATE INDEX idx_failure_analysis_failure_type ON failure_analysis(failure_type);
CREATE INDEX idx_failure_analysis_fix_applied ON failure_analysis(fix_applied);
CREATE INDEX idx_failure_analysis_analyzed_at ON failure_analysis(analyzed_at);

-- Success message
SELECT 'Accountability tables created successfully (without dependent FKs)' AS status;
