-- Migration for table: news_market_reactions
-- Generated: 2025-12-29 22:12:31
-- Description: 뉴스 후 실제 시장 반응 검증 - AI 해석의 정확도 측정

-- ====================================
-- Create Table
-- ====================================

CREATE TABLE IF NOT EXISTS news_market_reactions (
    id INTEGER NOT NULL,
    interpretation_id INTEGER NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    price_at_news FLOAT NOT NULL,
    price_1h_after FLOAT,
    price_1d_after FLOAT,
    price_3d_after FLOAT,
    actual_price_change_1h FLOAT,
    actual_price_change_1d FLOAT,
    actual_price_change_3d FLOAT,
    interpretation_correct BOOLEAN,
    confidence_justified FLOAT,
    magnitude_accuracy FLOAT,
    verified_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

-- ====================================
-- Create Indexes
-- ====================================

CREATE UNIQUE INDEX IF NOT EXISTS idx_reaction_interpretation ON news_market_reactions(interpretation_id);
CREATE INDEX IF NOT EXISTS idx_reaction_ticker ON news_market_reactions(ticker);
CREATE INDEX IF NOT EXISTS idx_reaction_verified ON news_market_reactions(verified_at);
CREATE INDEX IF NOT EXISTS idx_reaction_correctness ON news_market_reactions(interpretation_correct, confidence_justified);

-- ====================================
-- Column Comments
-- ====================================

COMMENT ON COLUMN news_market_reactions.id IS '고유 ID';
COMMENT ON COLUMN news_market_reactions.interpretation_id IS '뉴스 해석 ID (Foreign Key)';
COMMENT ON COLUMN news_market_reactions.ticker IS '종목 코드';
COMMENT ON COLUMN news_market_reactions.price_at_news IS '뉴스 발생 시점 가격';
COMMENT ON COLUMN news_market_reactions.price_1h_after IS '1시간 후 가격';
COMMENT ON COLUMN news_market_reactions.price_1d_after IS '1일 후 가격';
COMMENT ON COLUMN news_market_reactions.price_3d_after IS '3일 후 가격';
COMMENT ON COLUMN news_market_reactions.actual_price_change_1h IS '1시간 후 가격 변화율 (%)';
COMMENT ON COLUMN news_market_reactions.actual_price_change_1d IS '1일 후 가격 변화율 (%)';
COMMENT ON COLUMN news_market_reactions.actual_price_change_3d IS '3일 후 가격 변화율 (%)';
COMMENT ON COLUMN news_market_reactions.interpretation_correct IS '해석 정확 여부 (방향 일치)';
COMMENT ON COLUMN news_market_reactions.confidence_justified IS '신뢰도 적절성 점수 (0.0 ~ 1.0)';
COMMENT ON COLUMN news_market_reactions.magnitude_accuracy IS '크기 정확도 (예상 vs 실제 차이)';
COMMENT ON COLUMN news_market_reactions.verified_at IS '검증 완료 시각';
COMMENT ON COLUMN news_market_reactions.created_at IS '레코드 생성 시각';

-- Migration complete for news_market_reactions

