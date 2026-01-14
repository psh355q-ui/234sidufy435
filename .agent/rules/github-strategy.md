---
description: GitHub branch strategy and commit guidelines for different levels of expertise.
---

# GitHub Strategy & Guidelines

프로젝트의 안정적인 버전 관리와 협업을 위한 GitHub 활용 전략입니다. 사용자 숙련도에 따라 단계를 나누어 적용합니다.

## 1. 브랜치 전략 (Branch Strategy)

간소화된 GitFlow 전략을 사용합니다.

```
main (Production)
  ↑
develop (Integration)
  ↑
feature/YYMMDD-description (New Features)
fix/YYMMDD-description (Bug Fixes)
docs/YYMMDD-description (Documentation)
```

- **main**: 항상 배포 가능한 안정 상태 유지. 직접 커밋 금지 (가능한 경우).
- **develop**: 개발 중인 코드가 통합되는 곳. 다음 배포를 위한 준비 단계.
- **feature/*** : 새로운 기능 개발. `develop`에서 분기하여 `develop`으로 병합.
- **fix/*** : 버그 수정. `develop`에서 분기하여 `develop`으로 병합. 긴급한 경우 `main`에서 분기(hotfix).

### 브랜치 명명 규칙

`type/YYMMDD-description`

- `feature/260114-structure-map-auto`
- `fix/260114-db-connection-error`
- `docs/260114-update-readme`

## 2. 커밋 가이드 (Commit Guidelines)

**Conventional Commits** 형식을 권장합니다.

`type(scope): subject`

- `feat(auth): add google login`
- `fix(api): handle timeout error`
- `docs(readme): update installation guide`
- `refactor(db): optimize query performance`

**Types**:
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅 (로직 변경 없음)
- `refactor`: 리팩토링 (기능 변경 없음)
- `test`: 테스트 코드
- `chore`: 빌드, 패키지 매니저 설정 등

## 3. GitHub 활용 레벨 (User Levels)

사용자의 GitHub 숙련도에 따른 가이드입니다.

### Level 1: Beginner (현재 상태)
- **Main Only**: 모든 작업을 `main` 브랜치에서 진행.
- **Direct Commit**: PR 없이 직접 커밋 및 푸시.
- **목표**: Git 기본 명령어(`add`, `commit`, `push`, `pull`) 익숙해지기.

```bash
git checkout main
git pull origin main
# 작업 후
git add .
git commit -m "작업 내용"
git push origin main
```

### Level 2: Intermediate (권장)
- **Feature Branches**: 기능별로 브랜치 생성.
- **Pull Requests**: GitHub에서 PR 생성 후 Merge.
- **목표**: 작업 격리 및 코드 리뷰 프로세스 경험.

```bash
# 새 작업 시작
git checkout main
git pull origin main
git checkout -b feature/260114-my-feature

# 작업 및 커밋
git add .
git commit -m "feat: my new feature"
git push origin feature/260114-my-feature

# GitHub에서 PR 생성 및 Merge
# 완료 후 로컬 정리
git checkout main
git pull origin main
git branch -d feature/260114-my-feature
```

### Level 3: Advanced
- **GitFlow**: `develop`, `release` 브랜치 활용.
- **CI/CD**: 커밋 시 자동 테스트 및 배포.
- **Code Review**: 엄격한 코드 리뷰 및 승인 절차.

## 4. Workflows

Antigravity는 커밋을 돕기 위해 `/github-commit` 워크플로우를 제공합니다. 사용자의 Level에 맞춰 명령어를 제안합니다.

```
/github-commit
```
