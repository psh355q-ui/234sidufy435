# Repository Pattern Design: Multi-Strategy Orchestration (Phase 0, T0.3)

**Designer**: Gemini 2.0 Flash Thinking
**Date**: 2026-01-11
**Target**: `backend/database/repository.py`

---

## 🎯 설계 목표
본 문서는 멀티 전략 오케스트레이션을 위한 3개 핵심 Repository(`Strategy`, `PositionOwnership`, `ConflictLog`)의 인터페이스와 동작 방식을 정의합니다.
**목표**: 비즈니스 로직과 DB 접근 계층의 명확한 분리, 일관된 트랜잭션 처리, 그리고 Type-safe한 CRUD 보장.

---

## 1. 🏗️ Base Repository Strategy
모든 Repository는 공통적인 패턴을 따라야 합니다.

-   **Session Management**: `Depends(get_db)`를 통해 주입받거나, `Context Manager`를 지원해야 합니다.
-   **Type Hinting**: Return type을 명시하여 `Optional[Model]`, `List[Model]` 등을 정확히 표현합니다.
-   **Error Handling**: DB 에러(IntegrityError 등)를 Application 레벨의 커스텀 Exception으로 변환합니다.

---

## 2. 🧩 Repository 상세 설계

### 2.1 StrategyRepository
전략 메타데이터의 조회 및 관리를 담당합니다. **캐싱(Caching)** 패턴 적용이 가장 효과적인 영역입니다.

**Core Methods:**
-   `create(strategy: StrategyCreate) -> Strategy`: 새 전략 등록 (초기 시드 데이터용)
-   `get_by_name(name: str) -> Optional[Strategy]`: 시스템 이름으로 전략 조회 (Hot Path)
-   `get_all(active_only: bool = True) -> List[Strategy]`: 전략 목록 조회

**Specialized Methods:**
-   `get_active_strategies_by_priority() -> List[Strategy]`
    -   **목적**: 충돌 해결 엔진에서 전략 간 우위를 비교하기 위해 사용.
    -   **Query**: `SELECT * FROM strategies WHERE is_active = true ORDER BY priority DESC`
    -   **Optimization**: 쿼리 결과가 적으므로(10개 내외) 애플리케이션 메모리에 캐싱 권장.

-   `update_status(name: str, is_active: bool) -> Strategy`
    -   **목적**: 긴급 상황(Circuit Breaker) 시 특정 전략 비활성화.
    -   **Side Effect**: 비활성화 시 `PositionOwnershipRepository.release_locks_by_strategy(name)` 연쇄 호출 필요.

---

### 2.2 PositionOwnershipRepository
충돌 감지의 핵심입니다. **동시성 제어(Locking)**가 매우 중요합니다.

**Core Methods:**
-   `acquire_ownership(ticker: str, strategy_id: UUID, ...) -> PositionOwnership`
    -   **목적**: 포지션 소유권 획득. 유니크 제약조건(Primary 소유권) 위반 시 에러 처리.

**Specialized Methods:**
-   `get_primary_owner(ticker: str) -> Optional[PositionOwnership]`
    -   **목적**: 충돌 감지기(`ConflictDetector`)가 가장 먼저 호출하는 메서드. 해당 종목의 현재 '주인'을 찾음.
    -   **Query**: `SELECT * FROM position_ownership WHERE ticker = ? AND ownership_type = 'primary'`

-   `is_ticker_locked(ticker: str) -> bool`
    -   **목적**: 현재 잠겨있는지 확인 (`locked_until > NOW()`).

-   `transfer_ownership(ticker: str, from_strategy: UUID, to_strategy: UUID) -> PositionOwnership`
    -   **목적**: 소유권 이전.
    -   **Transaction**:
        1.  `SELECT ... FOR UPDATE` (Row Lock)
        2.  Verify `current_owner == from_strategy`
        3.  Update `strategy_id = to_strategy`
        4.  Log this event (optional, usually done by Service layer)

---

### 2.3 ConflictLogRepository
감사(Audit) 및 분석 목적의 **Insert-Only** 저장소입니다.

**Core Methods:**
-   `create_log(log: ConflictLogCreate) -> ConflictLog`: 충돌 발생 시 비동기로 저장 (Fire-and-forget 권장).

**Specialized Methods:**
-   `get_recent_conflicts(limit: int = 50) -> List[ConflictLogschema]`
    -   **목적**: 대시보드 실시간 알림용. `created_at DESC` 인덱스 활용.

-   `get_conflict_stats_by_ticker(days: int = 7) -> List[Dict]`
    -   **목적**: "어떤 종목이 가장 많이 싸우나?" 분석.
    -   **Query**: `GROUP BY ticker` 집계 쿼리 사용.

---

## 3. ⚙️ 트랜잭션 및 에러 처리 전략

### Transaction Scope (Unit of Work)
Repository 메서드는 기본적으로 **Atomic**해야 하지만, 커밋 시점은 **Service Layer**가 제어하는 것이 좋습니다.
-   **Read Operations**: `autocommit=False` (기본), 별도 커밋 불필요.
-   **Write Operations**: `session.add()`, `session.flush()`까지만 수행하고, 최종 `session.commit()`은 Service가 호출.
    -   *이유*: "소유권 이전" + "로그 저장" + "이벤트 발행"이 하나의 트랜잭션으로 묶여야 하기 때문입니다.

### Error Handling
SQLAlchemy 에러를 그대로 상위로 던지지 않고 래핑합니다.

| DB Error | Custom Exception | 상황 |
|----------|------------------|------|
| `IntegrityError` (Unique) | `StrategyAlreadyExists` / `OwnershipConflict` | 이미 소유권이 있거나 전략명 중복 |
| `IntegrityError` (FK) | `ResourceNotFound` | 존재하지 않는 전략ID 참조 |
| `OperationalError` | `DatabaseConnectionError` | DB 연결 실패 |

---

## 4. 📝 구현 가이드 (for Implementation Agent)

1.  `backend/database/repository.py` 파일을 열고 위 3개 클래스를 추가합니다.
2.  기존 `BaseRepository`가 있다면 상속받고, 없다면 `Session`을 생성자에서 받는 형태로 구현합니다.
3.  **Type Hints** (`List`, `Optional`, `UUID`)를 철저히 사용하세요.
4.  모든 Write 메서드(`create`, `update`, `delete`) 뒤에는 `session.flush()`를 호출하여 ID가 생성되도록 하되, `commit()`은 호출하지 마세요 (Service Layer 위임).

이 설계에 따라 구현을 진행해 주세요.
