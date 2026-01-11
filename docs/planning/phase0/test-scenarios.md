# Test Scenarios: Multi-Strategy Orchestration (Phase 0, T0.6)

**Target**: Multi-Strategy System (Strategy, Ownership, Conflict)
**Verification Scope**: Functional, Concurrency, and Integration

---

## 1. 🧪 Unit & Integration Test Scenarios (Automated)

### 1.1 Strategy Management (Code: `backend/tests/integration/test_strategy_repo.py`)
- [x] **Create Strategy**: 성공적으로 전략 생성 및 DB 저장 확인. (Verified manually)
- [ ] **Constraint Violation**: 중복된 `name`으로 생성 시 `IntegrityError` 발생 확인.
- [ ] **Validation Error**: `priority`가 0-1000 범위를 벗어나거나 `name`에 특수문자 포함 시 에러.
- [ ] **Update Strategy**: JSONB 설정(`config_metadata`) 부분 업데이트 및 `is_active` 상태 변경.

### 1.2 Position Ownership (Code: `backend/tests/integration/test_ownership_repo.py`)
- [ ] **Acquire Primary**: 빈 종목에 대해 `primary` 소유권 획득 성공.
- [ ] **Conflict Acquire**: 이미 주인이 있는 종목에 `primary` 요청 시 실패(Conflict).
- [ ] **Lock Expiry**: `locked_until` 시간이 지났을 때 `is_ticker_locked()`가 `False` 반환.
- [ ] **Transfer Ownership**: A전략 -> B전략 소유권 이전 및 로그 기록 확인.

### 1.3 Conflict Detection & Logging (Code: `backend/tests/integration/test_conflict_repo.py`)
- [ ] **Log Creation**: 충돌 발생 시 `ConflictLog` 생성 및 필수 필드(`reasoning`) 저장 확인.
- [ ] **History Retrieval**: 특정 종목의 최근 7일간 충돌 이력 조회.
- [ ] **Stats Aggregation**: 전략별 충돌 횟수 집계 정확성 검증.

---

## 2. 🚦 System Flow Scenarios (Manual / E2E)

### 2.1 Multi-Strategy Signal Flow
> **Scenario**: "Trading" 전략과 "LongTerm" 전략이 동시에 `AAPL` 매수 시도.
1.  **Setup**: `AAPL`은 현재 소유자 없음.
2.  **Action 1**: "LongTerm"(Priority 100)이 `AAPL` 매수 시도 -> **성공 (Ownership 획득)**.
3.  **Action 2**: "Trading"(Priority 50)이 `AAPL` 매도 시도.
4.  **Expectation**:
    -   Conflict 발생.
    -   Resolution: **Blocked** (우선순위 낮음 & 소유권 없음).
    -   ConflictLog에 기록됨.

### 2.2 Priority Override
> **Scenario**: "Emergency" 전략이 "LongTerm" 전략의 포지션을 청산해야 함.
1.  **Setup**: "LongTerm"(Priority 100)이 `NVDA` 소유.
2.  **Action**: "Emergency"(Priority 999)가 `NVDA` 매도 시도.
3.  **Expectation**:
    -   Conflict 발생.
    -   Resolution: **Priority Override** (999 > 100).
    -   주문 실행 허용.
    -   Ownership이 "Emergency"로 강제 이전됨(또는 해제).

### 2.3 Circuit Breaker (Operational)
> **Scenario**: 특정 전략("Experimental")이 너무 많은 충돌을 유발.
1.  **Monitor**: 최근 1시간 동안 충돌 50회 발생 감지.
2.  **Action**: `StrategyRepository.deactivate("experimental")` 호출.
3.  **Verification**: 해당 전략의 신규 주문이 모두 차단되는지 확인.

---

## 3. 🛡️ Security & Scalability Scenarios

- [ ] **Injection Check**: 전략 이름이나 Ticker에 SQL Injection 패턴 입력 시도시 차단.
- [ ] **Load Test**: 100개 전략이 동시에 0.1초 간격으로 소유권 확인 요청 시 DB 부하 및 응답 속도 측정.

---

## 4. ✅ Acceptance Criteria (Phase 0 종료 조건)

1.  모든 Repository 메서드가 실제 DB(Postgres)에서 정상 동작함. (Partial Done)
2.  `strategies` 테이블에 초기 시드 데이터(4개 Persona)가 생성됨.
3.  API Endpoints(T0.5에서 정의됨)가 Mock으로라도 호출 가능해야 함.
