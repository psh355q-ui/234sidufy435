-- DividendAristocrat 테이블 생성 SQL 스크립트
-- 실행 방법: psql -h localhost -U your_username -d ai_trading -f create_dividend_aristocrats.sql

-- 테이블 생성
CREATE TABLE IF NOT EXISTS dividend_aristocrats (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR NOT NULL UNIQUE,
    company_name VARCHAR NOT NULL,
    sector VARCHAR,
    consecutive_years INTEGER NOT NULL DEFAULT 0,
    total_years INTEGER NOT NULL DEFAULT 0,
    current_yield FLOAT NOT NULL DEFAULT 0.0,
    growth_rate FLOAT NOT NULL DEFAULT 0.0,
    last_dividend FLOAT NOT NULL DEFAULT 0.0,
    analyzed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_aristocrat_ticker ON dividend_aristocrats (ticker);

CREATE INDEX IF NOT EXISTS idx_aristocrat_consecutive_years ON dividend_aristocrats (consecutive_years);

CREATE INDEX IF NOT EXISTS idx_aristocrat_sector ON dividend_aristocrats (sector);

-- 확인
SELECT 'dividend_aristocrats 테이블 생성 완료!' as status;

\d dividend_aristocrats