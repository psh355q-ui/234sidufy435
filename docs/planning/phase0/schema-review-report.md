# Schema Review Report: Multi-Strategy Orchestration (Phase 0, T0.1)

**Reviewer**: Gemini 2.0 Flash Thinking
**Date**: 2026-01-11
**Target**: `backend/database/migrations/create_multi_strategy_tables.sql` & Schema JSONs

---

## 📊 종합 평가

| 카테고리 | 점수 | 요약 |
|----------|------|------|
| **인덱스 전략** | 🌟 Excellent | 주요 조회 경로(Hot path)에 대한 인덱스가 잘 설계되어 있으며, 부분 유니크 인덱스(`uk_ownership_primary_ticker`) 활용이 돋보입니다. |
| **무결성 설계** | ✅ Good | FK 제약조건(`RESTRICT`, `CASCADE`, `SET NULL`)이 각 테이블의 목적(레지스트리 vs 로그)에 맞게 적절히 설정되었습니다. |
| **유연성** | 🌟 Excellent | `JSONB`를 활용한 전략별 설정 관리로 스키마 변경 없이 다양한 전략 수용이 가능합니다. |
| **성능 예측** | ✅ Good | 헤비한 조인이 필요 없는 비정규화(`ticker` 컬럼 중복) 설계로 고빈도 충돌 감지 로직에 최적화되어 있습니다. |

---

## 1. 🔍 인덱스 전략 최적화 제안

### ✅ 잘된 점 (Keep)
1.  **`uk_ownership_primary_ticker` (Partial Unique Index)**
    -   `WHERE ownership_type = 'primary'` 조건으로 Primary 소유권의 유일성을 DB 레벨에서 강제한 점은 애플리케이션 버그로 인한 데이터 꼬임을 원천 차단하는 훌륭한 패턴입니다.
2.  **`idx_ownership_ticker`**
    -   충돌 감지 로직(`ConflictDetector.check_conflict`)의 핵심 쿼리(`SELECT * FROM position_ownership WHERE ticker = ?`)를 위한 인덱스가 존재하므로 O(log N) 조회가 보장됩니다.
3.  **`idx_strategies_active` (Partial Index)**
    -   활성 전략만 조회하는 패턴에 최적화되어 있습니다.

### 💡 개선 제안 (Optimize)
1.  **`strategies` 테이블 인덱스 다이어트**
    -   **분석**: `strategies` 테이블은 예상 로우가 10개 내외로 매우 작습니다. 이 경우 인덱스 스캔보다 Full Table Scan이 더 빠를 수 있습니다.
    -   **제안**: `idx_strategies_priority`, `idx_strategies_active`는 필수는 아닙니다. 유지해도 해는 없으나, 굳이 필요하지 않을 수 있습니다. (확장성을 위해 유지는 찬성)

2.  **`conflict_logs` 복합 인덱스 순서**
    -   **현재**: `idx_conflict_ticker_date` (`ticker`, `created_at DESC`)
    -   **분석**: 특정 종목의 최근 충돌 이력을 조회할 때 매우 유용합니다. 적절합니다.

---

## 2. 🔗 FK 관계 검증 (CASCADE vs RESTRICT vs SET NULL)

설계된 FK 전략이 비즈니스 로직과 잘 부합하는지 검증했습니다.

| 관계 | 설정 | 검토 의견 |
|------|------|-----------|
| `ownership` -> `strategy` | **RESTRICT** | **적절함**. 소유권이 존재하는 상태에서 전략을 삭제해버리면 고아 포지션이 발생합니다. 전략 삭제 전 소유권 해제를 강제하는 것이 안전합니다. |
| `ownership` -> `position` | **CASCADE** | **적절함**. 실제 포지션이 청산(삭제)되면 소유권 데이터도 자동으로 정리되는 것이 맞습니다. |
| `conflict_logs` -> `strategy` | **SET NULL** | **적절함**. 로그는 '감사(Audit)' 목적이므로 전략이 삭제되어도 기록은 남아야 합니다. 다만 `strategy_priority` 스냅샷 컬럼이 있어 컨텍스트 파악이 가능합니다. |

---

## 3. 📦 JSONB 사용 타당성 분석 (`config_metadata`)

### ✅ 타당성 검증
-   **다양성**: `long_term` 전략은 '보유 기간'이 중요하고, `intraday` 전략은 '시간대 제한'이 중요합니다. 이를 정규화된 컬럼으로 만들면 `NULL`이 많은 sparse table이 됩니다.
-   **쿼리 빈도**: 이 데이터는 주로 애플리케이션 로딩 시점에 한 번 읽혀 메모리에 캐싱되거나, 특정 전략 실행 시에만 참조됩니다. JSONB의 약간의 오버헤드는 문제되지 않습니다.
-   **결론**: **매우 적절한 사용 사례**입니다.

### ⚠️ 주의사항
-   **Schema Validation**: DB 레벨의 스키마 강제가 없으므로, **Pydantic 모델(`backend/api/schemas/strategy_schemas.py`)에서 엄격한 검증**이 필수적입니다. T0.4 단계에서 이를 확실히 챙겨야 합니다.

---

## 4. ⚡ 성능 병목 예측 및 완화 방안

### 🚀 잠재적 병목 구간
1.  **`position_ownership` Lock Contention (동시성)**
    -   **시나리오**: 급변동 장세에서 여러 `scalping` 전략이 동일 종목(`NVDA`)에 대해 동시에 매수 신호를 보내 소유권 획득을 시도할 때.
    -   **영향**: `INSERT/UPDATE` 시 Row-level Lock 대기 발생 가능.
    -   **완화**: `ConflictDetector`에서 DB 트랜잭션을 짧게 가져가야 합니다. 애플리케이션 레벨의 `Redis Lock`이나 `Memory Lock`을 앞단에 두는 것도 고려해볼 만합니다 (Phase 3에서 검토).

2.  **`conflict_logs` Insert Volume**
    -   **시나리오**: 전략 설정 오류로 인해 1초에 수백 번의 충돌이 발생하여 로그가 폭증하는 경우 (Log Flooding).
    -   **영향**: DB I/O 증가.
    -   **완화**:
        -   동일 종목/전략의 반복 충돌에 대한 **Log Throttling** 로직을 애플리케이션(`ConflictDetector`)에 구현해야 합니다. (예: 1분 내 동일 충돌은 1회만 기록)

---

## 📝 결론 및 승인

설계된 스키마는 Phase 0의 목표를 충분히 달성하며, 확장성과 데이터 무결성을 잘 고려했습니다.
별도의 스키마 수정 없이 **T0.2 (SQLAlchemy 모델 정의)** 로 진행해도 좋습니다.

**승인 여부**: ✅ **승인 (Approved)**
