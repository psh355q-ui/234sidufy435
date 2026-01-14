---
description: 개발 전 Structure Map 검토 및 업데이트 필수 규칙
---

# Structure First Development Rule

복잡한 시스템의 안정적인 개발을 위해, 모든 작업 전 **Structure Map**을 검토해야 합니다.

## 1. 개발 시작 전 (Before Development)

### Step 1: 업데이트
최신 코드 상태를 반영하기 위해 Structure Map을 업데이트합니다.

```powershell
python backend/utils/structure_mapper.py
```

### Step 2: 검토
생성된 `docs/architecture/structure-map.md`를 열어 다음을 확인합니다:
- 수정하려는 모듈이 어디서 사용되는지 (Who calls me?)
- 수정하려는 모듈이 무엇을 의존하는지 (Who do I call?)
- 함께 수정해야 할 연관 컴포넌트가 있는지

## 2. PR 제출 전 (Before Pull Request)

코드가 변경되었으므로 Structure Map도 변경되어야 합니다.

```powershell
# 1. 재생성
python backend/utils/structure_mapper.py

# 2. 변경사항 포함
git add docs/architecture/structure-map.md
git commit -m "docs: update structure map"
```

## 3. 왜 필요한가요?

- **의존성 파악**: 예상치 못한 사이드 이펙트 방지
- **설계 검증**: 순환 참조나 불필요한 결합 발견
- **문서 최신화**: 코드는 변하지만 문서는 낡는 문제 해결
