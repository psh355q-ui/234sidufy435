-- ============================================================
-- War Room DB Migration - Manual SQL Script
-- ============================================================
-- 목적: ai_debate_sessions 테이블에 debate_id 칼럼 추가
-- 실행 방법: psql -U postgres -d ai_trading -f migration.sql
-- ============================================================

-- 1. debate_id 칼럼 추가
ALTER TABLE ai_debate_sessions
ADD COLUMN IF NOT EXISTS debate_id VARCHAR(100);

-- 2. 기존 데이터에 debate_id 자동 생성
UPDATE ai_debate_sessions
SET
    debate_id = 'debate-' || ticker || '-' || to_char(
        created_at,
        'YYYYMMDD-HH24MISS'
    )
WHERE
    debate_id IS NULL;

-- 3. NOT NULL 제약조건 추가
ALTER TABLE ai_debate_sessions ALTER COLUMN debate_id SET NOT NULL;

-- 4. UNIQUE 제약조건 추가
ALTER TABLE ai_debate_sessions
ADD CONSTRAINT uq_debate_id UNIQUE (debate_id);

-- 5. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_debate_debate_id ON ai_debate_sessions (debate_id);

-- ============================================================
-- 확인 쿼리
-- ============================================================

-- 테이블 구조 확인
SELECT
    column_name,
    data_type,
    is_nullable,
    character_maximum_length
FROM information_schema.columns
WHERE
    table_name = 'ai_debate_sessions'
ORDER BY ordinal_position;

-- 제약조건 확인
SELECT
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE
    table_name = 'ai_debate_sessions';

-- 인덱스 확인
SELECT indexname
FROM pg_indexes
WHERE
    tablename = 'ai_debate_sessions';

-- 완료 메시지
SELECT '✅ Migration 완료!' as status;