---
description: Git 사용 규칙 및 Worktree 전략
---

# Git Conventions

프로젝트의 Git 사용 규칙 및 브랜치 전략을 정의합니다.

## Worktree 전략

### Phase 0: Main 브랜치
- **용도**: 프로젝트 초기 셋업
- **작업 위치**: main 브랜치 직접
- **예시**:
  - 프로젝트 구조 생성
  - 의존성 설치
  - 환경 설정 파일 (.env, docker-compose.yml)

### Phase 1+: Worktree 브랜치
- **용도**: 기능 개발 (TDD 적용)
- **작업 위치**: 별도 worktree
- **명명 규칙**: `phase/{phase번호}-{기능명}`

## Worktree 명명 규칙

```bash
# 패턴
git worktree add ../{프로젝트명}-phase{번호}-{기능명} -b phase/{번호}-{기능명}

# 예시
git worktree add ../ai-trading-phase1-auth -b phase/1-auth
git worktree add ../ai-trading-phase2-portfolio -b phase/2-portfolio
git worktree add ../ai-trading-phase3-backtest -b phase/3-backtest
```

## 브랜치 전략

### Main 브랜치
- **보호**: Phase 0 완료 후 보호 활성화
- **병합**: Pull Request를 통한 병합만 허용
- **테스트**: CI/CD 파이프라인 통과 필수

### Phase 브랜치
- **명명**: `phase/{번호}-{기능명}`
- **수명**: 기능 완료 및 병합 후 삭제
- **규칙**: 하나의 Phase는 하나의 주요 기능에 집중

### Feature 브랜치 (선택적)
- **명명**: `feature/{기능명}`
- **용도**: Phase 내 세부 기능 분리
- **병합**: Phase 브랜치로 병합

## 커밋 메시지 규칙

### 형식

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- **feat**: 새로운 기능
- **fix**: 버그 수정
- **docs**: 문서 변경
- **style**: 코드 포맷팅 (로직 변경 없음)
- **refactor**: 리팩토링
- **test**: 테스트 추가/수정
- **chore**: 빌드, 설정 파일 변경

### 예시

```
feat(auth): JWT 인증 API 구현

- POST /api/login 엔드포인트 추가
- JWT 토큰 생성 및 검증 로직
- 테스트 커버리지 85%

Closes #123
```

```
test(portfolio): 포트폴리오 조회 테스트 추가

- test_get_portfolio_success()
- test_get_portfolio_unauthorized()
- Mock KIS API 응답 설정
```

## Worktree 관리

### Worktree 목록 확인

```bash
git worktree list
```

### Worktree 제거

```bash
# 1. Worktree 디렉토리로 이동하여 작업 완료 확인
# 2. 원본 디렉토리로 복귀
cd /path/to/main/project

# 3. Worktree 제거
git worktree remove ../ai-trading-phase1-auth

# 4. 브랜치 삭제 (병합 완료 후)
git branch -d phase/1-auth
```

### Worktree 정리 (비활성 Worktree 제거)

```bash
git worktree prune
```

## Pull Request 규칙

### PR 제목

```
[Phase {번호}] {기능명}
```

예시:
- `[Phase 1] User 인증 API`
- `[Phase 2] 포트폴리오 조회 기능`

### PR 설명 템플릿

```markdown
## 변경 사항
- 주요 변경 내용 요약

## TDD 사이클
- [ ] RED: 테스트 작성 완료
- [ ] GREEN: 구현 완료
- [ ] REFACTOR: 리팩토링 완료

## 테스트
- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] 코드 커버리지 80% 이상

## 체크리스트
- [ ] 코드 리뷰 요청
- [ ] CI/CD 파이프라인 통과
- [ ] 문서 업데이트
```

## Git 작업 흐름

### Phase 1 작업 예시

```bash
# 1. Worktree 생성
git worktree add ../ai-trading-phase1-auth -b phase/1-auth

# 2. Worktree로 이동
cd ../ai-trading-phase1-auth

# 3. TDD 사이클
# RED: 테스트 작성
git add tests/test_auth.py
git commit -m "test(auth): 로그인 테스트 작성"

# GREEN: 구현
git add api/auth_router.py
git commit -m "feat(auth): 로그인 API 구현"

# REFACTOR: 정리
git add api/auth_router.py
git commit -m "refactor(auth): 인증 로직 정리"

# 4. 원격 저장소에 푸시
git push origin phase/1-auth

# 5. Pull Request 생성
# GitHub/GitLab에서 PR 생성

# 6. 병합 후 Worktree 제거
cd /path/to/ai-trading-system
git worktree remove ../ai-trading-phase1-auth
git branch -d phase/1-auth
```

## 규칙 위반 예시

### ❌ 잘못된 예

```bash
# Phase 1 작업을 main 브랜치에서 직접 수행
git checkout main
git add api/auth_router.py
git commit -m "add auth"  # 너무 간략한 커밋 메시지
```

### ✅ 올바른 예

```bash
# Worktree 생성 후 작업
git worktree add ../ai-trading-phase1-auth -b phase/1-auth
cd ../ai-trading-phase1-auth
git add api/auth_router.py
git commit -m "feat(auth): JWT 인증 API 구현

- POST /api/login 엔드포인트 추가
- 테스트 커버리지 85%"
```

## 관련 문서

- `.agent/rules/tdd-workflow.md`: TDD 워크플로우 규칙
- `.agent/rules/planning-standards.md`: 기획 문서 작성 표준
