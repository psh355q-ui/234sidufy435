---
description: 헌법(Constitution) 및 핵심 시스템 규칙 수정 시 준수해야 할 엄격한 절차.
---

# Constitution Management Rules

이 프로젝트에는 **헌법(Constitution)**이라 불리는 변경 불가에 가까운 핵심 규칙들이 존재합니다. 이를 수정할 때는 시스템의 안전성을 위해 엄격한 절차를 따라야 합니다.

## 1. 헌법의 범위 (Scope)

헌법으로 취급되는 항목은 다음과 같습니다:

1. **Hard Rules (8개)**: `backend/execution/order_validator.py`
2. **Risk Limits**: `backend/constitution/risk_limits.py`
3. **Agent Weights Rules**: `agent_weights_history` 조정 로직
4. **Position Sizing Formula**: `backend/ai/mvp/risk_agent_mvp.py`
5. **Constitution Files**: `backend/constitution/*.py`

## 2. 수정 원칙 (Amendment Principles)

1. **불변성 존중**: 헌법은 기본적으로 변경하지 않는 것이 원칙입니다.
2. **명시적 승인**: 모든 수정은 사용자의 명시적인 승인(Explicit Approval)이 필요합니다. AI가 자의적으로 판단하여 수정할 수 없습니다.
3. **무결성 검증**: 수정 후에는 반드시 전체 시스템 무결성 테스트(Integrity Check)를 통과해야 합니다.

## 3. 수정 절차 (Amendment Procedure)

### Step 1: 수정 제안서 (Proposal)
수정하려는 이유와 예상되는 영향(Side Effect)을 문서로 작성합니다.

### Step 2: 백테스트 (Backtest)
가능한 경우, 변경된 규칙을 과거 데이터에 적용하여 시뮬레이션합니다. 예: "손절 범위를 5% → 10%로 늘리면 수익률 변화는?"

### Step 3: 사용자 승인 (Approval)
사용자에게 제안서와 데이터 기반 근거를 제시하고 승인을 받습니다.

### Step 4: 적용 및 버전 업 (Implementation)
- 코드를 수정합니다.
- `docs/CONSTITUTION_AMENDMENT.md` (혹은 관련 문서)에 수정 이력을 남깁니다.
- 헌법 버전(v2.0.0 → v2.0.1)을 올립니다.

## 4. Workflow

Antigravity는 헌법 수정을 돕기 위해 `/constitution-amendment` 워크플로우를 제공합니다.

```
/constitution-amendment
```
