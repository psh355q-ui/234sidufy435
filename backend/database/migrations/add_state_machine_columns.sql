-- ====================================
-- Migration: Add State Machine Columns to Orders Table
-- Date: 2026-01-10
-- Description: Phase 1-3 구현 - State Machine, Recovery, Event Bus 지원
-- ====================================

-- 1. Add new columns
ALTER TABLE orders ADD COLUMN IF NOT EXISTS filled_quantity INTEGER;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_metadata JSONB;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS needs_manual_review BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- 2. Update default status from 'pending' to 'idle'
-- (This will not affect existing rows, only new inserts)
ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'idle';

-- 3. Add column comments
COMMENT ON COLUMN orders.filled_quantity IS '체결된 수량 (부분 체결용)';
COMMENT ON COLUMN orders.order_metadata IS '추가 메타데이터 (signal_data, validation_result, broker_info 등)';
COMMENT ON COLUMN orders.needs_manual_review IS '수동 검토 필요 플래그 (Recovery 실패 시)';
COMMENT ON COLUMN orders.updated_at IS '주문 상태 업데이트 시각';

-- 4. Update status column comment to reflect new states
COMMENT ON COLUMN orders.status IS '주문 상태 (OrderState Enum: idle, signal_received, validating, order_pending, order_sent, partial_filled, fully_filled, cancelled, rejected, failed)';

-- 5. Create trigger for updated_at auto-update (PostgreSQL)
CREATE OR REPLACE FUNCTION update_orders_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS orders_updated_at_trigger ON orders;
CREATE TRIGGER orders_updated_at_trigger
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_orders_updated_at();

-- ====================================
-- Migration Notes
-- ====================================
-- 1. filled_quantity: 부분 체결 추적용
-- 2. order_metadata: 유연한 메타데이터 저장 (JSONB) - 'metadata'는 SQLAlchemy 예약어이므로 'order_metadata' 사용
-- 3. needs_manual_review: Recovery 실패 시 수동 검토 플래그
-- 4. updated_at: 상태 전이 시각 추적 (트리거로 자동 업데이트)
-- 5. status default 변경: 'pending' → 'idle' (OrderState.IDLE)

-- Migration complete
