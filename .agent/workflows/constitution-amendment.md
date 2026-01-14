---
description: 헌법(Constitution) 수정 프로세스를 안내하는 워크플로우.
---

# Constitution Amendment Workflow

시스템의 핵심 규칙인 헌법을 수정하기 위한 워크플로우입니다.

## 트리거 (Trigger)
- 명령어: `/constitution-amendment`
- 키워드: "헌법 수정", "규칙 변경", "hard rule 수정"

## Workflow Steps

### 1. 현재 헌법 확인
수정하려는 규칙이 정의된 파일을 찾습니다.
- 관련 파일: `backend/constitution/*.py`, `backend/execution/order_validator.py` 등

### 2. 수정 제안 요청
사용자로부터 수정 내용과 이유를 입력받습니다.

> "현재 포지션 제한 10%를 15%로 늘리고 싶습니다. 이유는..."

### 3. 위험성 경고 (Risk Warning)
헌법 수정이 시스템에 미칠 수 있는 위험을 경고합니다.

> ⚠️ **경고**: 포지션 제한을 완화하면 최대 낙폭(MDD)이 증가할 수 있습니다.

### 4. 코드 수정 및 검증
사용자가 확정하면 코드를 수정하고, 기존 테스트를 실행하여 깨지는 부분이 없는지 확인합니다.

```powershell
pytest backend/tests/test_order_validator.py
python backend/constitution/check_integrity.py
```

### 5. 문서화
수정 이력을 기록합니다.

---

## 사용 예시

**User**: "/constitution-amendment 손절 규칙 완화해줘"

**Antigravity**:
1. `order_validator.py`의 `NO_STOP_LOSS` 규칙 확인
2. 위험성 경고 및 확인 요청
3. 코드 수정
4. 테스트 실행
5. 완료
