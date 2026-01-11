# ORM Review Report: Multi-Strategy Orchestration (Phase 0, T0.2)

**Reviewer**: Gemini 2.0 Flash Thinking
**Date**: 2026-01-11
**Target**: `backend/database/models.py` (Strategy, PositionOwnership, ConflictLog)

---

## 📊 종합 평가

| 카테고리 | 점수 | 요약 |
|----------|------|------|
| **ORM 매핑** | ⚠️ Attention | 기본 구조는 훌륭하나, `relationship`의 `foreign_keys` 파라미터 문법에 잠재적 오류가 발견되었습니다. |
| **N+1 방지** | ⚠️ Warning | 모든 관계가 기본 `lazy='select'`로 설정되어 있어, 리스트 조회 시 N+1 쿼리 발생 위험이 높습니다. |
| **인덱스 정의** | ✅ Good | SQL 스키마와 모델의 `__table_args__`가 일치하며, 쿼리 최적화가 잘 반영되었습니다. |

---

## 1. 🔍 ORM 관계 매핑 검증

### 🚩 발견된 이슈: `foreign_keys` 문법
현재 모델 정의에서 관계 설정 시 아래와 같은 문법이 사용되었습니다:

```python
# 현재 코드
position_ownerships = relationship("PositionOwnership", ..., foreign_keys="[PositionOwnership.strategy_id]")
```

**문제점**: `foreign_keys` 인자는 **컬럼 객체 리스트**(`[val1, val2]`) 또는 **문자열**(`"Class.column"`)을 받습니다. 문자열 내에 대괄호를 포함한 `"['Class.column']"` 형태는 SQLAlchemy 버전이나 설정에 따라 **해석 오류(ArgumentError)**를 일으킬 수 있습니다.

**개선 제안**: 명확성을 위해 문자열 표현 시 대괄호를 제거하거나, 가능하다면 컬럼 객체를 직접 참조하는 것이 안전합니다. 순환 참조 문제로 문자열을 사용해야 한다면 아래 형식을 권장합니다.

```python
# 수정 제안
position_ownerships = relationship(
    "PositionOwnership", 
    back_populates="strategy", 
    foreign_keys="PositionOwnership.strategy_id"  # 대괄호 제거
)
```

### ✅ 관계 방향성 (Backref/Back_populates)
-   `Strategy` <-> `PositionOwnership`: 1:N 관계가 양방향으로 잘 설정됨.
-   `Strategy` <-> `ConflictLog`: 다중 관계(Conflicting vs Owning)가 명시적 `foreign_keys` 구분을 통해 잘 정의됨.

---

## 2. ⚡ N+1 쿼리 문제 예측 및 전략

### ⚠️ 위험 구간
1.  **전략별 포지션 조회**: `strategy.position_ownerships` 접근 시.
    -   대응: `StrategyRepository.get_with_positions()` 등의 메서드에서 `.options(joinedload(Strategy.position_ownerships))` 사용 필수.
2.  **소유권 리스트 조회**: 여러 `PositionOwnership`을 나열하고 각 `ownership.strategy.name`을 표시할 때.
    -   대응: `PositionOwnership` 쪽의 `strategy` 관계에 `lazy='joined'`를 설정하거나 쿼리 시 `joinedload` 사용.

### 💡 Loading 전략 제안
-   `PositionOwnership.strategy`: 항상 함께 쓰일 가능성이 높으므로 **Eager Loading (`lazy='joined'`)** 고려.
-   `Strategy.position_ownerships`: 데이터가 많을 수 있으므로 **Lazy Loading** 유지하되, 필요한 경우에만 명시적 로딩.

---

## 3. 🛡️ Cascade 규칙 및 정합성

### Cascade 설정
-   `Strategy` 삭제 시 `owned_positions` 처리가 `cascade="all, delete-orphan"`이 아닌 `RESTRICT`(DB 레벨)로 보호되고 있습니다. 이는 의도된 설계(안전장치)로 보입니다.
-   **권장**: 모델 레벨에서도 명시적으로 삭제를 막거나, `passive_deletes=True`를 설정하여 DB 제약조건에 위임함을 명시하는 것이 좋습니다.

---

## 📝 결론 및 액션 아이템

모델 정의는 전반적으로 견고하지만, 실행 시 오류를 방지하기 위해 **Relationship 문법 수정**이 필요합니다.

**승인 여부**: ⚠️ **조건부 승인 (Conditional Approval)**

**필수 수정 사항 (T0.2 내 반영 필요)**:
1.  `models.py` 내 모든 `relationship` 정의에서 `foreign_keys` 문자열의 불필요한 대괄호(`[]`) 제거.
    -   `foreign_keys="[Start...` -> `foreign_keys="Start...`

이 수정 후 T0.3 (Repository 구현)으로 진행하시기 바랍니다.
