---
description: AI 에이전트 팀 구조(.claude/agents/)와 프로젝트 환경을 자동 생성
---

# Project Bootstrap

프로젝트용 AI 에이전트 팀 구조를 자동 생성하고, 선택적으로 실제 프로젝트 환경까지 셋업합니다.

## 트리거 키워드

- 명령어: `/project-bootstrap`
- 키워드: "에이전트 팀 만들어줘", "에이전트 팀 구성", "에이전트 팀 생성"

> [!IMPORTANT]
> **"에이전트 팀"이라는 키워드가 반드시 포함되어야 합니다.**
> 단순 코딩 요청이나 프로젝트 생성 요청에는 반응하지 않습니다.

## 필수 실행 규칙

이 워크플로우는 반드시 아래 단계를 순서대로 실행해야 합니다. 단계를 건너뛰지 마세요.

---

## 1단계: 기술 스택 확인

### Case A: 기술 스택이 명시된 경우

예: "FastAPI + React로 에이전트 팀 만들어줘"

→ **2단계로 진행**

### Case B: 기술 스택이 명시되지 않은 경우

예: "에이전트 팀 만들어줘"

**⚠️ 중요: 기술 스택 없이 진행 불가. 반드시 `/socrates`를 먼저 실행합니다.**

사용자에게 안내:
```
기술 스택이 지정되지 않았습니다.
먼저 /socrates로 프로젝트 기획을 진행하겠습니다.
21개 질문을 통해 요구사항을 정리하고, 적합한 기술 스택을 추천해 드립니다.
```

→ `/socrates` 워크플로우 실행
→ socrates 완료 후 기술 스택이 결정되면 2단계로 진행

---

## 2단계: 하위 기술 스택 선택

사용자에게 다음 질문들을 합니다:

### 질문 2-1: 데이터베이스 선택

```
어떤 데이터베이스를 사용하시겠습니까?

1. PostgreSQL (권장) - 벡터 DB 지원, 확장성
2. MySQL - 범용 관계형 DB
3. SQLite - 로컬 개발
4. MongoDB - NoSQL 문서 DB
```

### 질문 2-2: 인증 포함 여부

```
인증 기능(로그인/회원가입/프로필)을 포함할까요?

1. 예 (권장) - JWT 인증 + 로그인/회원가입/프로필 페이지
2. 아니오 - 인증 없이 기본 구조만
```

### 질문 2-3: 추가 기능 선택

```
추가로 필요한 기능이 있나요? (복수 선택 가능)

1. 벡터 DB (PGVector) - AI/RAG 애플리케이션용
2. Redis 캐시 - 세션/캐시 저장소
3. 3D 엔진 (Three.js) - 3D 시각화
4. 없음
```

---

## 3단계: 프로젝트 셋업 확인

```
프로젝트 환경을 셋업할까요?

1. 예 (권장) - 에이전트 팀 + 백엔드 + 프론트엔드 + Docker
2. 에이전트 팀만 - .claude/agents/ 파일만 생성
```

---

## 4단계: 프로젝트 생성

### 4-1. 에이전트 팀 생성 (항상 실행)

`.agent/scripts/project-bootstrap/references/` 디렉토리의 템플릿을 기반으로 에이전트 및 커맨드 파일을 생성합니다.

**생성 구조:**
```
.claude/
  agents/
    backend-specialist.md
    frontend-specialist.md
    database-specialist.md
    test-specialist.md
    3d-engine-specialist.md (3D 선택 시)
  commands/
    orchestrate.md          ← 커맨드로 설치 (Task 도구 사용)
    integration-validator.md
    agent-lifecycle.md
```

**중요:** 오케스트레이터는 Task 도구를 사용해야 하므로 반드시 커맨드로 설치합니다!

### 4-2. MCP 서버 설정

```powershell
python .agent\scripts\project-bootstrap\setup_mcp.py -p .
```

### 4-3. Docker Compose 생성

```powershell
# 데이터베이스 선택에 따라
python .agent\scripts\project-bootstrap\setup_docker.py -t <template> -p .
```

| 선택 | Template |
|------|----------|
| PostgreSQL | `postgres` |
| PostgreSQL + 벡터 | `postgres-pgvector` |
| PostgreSQL + Redis | `postgres-redis` |
| MySQL | `mysql` |
| MongoDB | `mongodb` |

### 4-4. 백엔드 생성

```powershell
python .agent\scripts\project-bootstrap\setup_backend.py -f <framework> -p .\backend
# 인증 포함 시: --with-auth 추가
```

| 프레임워크 | 명령어 |
|-----------|--------|
| FastAPI | `-f fastapi` |
| Express | `-f express` |
| Rails | `-f rails` |
| Django | `-f django` |

### 4-5. 프론트엔드 생성

```powershell
python .agent\scripts\project-bootstrap\setup_frontend.py -f <framework> -p .\frontend
# 인증 포함 시: --with-auth 추가
```

| 프레임워크 | 명령어 |
|-----------|--------|
| React + Vite | `-f react-vite` |
| Next.js | `-f nextjs` |
| SvelteKit | `-f sveltekit` |
| Remix | `-f remix` |

### 4-6. Git 초기화

```powershell
python .agent\scripts\project-bootstrap\git_init.py -g fullstack -m "Initial commit"
```

---

## 5단계: 의존성 설치 확인

프로젝트 생성 완료 후 사용자에게 질문:

```
✅ 프로젝트 셋업이 완료되었습니다!

의존성 설치와 DB 마이그레이션을 진행할까요?

1. 예 - Docker 시작 + 의존성 설치 + DB 마이그레이션
2. 아니오 - 나중에 수동으로 진행
```

### "예" 선택 시 실행:

```powershell
# Docker 시작
docker compose up -d

# 백엔드 의존성 설치
cd backend

# FastAPI/Django
pip install -r requirements.txt

# Express
npm install

# Rails
bundle install
rails db:migrate

cd ..

# 프론트엔드 의존성 설치
cd frontend
npm install
cd ..
```

---

## 6단계: 기획 문서 확인

의존성 설치 완료 후 사용자에게 질문:

```
✅ 프로젝트 셋업이 완료되었습니다!

다음 단계를 선택해주세요:

1. 기획부터 시작 (권장) - /socrates로 PRD, TASKS 등 기획 문서 생성
2. 기존 기획 문서 사용 - 이미 docs/planning/에 기획 문서가 있는 경우
3. 바로 개발 시작 - 기획 문서 없이 자유롭게 개발
```

### "기획부터 시작" 선택 시
- `/socrates` 워크플로우 실행
- 21개 질문을 통해 요구사항 수집
- 기획 문서 생성 (docs/planning/)

### "기존 기획 문서 사용" 선택 시
- docs/planning/ 디렉토리 확인
- 문서가 없으면 다시 선택 요청

### "바로 개발 시작" 선택 시
- 안내 메시지 출력 후 종료

---

## 지원 기술 스택

### 백엔드

| Framework | Auth | 설명 |
|-----------|------|------|
| FastAPI | ✅ | Python + SQLAlchemy + JWT + Alembic |
| Express | ✅ | Node.js + TypeScript + JWT |
| Rails | ✅ | Ruby on Rails 8 + JWT/Session + SQLite WAL |
| Django | ❌ | Python + DRF |

### 프론트엔드

| Framework | Auth | 설명 |
|-----------|------|------|
| React+Vite | ✅ | React 19 + Zustand + TailwindCSS |
| Next.js | ✅ | App Router + Zustand + TailwindCSS |
| SvelteKit | ✅ | Svelte 5 runes + TailwindCSS |
| Remix | ✅ | Loader/Action 패턴 + TailwindCSS |

### 데이터베이스

| DB | Docker Template |
|----|-----------------|
| PostgreSQL | `postgres` |
| PostgreSQL + PGVector | `postgres-pgvector` |
| PostgreSQL + Redis | `postgres-redis` |
| MySQL | `mysql` |
| MongoDB | `mongodb` |

---

## 인증 UI 페이지 (--with-auth 시 생성)

| 경로 | 기능 |
|------|------|
| `/login` | 로그인 |
| `/register` | 회원가입 |
| `/profile` | 프로필 (비밀번호 변경, 로그아웃, 계정 삭제) |

---

## 관련 워크플로우

- `.agent/workflows/socrates.md`: 프로젝트 기획 문서 생성
- `.agent/workflows/tasks-generator.md`: TASKS.md 생성

## 관련 규칙

- `.agent/rules/planning-standards.md`: 기획 문서 작성 표준
- `.agent/rules/git-conventions.md`: Git 사용 규칙
