-- Migration for table: macro_context_snapshots
-- Generated: 2025-12-29 22:12:31
-- Description: 거시 경제 상황 스냅샷 - 매일 갱신되는 시장 체제 정보

-- ====================================
-- Create Table
-- ====================================

CREATE TABLE IF NOT EXISTS macro_context_snapshots (
    id INTEGER NOT NULL,
    snapshot_date DATE NOT NULL,
    regime VARCHAR(30) NOT NULL,
    fed_stance VARCHAR(20) NOT NULL,
    vix_level FLOAT NOT NULL,
    vix_category VARCHAR(20) NOT NULL,
    sector_rotation VARCHAR(50),
    dominant_narrative TEXT NOT NULL,
    geopolitical_risk VARCHAR(20) NOT NULL,
    earnings_season BOOLEAN NOT NULL DEFAULT False,
    market_sentiment VARCHAR(20) NOT NULL,
    sp500_trend VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

-- ====================================
-- Create Indexes
-- ====================================

CREATE UNIQUE INDEX IF NOT EXISTS idx_macro_snapshot_date ON macro_context_snapshots(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_macro_regime ON macro_context_snapshots(regime, fed_stance);
CREATE INDEX IF NOT EXISTS idx_macro_vix ON macro_context_snapshots(vix_category);
CREATE INDEX IF NOT EXISTS idx_macro_sentiment ON macro_context_snapshots(market_sentiment);

-- ====================================
-- Column Comments
-- ====================================

COMMENT ON COLUMN macro_context_snapshots.id IS '고유 ID';
COMMENT ON COLUMN macro_context_snapshots.snapshot_date IS '스냅샷 날짜 (일별 unique)';
COMMENT ON COLUMN macro_context_snapshots.regime IS '시장 체제';
COMMENT ON COLUMN macro_context_snapshots.fed_stance IS 'Fed 스탠스';
COMMENT ON COLUMN macro_context_snapshots.vix_level IS 'VIX 지수';
COMMENT ON COLUMN macro_context_snapshots.vix_category IS 'VIX 범주';
COMMENT ON COLUMN macro_context_snapshots.sector_rotation IS '섹터 로테이션 방향';
COMMENT ON COLUMN macro_context_snapshots.dominant_narrative IS '지배적 서사 (AI 생성)';
COMMENT ON COLUMN macro_context_snapshots.geopolitical_risk IS '지정학적 리스크 수준';
COMMENT ON COLUMN macro_context_snapshots.earnings_season IS '실적 시즌 여부';
COMMENT ON COLUMN macro_context_snapshots.market_sentiment IS '시장 센티먼트';
COMMENT ON COLUMN macro_context_snapshots.sp500_trend IS 'S&P 500 트렌드';
COMMENT ON COLUMN macro_context_snapshots.created_at IS '레코드 생성 시각';
COMMENT ON COLUMN macro_context_snapshots.updated_at IS '레코드 수정 시각';

-- Migration complete for macro_context_snapshots

