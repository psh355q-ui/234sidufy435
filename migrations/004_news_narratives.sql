-- Migration for table: news_narratives
-- Generated: 2025-12-29 22:12:31
-- Description: 리포트에 사용된 문장 추적 - 리포트 정확도 측정용

-- ====================================
-- Create Table
-- ====================================

CREATE TABLE IF NOT EXISTS news_narratives (
    id INTEGER NOT NULL,
    report_date DATE NOT NULL,
    report_type VARCHAR(20) NOT NULL,
    page_number INTEGER NOT NULL,
    section VARCHAR(50) NOT NULL,
    narrative_text TEXT NOT NULL,
    interpretation_id INTEGER,
    ticker VARCHAR(20),
    claim_type VARCHAR(30) NOT NULL,
    accuracy_score FLOAT,
    verified BOOLEAN NOT NULL DEFAULT False,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    PRIMARY KEY (id)
);

-- ====================================
-- Create Indexes
-- ====================================

CREATE INDEX IF NOT EXISTS idx_narrative_report_date ON news_narratives(report_date, report_type);
CREATE INDEX IF NOT EXISTS idx_narrative_interpretation ON news_narratives(interpretation_id);
CREATE INDEX IF NOT EXISTS idx_narrative_ticker ON news_narratives(ticker);
CREATE INDEX IF NOT EXISTS idx_narrative_claim_type ON news_narratives(claim_type, verified);
CREATE INDEX IF NOT EXISTS idx_narrative_accuracy ON news_narratives(accuracy_score);

-- ====================================
-- Column Comments
-- ====================================

COMMENT ON COLUMN news_narratives.id IS '고유 ID';
COMMENT ON COLUMN news_narratives.report_date IS '리포트 날짜';
COMMENT ON COLUMN news_narratives.report_type IS '리포트 타입';
COMMENT ON COLUMN news_narratives.page_number IS '페이지 번호';
COMMENT ON COLUMN news_narratives.section IS '섹션 이름';
COMMENT ON COLUMN news_narratives.narrative_text IS '실제 서술 문장';
COMMENT ON COLUMN news_narratives.interpretation_id IS '관련 뉴스 해석 ID (Foreign Key)';
COMMENT ON COLUMN news_narratives.ticker IS '관련 종목 코드';
COMMENT ON COLUMN news_narratives.claim_type IS '주장 유형';
COMMENT ON COLUMN news_narratives.accuracy_score IS '정확도 점수 (0.0 ~ 1.0) - 나중에 계산';
COMMENT ON COLUMN news_narratives.verified IS '검증 완료 여부';
COMMENT ON COLUMN news_narratives.created_at IS '레코드 생성 시각';
COMMENT ON COLUMN news_narratives.verified_at IS '검증 완료 시각';

-- Migration complete for news_narratives

