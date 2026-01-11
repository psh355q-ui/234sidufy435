# API Schema Review Report: Multi-Strategy Orchestration (Phase 0, T0.4)

**Reviewer**: Gemini 2.0 Flash Thinking
**Date**: 2026-01-11
**Target**: `backend/api/schemas/strategy_schemas.py`

---

## 📊 종합 평가

| 카테고리 | 점수 | 요약 |
|----------|------|------|
| **유효성 검증** | 🌟 Excellent | 정규식(`name`), 범위(`priority`), 대문자 변환(`ticker`) 등 Validator가 철저하게 구현되었습니다. |
| **타입 일관성** | ✅ Good | `Base`, `Create`, `Response`의 DTO 패턴이 명확하며, `orm_mode = True` 설정이 빠짐없이 적용되었습니다. |
| **Nested 모델** | 🌟 Excellent | `PositionOwnershipResponse`에 `StrategyResponse`를 포함시키면서, ORM의 `lazy='joined'` 전략과 완벽하게 매칭됩니다. |
| **확장성** | ✅ Good | `ConfigMetadata`를 위한 구체적인 스키마(`TradingConfigMetadata` 등)를 정의해두어 향후 JSONB 검증의 기반을 마련했습니다. |

---

## 1. 🛡️ 필드 검증 규칙 및 Validator

### ✅ 강점
1.  **Strict Validation**:
    -   `Strategy.priority`: 0~1000 범위 제한 (`ge=0, le=1000`)으로 비즈니스 로직 오류 방지.
    -   `Strategy.name`: `isalnum()` 검증으로 URL 경로 파라미터 안전성 확보.
2.  **Auto Formatting**:
    -   `ticker`: 입력받자마자 대문자로 변환(`uppercase_validator`)하여 대소문자 혼용으로 인한 검색 실패 방지.

### 💡 개선 제안
-   **`config_metadata` Validation**:
    -   현재 `Dict[str, Any]`로 열려 있습니다. 추후 `persona_type`에 따라 동적으로 `TradingConfigMetadata` 등을 검증하는 로직을 Service Layer에 추가해야 합니다.

---

## 2. 🧬 Request/Response 및 Nested 모델

### ✅ 강점
-   **N+1 방지 설계**:
    -   `PositionOwnershipResponse`가 `strategy` 필드를 포함합니다.
    -   이전 T0.2에서 `relationship(..., lazy='joined')` 설정을 제안/적용한 것과 맞물려, 추가 쿼리 없이 한 번에 데이터를 가져오는 효율적인 구조입니다.

### ⚠️ 주의사항
-   **`StrategyUpdate.config_metadata`**:
    -   타입이 `Optional[Dict]`입니다. 클라이언트가 이 필드를 보낼 때 "전체 교체"인지 "일부분 병합(Patch)"인지 명확한 계약이 필요합니다. 통상적으로 `PUT`은 교체, `PATCH`는 병합이지만, JSON 컬럼은 구현에 따라 다릅니다.
    -   **권장**: API 계약(T0.5) 단계에서 "JSONB 필드는 Top-level Key 기준 Merge 또는 Replace"임을 명시하십시오.

---

## 3. 🧩 Enum 정의 완전성

`PersonaType`, `TimeHorizon`, `OwnershipType` 등이 DB 컬럼의 Check Constraint와 정확히 일치합니다.

---

## 📝 결론 및 승인

매우 완성도 높은 스키마입니다. 별도의 수정 없이 **승인(Approved)** 합니다.
T0.5 (API 계약 정의) 단계로 넘어가셔도 좋습니다.

**승인 여부**: ✅ **승인 (Approved)**
