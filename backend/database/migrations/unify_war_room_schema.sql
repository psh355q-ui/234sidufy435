-- ============================================================
-- War Room Schema Unification Migration
-- ============================================================
-- 목적: PM 출력과 DB 스키마를 consensus_action으로 통일
-- 실행: pgAdmin Query Tool 또는 psql
-- ============================================================

-- 1. votes JSONB 칼럼 추가 (모든 8개 agent 투표 저장)
ALTER TABLE ai_debate_sessions ADD COLUMN IF NOT EXISTS votes JSONB;

-- 2. consensus_action 칼럼 추가 (PM 최종 결정)
ALTER TABLE ai_debate_sessions
ADD COLUMN IF NOT EXISTS consensus_action VARCHAR(10);

-- 3. consensus_confidence 칼럼 추가 (신뢰도)
ALTER TABLE ai_debate_sessions
ADD COLUMN IF NOT EXISTS consensus_confidence FLOAT;

-- 4. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_consensus_action ON ai_debate_sessions (consensus_action);

CREATE INDEX IF NOT EXISTS idx_created_at ON ai_debate_sessions (created_at);

-- ============================================================
-- 검증 쿼리
-- ============================================================

-- 칼럼 확인
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE
    table_name = 'ai_debate_sessions'
    AND column_name IN (
        'votes',
        'consensus_action',
        'consensus_confidence',
        'debate_id'
    )
ORDER BY column_name;

-- 인덱스 확인
SELECT indexname, indexdef
FROM pg_indexes
WHERE
    tablename = 'ai_debate_sessions'
    AND indexname IN (
        'idx_consensus_action',
        'idx_created_at',
        'idx_debate_debate_id'
    );

-- 완료 메시지
SELECT '✅ War Room Schema Unification Complete!' as status;