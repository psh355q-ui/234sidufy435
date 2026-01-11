-- ====================================
-- Multi-Strategy Orchestration: Extend positions table
-- ====================================
-- Generated: 2026-01-11
-- Phase: 0, Task: T0.1
-- Description: positions 테이블에 전략 소유권 및 잠금 상태 컬럼 추가
-- ====================================

-- Add primary_strategy_id column
ALTER TABLE positions
ADD COLUMN IF NOT EXISTS primary_strategy_id UUID;

-- Add lock columns
ALTER TABLE positions
ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE;

ALTER TABLE positions
ADD COLUMN IF NOT EXISTS locked_reason TEXT;

-- Add foreign key constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_positions_strategy'
        AND table_name = 'positions'
    ) THEN
        ALTER TABLE positions
        ADD CONSTRAINT fk_positions_strategy
        FOREIGN KEY (primary_strategy_id) REFERENCES strategies(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Create index for strategy_id
CREATE INDEX IF NOT EXISTS idx_positions_strategy_id ON positions(primary_strategy_id);

-- Create composite index for strategy + status queries
CREATE INDEX IF NOT EXISTS idx_positions_strategy_ticker ON positions(primary_strategy_id, ticker);

-- Create index for locked positions
CREATE INDEX IF NOT EXISTS idx_positions_locked ON positions(is_locked) WHERE is_locked = TRUE;

-- Add column comments
COMMENT ON COLUMN positions.primary_strategy_id IS '포지션을 주로 소유하는 전략 ID. position_ownership 테이블과 연동';
COMMENT ON COLUMN positions.is_locked IS '포지션 잠금 상태. TRUE: 다른 전략이 매도/수정 불가';
COMMENT ON COLUMN positions.locked_reason IS '잠금 이유 설명 (AI 설명 가능성)';

-- Verification
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'positions' AND column_name = 'primary_strategy_id'
    ) THEN
        RAISE NOTICE 'Column primary_strategy_id added to positions table successfully';
    END IF;
END $$;

-- ====================================
-- Migration Complete
-- ====================================
