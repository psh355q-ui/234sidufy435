-- Migration for table: news_interpretations
-- Generated: 2025-12-29 22:12:31
-- Description: AI의 뉴스 해석 저장 - War Room 실행 중 News Agent가 생성

-- ====================================
-- Create Table
-- ====================================

CREATE TABLE IF NOT EXISTS news_interpretations (
    id INTEGER NOT NULL,
    news_article_id INTEGER NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    headline_bias VARCHAR(20) NOT NULL,
    expected_impact VARCHAR(20) NOT NULL,
    time_horizon VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    reasoning TEXT NOT NULL,
    macro_context_id INTEGER,
    interpreted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

-- ====================================
-- Create Indexes
-- ====================================

CREATE INDEX IF NOT EXISTS idx_interpretation_news_article ON news_interpretations(news_article_id);
CREATE INDEX IF NOT EXISTS idx_interpretation_ticker ON news_interpretations(ticker);
CREATE INDEX IF NOT EXISTS idx_interpretation_date ON news_interpretations(interpreted_at);
CREATE INDEX IF NOT EXISTS idx_interpretation_impact ON news_interpretations(expected_impact, headline_bias);

-- ====================================
-- Column Comments
-- ====================================

COMMENT ON COLUMN news_interpretations.id IS '고유 ID';
COMMENT ON COLUMN news_interpretations.news_article_id IS '뉴스 기사 ID (Foreign Key)';
COMMENT ON COLUMN news_interpretations.ticker IS '종목 코드';
COMMENT ON COLUMN news_interpretations.headline_bias IS '헤드라인 편향';
COMMENT ON COLUMN news_interpretations.expected_impact IS '예상 영향도';
COMMENT ON COLUMN news_interpretations.time_horizon IS '시간 지평';
COMMENT ON COLUMN news_interpretations.confidence IS '신뢰도 (0.0 ~ 1.0)';
COMMENT ON COLUMN news_interpretations.reasoning IS '해석 근거';
COMMENT ON COLUMN news_interpretations.macro_context_id IS '거시 경제 컨텍스트 ID (Foreign Key)';
COMMENT ON COLUMN news_interpretations.interpreted_at IS '해석 생성 시각';
COMMENT ON COLUMN news_interpretations.created_at IS '레코드 생성 시각';

-- Migration complete for news_interpretations

