-- Migration for table: failure_analysis
-- Generated: 2025-12-29 22:12:31
-- Description: 실패 분석 및 학습 저장소 - AI가 틀렸던 판단에 대한 사후 분석

-- ====================================
-- Create Table
-- ====================================

CREATE TABLE IF NOT EXISTS failure_analysis (
    id INTEGER NOT NULL,
    interpretation_id INTEGER,
    decision_link_id INTEGER,
    ticker VARCHAR(20) NOT NULL,
    failure_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    expected_outcome TEXT NOT NULL,
    actual_outcome TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    lesson_learned TEXT NOT NULL,
    recommended_fix TEXT NOT NULL,
    fix_applied BOOLEAN NOT NULL DEFAULT False,
    fix_description TEXT,
    fix_effective BOOLEAN,
    rag_context_updated BOOLEAN NOT NULL DEFAULT False,
    analyzed_by VARCHAR(50) NOT NULL DEFAULT 'failure_learning_agent',
    analyzed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

-- ====================================
-- Create Indexes
-- ====================================

CREATE INDEX IF NOT EXISTS idx_failure_interpretation ON failure_analysis(interpretation_id);
CREATE INDEX IF NOT EXISTS idx_failure_decision_link ON failure_analysis(decision_link_id);
CREATE INDEX IF NOT EXISTS idx_failure_ticker ON failure_analysis(ticker);
CREATE INDEX IF NOT EXISTS idx_failure_type_severity ON failure_analysis(failure_type, severity);
CREATE INDEX IF NOT EXISTS idx_failure_fix_status ON failure_analysis(fix_applied, fix_effective);
CREATE INDEX IF NOT EXISTS idx_failure_analyzed_at ON failure_analysis(analyzed_at);

-- ====================================
-- Column Comments
-- ====================================

COMMENT ON COLUMN failure_analysis.id IS '고유 ID';
COMMENT ON COLUMN failure_analysis.interpretation_id IS '관련 뉴스 해석 ID (Foreign Key)';
COMMENT ON COLUMN failure_analysis.decision_link_id IS '관련 의사결정 링크 ID (Foreign Key)';
COMMENT ON COLUMN failure_analysis.ticker IS '종목 코드';
COMMENT ON COLUMN failure_analysis.failure_type IS '실패 유형';
COMMENT ON COLUMN failure_analysis.severity IS '심각도';
COMMENT ON COLUMN failure_analysis.expected_outcome IS '예상했던 결과';
COMMENT ON COLUMN failure_analysis.actual_outcome IS '실제 발생한 결과';
COMMENT ON COLUMN failure_analysis.root_cause IS '근본 원인 분석 (AI 생성)';
COMMENT ON COLUMN failure_analysis.lesson_learned IS '학습한 교훈 (AI 생성)';
COMMENT ON COLUMN failure_analysis.recommended_fix IS '권장 수정 사항 (AI 생성)';
COMMENT ON COLUMN failure_analysis.fix_applied IS '수정 적용 여부';
COMMENT ON COLUMN failure_analysis.fix_description IS '적용된 수정 내용';
COMMENT ON COLUMN failure_analysis.fix_effective IS '수정 효과 여부 (나중에 평가)';
COMMENT ON COLUMN failure_analysis.rag_context_updated IS 'RAG 컨텍스트 업데이트 여부';
COMMENT ON COLUMN failure_analysis.analyzed_by IS '분석 주체';
COMMENT ON COLUMN failure_analysis.analyzed_at IS '분석 시각';
COMMENT ON COLUMN failure_analysis.created_at IS '레코드 생성 시각';
COMMENT ON COLUMN failure_analysis.updated_at IS '레코드 수정 시각';

-- Migration complete for failure_analysis

