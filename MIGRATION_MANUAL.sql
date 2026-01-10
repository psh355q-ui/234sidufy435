-- ====================================
-- MANUAL MIGRATION INSTRUCTIONS
-- ====================================
-- Execute this in DBeaver, pgAdmin, or psql
-- Database: ai_trading_system
-- Date: 2026-01-10
-- ====================================

-- Add new columns
ALTER TABLE orders ADD COLUMN IF NOT EXISTS filled_quantity INTEGER;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_metadata JSONB;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS needs_manual_review BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Update default status
ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'idle';

-- Add column comments
COMMENT ON COLUMN orders.filled_quantity IS '체결된 수량 (부분 체결용)';
COMMENT ON COLUMN orders.order_metadata IS '추가 메타데이터 (signal_data, validation_result, broker_info 등)';
COMMENT ON COLUMN orders.needs_manual_review IS '수동 검토 필요 플래그 (Recovery 실패 시)';
COMMENT ON COLUMN orders.updated_at IS '주문 상태 업데이트 시각';

-- Update status column comment
COMMENT ON COLUMN orders.status IS '주문 상태 (OrderState Enum: idle, signal_received, validating, order_pending, order_sent, partial_filled, fully_filled, cancelled, rejected, failed)';

-- Create trigger for updated_at
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
-- Verification
-- ====================================
-- After running the above, verify with:
-- \d orders
-- You should see the new columns:
-- - filled_quantity (integer)
-- - order_metadata (jsonb)
-- - needs_manual_review (boolean)
-- - updated_at (timestamp)
