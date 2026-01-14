---
description: TDD 워크플로우 규칙 - Phase 1+ 작업 시 필수 적용
---

# TDD Workflow Rules

Phase 1 이상의 모든 개발 작업은 반드시 TDD 사이클을 따릅니다.

## 필수 사이클

모든 Phase 1+ 태스크는 다음 순서를 따라야 합니다:

1. **RED**: 테스트 먼저 작성 (실패 확인)
2. **GREEN**: 최소 구현 (테스트 통과)
3. **REFACTOR**: 리팩토링 (테스트 유지)

## Phase별 작업 방식

### Phase 0: 프로젝트 셋업
- **Git Worktree**: 불필요
- **작업 위치**: main 브랜치에서 직접 작업
- **목적**: 프로젝트 기본 구조, 의존성 설치, 환경 설정

### Phase 1+: 기능 개발
- **Git Worktree**: 필수
- **작업 위치**: 별도 worktree에서 작업
- **TDD**: 필수

## Git Worktree 설정

Phase 1 이상의 작업을 시작할 때:

```bash
# Worktree 생성
git worktree add ../project-phase1-{feature} -b phase/1-{feature}

# Worktree로 이동
cd ../project-phase1-{feature}

# TDD 사이클 시작
# 1. RED: 테스트 작성
# 2. GREEN: 구현
# 3. REFACTOR: 정리
```

## 태스크 독립성 원칙

각 태스크는 독립적으로 실행 가능해야 합니다:

- **의존성이 있는 경우**: Mock 설정 포함
- **병렬 실행**: 가능한 경우 명시
- **인수 조건**: 명확하게 정의

## 예시: Phase 1 태스크

```markdown
### [] Phase 1, T1.1: User 인증 API RED→GREEN

**담당**: backend-specialist

**Git Worktree 설정**:
```bash
git worktree add ../ai-trading-phase1-auth -b phase/1-auth
```

**TDD 사이클**:
1. **RED**: `tests/test_auth.py` 작성 (실패 확인)
   - test_login_success()
   - test_login_invalid_credentials()
   - test_token_validation()

2. **GREEN**: `api/auth_router.py` 최소 구현
   - POST /api/login 엔드포인트
   - JWT 토큰 생성
   - 테스트 통과 확인

3. **REFACTOR**: 코드 정리
   - 중복 제거
   - 가독성 개선
   - 테스트 유지

**산출물**:
- backend/api/auth_router.py
- backend/tests/test_auth.py
- JWT 토큰 발급 로직

**인수 조건**:
- [ ] 모든 테스트 통과 (pytest)
- [ ] 코드 커버리지 80% 이상
- [ ] Worktree에서 독립적으로 실행 가능
```

## 규칙 위반 시

다음과 같은 경우 개발을 중단하고 수정이 필요합니다:

- ❌ Phase 1+ 작업을 main 브랜치에서 직접 수행
- ❌ 테스트 없이 구현 먼저 작성
- ❌ 테스트가 실패하는 상태로 커밋
- ❌ Worktree 설정 없이 Phase 1+ 작업 진행

## 관련 문서

- `.agent/rules/git-conventions.md`: Git 브랜치 전략 및 커밋 규칙
- `.agent/rules/planning-standards.md`: 태스크 문서 작성 표준
- `.agent/workflows/tasks-generator.md`: TASKS.md 생성 워크플로우
