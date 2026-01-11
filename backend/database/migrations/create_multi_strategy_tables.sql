-- ====================================
-- Multi-Strategy Orchestration: Create Tables
-- ====================================
-- Generated: 2026-01-11
-- Phase: 0, Task: T0.1
-- Description: 멀티 전략 오케스트레이션을 위한 3개 핵심 테이블 생성
--              1. strategies: 전략 메타데이터 레지스트리
--              2. position_ownership: 포지션 소유권 추적
--              3. conflict_logs: 전략 간 충돌 이력 기록
-- ====================================

-- ====================================
-- 1. strategies (전략 레지스트리)
-- ====================================

CREATE TABLE IF NOT EXISTS strategies (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    persona_type VARCHAR(50) NOT NULL,
    priority INTEGER NOT NULL,
    time_horizon VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    config_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT uk_strategies_name UNIQUE (name)
);

-- Indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_strategies_name ON strategies(name);
CREATE INDEX IF NOT EXISTS idx_strategies_priority ON strategies(priority DESC);
CREATE INDEX IF NOT EXISTS idx_strategies_active ON strategies(is_active) WHERE is_active = TRUE;

-- Comments
COMMENT ON TABLE strategies IS '전략 레지스트리 - 멀티 전략 오케스트레이션을 위한 전략 메타데이터 관리';
COMMENT ON COLUMN strategies.id IS '전략 고유 식별자';
COMMENT ON COLUMN strategies.name IS '전략 시스템명 (trading, long_term, dividend, aggressive 등)';
COMMENT ON COLUMN strategies.display_name IS '사용자 표시용 전략명';
COMMENT ON COLUMN strategies.persona_type IS 'PersonaRouter에서 사용하는 페르소나 타입 (trading, long_term, dividend, aggressive)';
COMMENT ON COLUMN strategies.priority IS '충돌 시 우선순위 (높을수록 우선). long_term=100, dividend=90, trading=50, aggressive=30';
COMMENT ON COLUMN strategies.time_horizon IS '투자 시간 프레임 (short: 1일~1주, medium: 1주~3개월, long: 3개월+)';
COMMENT ON COLUMN strategies.is_active IS '전략 활성화 여부. 비활성화 시 새 주문 생성 차단, 소유권 잠금 해제';
COMMENT ON COLUMN strategies.config_metadata IS '전략별 유연한 설정값 (stop_loss_pct, max_position_size, sector_focus 등)';
COMMENT ON COLUMN strategies.created_at IS '전략 생성 시각';
COMMENT ON COLUMN strategies.updated_at IS '전략 정보 최종 수정 시각';

-- ====================================
-- 2. position_ownership (포지션 소유권)
-- ====================================

CREATE TABLE IF NOT EXISTS position_ownership (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    position_id UUID,
    strategy_id UUID NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    ownership_type VARCHAR(20) NOT NULL,
    locked_until TIMESTAMP WITH TIME ZONE,
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT fk_ownership_strategy FOREIGN KEY (strategy_id)
        REFERENCES strategies(id) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ownership_position ON position_ownership(position_id);
CREATE INDEX IF NOT EXISTS idx_ownership_strategy ON position_ownership(strategy_id);
CREATE INDEX IF NOT EXISTS idx_ownership_ticker ON position_ownership(ticker);
CREATE INDEX IF NOT EXISTS idx_ownership_ticker_strategy ON position_ownership(ticker, strategy_id);
CREATE INDEX IF NOT EXISTS idx_ownership_locked ON position_ownership(locked_until)
    WHERE locked_until IS NOT NULL;

-- Partial Unique Index: primary 소유권은 종목당 1개만
CREATE UNIQUE INDEX IF NOT EXISTS uk_ownership_primary_ticker ON position_ownership(ticker)
    WHERE ownership_type = 'primary';

-- Comments
COMMENT ON TABLE position_ownership IS '포지션 소유권 추적 - 어떤 전략이 어떤 포지션을 소유하는지 관리하여 전략 간 충돌 방지';
COMMENT ON COLUMN position_ownership.id IS '소유권 레코드 고유 식별자';
COMMENT ON COLUMN position_ownership.position_id IS '포지션 ID (positions 테이블 참조). NULL 허용: positions 테이블 미구현 시 ticker로 식별';
COMMENT ON COLUMN position_ownership.strategy_id IS '소유 전략 ID';
COMMENT ON COLUMN position_ownership.ticker IS '종목 코드 (포지션 빠른 조회용 비정규화)';
COMMENT ON COLUMN position_ownership.ownership_type IS '소유권 유형 (primary: 독점 소유, shared: 공유 소유)';
COMMENT ON COLUMN position_ownership.locked_until IS '소유권 잠금 해제 시각. NULL이면 잠금 없음. 시간 경과 시 자동 해제.';
COMMENT ON COLUMN position_ownership.reasoning IS '소유권 설정 이유 (AI 설명 가능성)';
COMMENT ON COLUMN position_ownership.created_at IS '소유권 생성 시각';

-- ====================================
-- 3. conflict_logs (충돌 로그)
-- ====================================

CREATE TABLE IF NOT EXISTS conflict_logs (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    conflicting_strategy_id UUID,
    owning_strategy_id UUID,
    action_attempted VARCHAR(10) NOT NULL,
    action_blocked BOOLEAN NOT NULL,
    resolution VARCHAR(50) NOT NULL,
    reasoning TEXT NOT NULL,
    conflicting_strategy_priority INTEGER,
    owning_strategy_priority INTEGER,
    order_id VARCHAR(100),
    ownership_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT fk_conflict_conflicting_strategy FOREIGN KEY (conflicting_strategy_id)
        REFERENCES strategies(id) ON DELETE SET NULL,
    CONSTRAINT fk_conflict_owning_strategy FOREIGN KEY (owning_strategy_id)
        REFERENCES strategies(id) ON DELETE SET NULL,
    CONSTRAINT fk_conflict_ownership FOREIGN KEY (ownership_id)
        REFERENCES position_ownership(id) ON DELETE SET NULL,
    CONSTRAINT chk_conflict_different_strategies
        CHECK (conflicting_strategy_id != owning_strategy_id OR conflicting_strategy_id IS NULL OR owning_strategy_id IS NULL)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_conflict_ticker ON conflict_logs(ticker);
CREATE INDEX IF NOT EXISTS idx_conflict_created_at ON conflict_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conflict_conflicting_strategy ON conflict_logs(conflicting_strategy_id);
CREATE INDEX IF NOT EXISTS idx_conflict_owning_strategy ON conflict_logs(owning_strategy_id);
CREATE INDEX IF NOT EXISTS idx_conflict_resolution ON conflict_logs(resolution, action_blocked);
CREATE INDEX IF NOT EXISTS idx_conflict_ticker_date ON conflict_logs(ticker, created_at DESC);

-- Comments
COMMENT ON TABLE conflict_logs IS '충돌 로그 - 전략 간 충돌 발생 이력 및 해결 방법 기록. AI 설명 가능성 및 분석용.';
COMMENT ON COLUMN conflict_logs.id IS '충돌 로그 고유 식별자';
COMMENT ON COLUMN conflict_logs.ticker IS '충돌 발생 종목 코드';
COMMENT ON COLUMN conflict_logs.conflicting_strategy_id IS '충돌을 일으킨 전략 ID (새 주문을 시도한 전략)';
COMMENT ON COLUMN conflict_logs.owning_strategy_id IS '기존 소유권을 가진 전략 ID';
COMMENT ON COLUMN conflict_logs.action_attempted IS '시도된 주문 유형 (buy/sell)';
COMMENT ON COLUMN conflict_logs.action_blocked IS '주문 차단 여부. true: 차단됨, false: 허용됨(우선순위 override 등)';
COMMENT ON COLUMN conflict_logs.resolution IS '충돌 해결 방법 (allowed/blocked/priority_override)';
COMMENT ON COLUMN conflict_logs.reasoning IS '충돌 상세 설명 및 해결 이유 (AI 설명 가능성 핵심)';
COMMENT ON COLUMN conflict_logs.conflicting_strategy_priority IS '충돌 시점의 conflicting_strategy 우선순위 (스냅샷)';
COMMENT ON COLUMN conflict_logs.owning_strategy_priority IS '충돌 시점의 owning_strategy 우선순위 (스냅샷)';
COMMENT ON COLUMN conflict_logs.order_id IS '관련 주문 ID (차단된 주문 또는 허용된 주문)';
COMMENT ON COLUMN conflict_logs.ownership_id IS '관련 소유권 레코드 ID';
COMMENT ON COLUMN conflict_logs.created_at IS '충돌 발생 시각';

-- ====================================
-- Seed Data: Default Strategies
-- ====================================

INSERT INTO strategies (name, display_name, persona_type, priority, time_horizon, is_active, config_metadata)
VALUES
    ('long_term', '장기 투자', 'long_term', 100, 'long', TRUE, '{"default_hold_period_days": 90, "sector_focus": ["technology", "healthcare"]}'::JSONB),
    ('dividend', '배당 투자', 'dividend', 90, 'long', TRUE, '{"min_dividend_yield": 3.0, "dividend_growth_years": 10}'::JSONB),
    ('trading', '단기 트레이딩', 'trading', 50, 'short', TRUE, '{"max_hold_days": 7, "stop_loss_pct": 3.0}'::JSONB),
    ('aggressive', '공격적 단타', 'aggressive', 30, 'short', TRUE, '{"max_hold_days": 1, "stop_loss_pct": 5.0}'::JSONB)
ON CONFLICT (name) DO NOTHING;

-- ====================================
-- Verification Queries
-- ====================================

-- Verify table creation
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'strategies') THEN
        RAISE NOTICE 'Table strategies created successfully';
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'position_ownership') THEN
        RAISE NOTICE 'Table position_ownership created successfully';
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'conflict_logs') THEN
        RAISE NOTICE 'Table conflict_logs created successfully';
    END IF;
END $$;

-- ====================================
-- Migration Complete
-- ====================================
