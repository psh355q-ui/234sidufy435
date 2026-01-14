---
description: 사용자의 숙련도(Level 1~3)에 맞춰 GitHub 커밋 및 PR 과정을 가이드합니다.
---

# GitHub Commit Guide

초보자부터 고급 사용자까지, 각자의 단계에 맞춰 올바른 방식으로 코드를 커밋하고 푸시하도록 돕습니다.

## 트리거 (Trigger)
- 명령어: `/github-commit`
- 키워드: "커밋해줘", "깃허브 푸시", "PR 보내기"

## Workflow Steps

### 1. 현재 상태 진단
`git status`와 브랜치 상태를 확인하여 현재 사용자의 레벨을 짐작합니다.

- Level 1: `main` 브랜치에 있고, 변경사항이 스테이징되지 않음.
- Level 2: `feature/` 브랜치에 있음.
- Level 3: `develop` 브랜치에 있거나 복잡한 머지 상태.

### 2. 가이드 제공

#### 사용자 상태: Level 1 (Beginner)
아직 브랜치를 사용하지 않는 사용자에게:
1. "현재 `main` 브랜치에 직접 커밋하려고 합니다."
2. **도전 과제 제안**: "이번에는 브랜치를 따로 만들어볼까요? (Level 2)"
   - [네, 알려주세요] -> Level 2 가이드로 이동
   - [아니요, 그냥 할래요] -> "알겠습니다. `git add .`, `git commit -m ...`, `git push`를 진행합니다."

#### 사용자 상태: Level 2 (Intermediate)
이미 브랜치를 사용 중인 경우:
1. 커밋 메시지 컨벤션(`feat: ...`)을 제안합니다.
2. Push 후 PR 링크 생성 방법을 안내합니다.

#### 사용자 상태: Level 3 (Advanced)
CI/CD 및 코드 리뷰 준비:
1. 테스트 실행 여부 확인 (`pytest`)
2. PR 본문 템플릿 작성 가이드

### 3. 명령어 실행 대행 (Turbo)
사용자가 동의하면 실제 git 명령어를 실행합니다.

```powershell
# 예시
git add .
git commit -m "feat: implement github guide workflow"
git push origin feature/github-guide
```

## 팁 (Tip)

이 워크플로우는 단순 명령어 실행보다 **"성장"**에 초점을 맞춥니다. 사용자가 점점 더 안전하고 체계적인 Git 사용법을 익히도록 유도하세요.
