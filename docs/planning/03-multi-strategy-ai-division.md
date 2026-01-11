# AI 분업 전략: Claude Code + Gemini 2.0 Flash Thinking

**Version**: 1.0
**Date**: 2026-01-11
**Based On**: [02-multi-strategy-orchestration-tasks.md](./02-multi-strategy-orchestration-tasks.md)

---

## 🎯 분업 원칙

| AI | 역할 | 강점 | 담당 작업 |
|----|------|------|----------|
| **Claude Code** | 코드 구현 전문 | TDD, Git Worktree, 에이전트 오케스트레이션 | 백엔드/프론트엔드 코드 작성, 테스트 |
| **Gemini 2.0 Flash Thinking** | 설계 & 검증 전문 | 빠른 추론, 비용 효율, 문서 분석 | 설계 검토, 테스트 시나리오, 문서화 |

---

## 📋 Phase별 분업 계획

### Phase 0: DB 스키마 & 테스트 설계

#### T0.1: DB 스키마 정의 및 마이그레이션 스크립트 작성

**🤖 Claude Code 담당**
```
database-orchestrator 에이전트를 사용해서:
1. db-schema-manager로 3개 테이블 스키마 JSON 생성
2. 스키마 검증 스크립트 실행
3. 마이그레이션 SQL 생성
```

**산출물**:
- `backend/ai/skills/system/db-schema-manager/schemas/strategies.json`
- `backend/ai/skills/system/db-schema-manager/schemas/position_ownership.json`
- `backend/ai/skills/system/db-schema-manager/schemas/conflict_logs.json`
- `backend/database/migrations/create_multi_strategy_tables.sql`

**🧠 Gemini 담당**
```
생성된 스키마를 검토하고:
1. 인덱스 전략 최적화 제안
2. FK 관계 검증 (CASCADE, RESTRICT 규칙)
3. JSONB 사용 타당성 분석
4. 성능 병목 예측 및 완화 방안
```

**산출물**:
- `docs/planning/schema-review-report.md` (검토 보고서)

---

#### T0.2: SQLAlchemy 모델 정의

**🤖 Claude Code 담당**
```
backend-architect 에이전트가:
1. backend/database/models.py에 3개 모델 추가
2. 관계 설정 (relationship, back_populates)
3. 타입 힌트 적용
```

**산출물**:
- `backend/database/models.py` (수정)

**🧠 Gemini 담당**
```
생성된 모델을 검토하고:
1. ORM 관계 매핑 정확성 검증
2. N+1 쿼리 문제 예측
3. Lazy Loading vs Eager Loading 전략 제안
```

**산출물**:
- `docs/planning/orm-review.md` (ORM 검토)

---

#### T0.3: Repository 클래스 생성

**🤖 Claude Code 담당**
```
backend-architect 에이전트가:
1. 3개 Repository 클래스 생성 (StrategyRepository, PositionOwnershipRepository, ConflictLogRepository)
2. CRUD 메서드 구현
3. 특화 메서드 구현 (get_active_strategies, get_by_ticker 등)
```

**산출물**:
- `backend/database/repository.py` (수정)

**🧠 Gemini 담당**
```
Repository 패턴 검증:
1. 추상화 레벨 적절성
2. 메서드 시그니처 일관성
3. 트랜잭션 처리 전략
4. 에러 핸들링 패턴
```

**산출물**:
- `docs/planning/repository-pattern-review.md`

---

#### T0.4: Pydantic 스키마 정의

**🤖 Claude Code 담당**
```
backend-architect 에이전트가:
1. backend/api/schemas/strategy_schemas.py 생성
2. 9개 Pydantic 스키마 정의
3. Enum 타입 정의 (ConflictResolution, OwnershipType, TimeHorizon)
```

**산출물**:
- `backend/api/schemas/strategy_schemas.py`

**🧠 Gemini 담당**
```
API 스키마 검증:
1. 필드 검증 규칙 충분성
2. OpenAPI 문서 자동 생성 품질
3. Request/Response 타입 일관성
```

**산출물**:
- `docs/planning/api-schema-review.md`

---

#### T0.5: API 계약 정의

**🧠 Gemini 담당** (Gemini가 먼저 설계)
```
API 계약 초안 작성:
1. 엔드포인트 경로 설계 (RESTful 규칙)
2. Request/Response 스키마 정의
3. 에러 응답 시나리오 (409, 422, 500 등)
4. 인증/인가 요구사항
```

**산출물**:
- `backend/contracts/strategy_contracts.py` (초안)

**🤖 Claude Code 담당** (계약 기반 구현)
```
Gemini가 작성한 계약을 backend/contracts/에 추가하고:
1. FastAPI router 스텁 생성
2. 계약 위반 시 자동 검증 로직
```

---

#### T0.6: 단위 테스트 템플릿 작성 (TDD RED)

**🧠 Gemini 담당** (테스트 시나리오 설계)
```
테스트 시나리오 작성:
1. 충돌 감지 시나리오 10개 정의
2. Edge case 식별 (동일 우선순위, NULL 처리 등)
3. Mock 데이터 설계
4. Given-When-Then 형식으로 시나리오 작성
```

**산출물**:
- `docs/planning/test-scenarios.md`

**🤖 Claude Code 담당** (테스트 코드 작성)
```
test-engineer 에이전트가 Gemini 시나리오를 pytest로 변환:
1. backend/tests/test_conflict_detector.py 생성
2. backend/tests/test_strategy_repository.py 생성
3. Mock 설정 (backend/tests/mocks/strategy_mocks.py)
4. 모든 테스트 RED 상태 확인
```

**산출물**:
- `backend/tests/test_*.py` (10개 이상 테스트 함수)

---

### Phase 1: 전략 레지스트리

#### T1.1: Strategy 모델 CRUD 구현 RED→GREEN

**🤖 Claude Code 담당** (TDD 사이클 전체)
```
Git Worktree 생성 후:
1. RED: 테스트 실행 (Phase 0에서 작성됨)
2. GREEN: StrategyRepository 구현
3. REFACTOR: 중복 제거, 타입 힌트 보완
```

**🧠 Gemini 담당** (코드 리뷰)
```
Claude가 구현한 코드 리뷰:
1. 테스트 커버리지 확인 (>= 80%)
2. 리팩토링 제안 (SOLID 원칙)
3. 성능 최적화 기회 식별
```

**산출물** (Gemini):
- `docs/planning/phase1-code-review.md`

---

#### T1.2: 기본 전략 시드 데이터 생성

**🧠 Gemini 담당** (시드 데이터 설계)
```
전략 메타데이터 설계:
1. 4개 기본 전략 (long_term, dividend, trading, aggressive)
2. 우선순위 값 정의 (100, 90, 50, 30)
3. time_horizon 매핑
4. config_metadata JSON 구조 설계
```

**산출물**:
- `docs/planning/seed-strategies.json` (설계)

**🤖 Claude Code 담당** (시드 스크립트 구현)
```
backend-architect 에이전트가:
1. backend/scripts/seed_strategies.py 생성
2. Gemini가 설계한 데이터를 코드로 변환
3. Idempotent 로직 구현 (중복 방지)
```

---

#### T1.3: 전략 관리 API 엔드포인트

**🤖 Claude Code 담당** (API 구현)
```
backend-architect 에이전트가:
1. backend/api/strategy_router.py 생성
2. GET /api/v1/strategies
3. POST /api/v1/strategies/{id}/activate
4. POST /api/v1/strategies/{id}/deactivate
```

**🧠 Gemini 담당** (API 테스트 시나리오)
```
Postman/HTTPie 시나리오 작성:
1. 정상 케이스 (200 OK)
2. 에러 케이스 (404 Not Found, 409 Conflict)
3. 인증 실패 케이스
```

**산출물**:
- `docs/planning/api-test-scenarios.md`

---

### Phase 2: 포지션 소유권 추적

#### T2.1: PositionOwnership 모델 CRUD 구현

**🤖 Claude Code 담당** (TDD 구현)
```
Git Worktree phase/2-ownership 에서:
1. RED → GREEN → REFACTOR
2. PositionOwnershipRepository 구현
```

**🧠 Gemini 담당** (동시성 문제 분석)
```
동시성 시나리오 검토:
1. 두 전략이 동시에 같은 종목 매수 시도
2. Race condition 발생 가능성
3. PostgreSQL 트랜잭션 격리 수준 제안
4. Optimistic Locking vs Pessimistic Locking
```

**산출물**:
- `docs/planning/concurrency-analysis.md`

---

#### T2.2: 포지션 생성 시 자동 소유권 할당

**🤖 Claude Code 담당** (Order Manager 수정)
```
backend/execution/order_manager.py 수정:
1. _create_position_from_order() 메서드 확장
2. PositionOwnership 자동 생성
3. Event Bus 이벤트 발행 (OWNERSHIP_ACQUIRED)
```

**🧠 Gemini 담당** (트랜잭션 검증)
```
트랜잭션 시나리오 검증:
1. Position 생성 성공 + Ownership 생성 실패 → 롤백?
2. 원자성 보장 방법
3. 이벤트 발행 실패 시 복구 전략
```

**산출물**:
- `docs/planning/transaction-scenarios.md`

---

#### T2.3: 소유권 이전 로직

**🧠 Gemini 담당** (이전 규칙 설계)
```
소유권 이전 시나리오 설계:
1. 우선순위 비교 규칙
2. 부분 이전 vs 전체 이전
3. 이전 불가 조건 (잠금 상태 등)
4. 이전 이력 추적 방법
```

**산출물**:
- `docs/planning/ownership-transfer-rules.md`

**🤖 Claude Code 담당** (구현)
```
backend/services/ownership_service.py 생성:
1. transfer_ownership() 메서드 구현
2. Gemini가 설계한 규칙 적용
```

---

### Phase 3: 충돌 감지 엔진

#### T3.1: ConflictDetector 클래스 구현

**🧠 Gemini 담당** (충돌 감지 알고리즘 설계)
```
충돌 감지 의사결정 트리 작성:
1. 입력: TradingSignal (strategy_id, ticker, action)
2. 단계별 검사 로직
   - Step 1: 해당 종목 포지션 존재 여부
   - Step 2: 소유 전략 확인
   - Step 3: 우선순위 비교
   - Step 4: 잠금 상태 확인
   - Step 5: Resolution 결정 (allowed/blocked/override)
3. 각 단계별 reasoning 생성 규칙
```

**산출물**:
- `docs/planning/conflict-detection-algorithm.md` (의사결정 트리 다이어그램 포함)

**🤖 Claude Code 담당** (구현)
```
backend/services/conflict_detector.py 생성:
1. ConflictDetector 클래스
2. check_conflict(signal: TradingSignal) 메서드
3. Gemini가 설계한 알고리즘 구현
```

---

#### T3.2: 우선순위 규칙 엔진

**🧠 Gemini 담당** (규칙 테이블 설계)
```
우선순위 규칙 매트릭스 작성:

| 소유 전략 | 새 전략 | 액션 | 결과 | Reasoning |
|----------|---------|------|------|-----------|
| long_term (100) | trading (50) | sell | BLOCKED | "장기 투자 우선순위로 차단" |
| trading (50) | long_term (100) | buy | ALLOWED + TRANSFER | "높은 우선순위로 소유권 이전" |
| long_term (100) | long_term (100) | sell | ALLOWED | "동일 전략 내 조정" |

전체 16개 시나리오 작성
```

**산출물**:
- `docs/planning/priority-rules-matrix.md`

**🤖 Claude Code 담당** (규칙 엔진 구현)
```
backend/services/priority_rules.py 생성:
1. PriorityRulesEngine 클래스
2. resolve_conflict() 메서드
3. Gemini가 작성한 매트릭스를 코드로 변환
4. 규칙 설정 JSON 파일로 외부화 가능하게
```

---

#### T3.3: ConflictLog 저장 및 조회

**🤖 Claude Code 담당** (로깅 구현)
```
ConflictLogRepository 구현:
1. create() - 충돌 로그 저장
2. get_recent_conflicts(days=7) - 최근 충돌 조회
3. ConflictDetector에 로깅 통합
```

**🧠 Gemini 담당** (로그 분석 전략)
```
로그 분석 시나리오 설계:
1. 충돌 빈도 분석 (어떤 전략 조합이 자주 충돌?)
2. 차단된 주문의 잠재 수익 손실 계산
3. 우선순위 규칙 조정 필요성 판단 기준
```

**산출물**:
- `docs/planning/conflict-log-analysis.md`

---

### Phase 4: Order Manager 통합

#### T4.1: Order Manager에 충돌 검사 추가

**🤖 Claude Code 담당** (Order Manager 수정)
```
backend/execution/order_manager.py 수정:
1. _validate_order() 메서드에 충돌 검사 추가
2. ConflictDetector.check_conflict() 호출
3. 충돌 시 REJECTED 상태로 전환
```

**🧠 Gemini 담당** (통합 시나리오 검증)
```
Order Manager 통합 시나리오:
1. 주문 생성 → 충돌 검사 → 차단 → REJECTED
2. 주문 생성 → 충돌 없음 → PENDING → SUBMITTED
3. State Machine 상태 전이 다이어그램 업데이트
```

**산출물**:
- `docs/planning/order-manager-integration.md`

---

#### T4.2: Event Bus 이벤트 추가

**🤖 Claude Code 담당** (이벤트 추가)
```
backend/events/event_types.py 수정:
1. 5개 이벤트 타입 추가 (CONFLICT_DETECTED, ORDER_BLOCKED_BY_CONFLICT 등)
2. ConflictDetector에 이벤트 발행 로직 추가
```

**🧠 Gemini 담당** (이벤트 구독자 설계)
```
이벤트 구독자 전략 설계:
1. CONFLICT_DETECTED → 알림 발송, 로그 저장
2. OWNERSHIP_TRANSFERRED → 포트폴리오 재계산
3. ORDER_BLOCKED_BY_CONFLICT → 사용자 대시보드 알림
4. 이벤트 재처리 전략 (실패 시 재시도)
```

**산출물**:
- `docs/planning/event-subscriber-strategy.md`

---

### Phase 5: API & 프론트엔드

#### T5.1: 충돌 검사 API 엔드포인트

**🤖 Claude Code 담당** (API 구현)
```
backend/api/strategy_router.py 수정:
1. POST /api/v1/orders/check-conflict 엔드포인트
2. ConflictDetector 서비스 호출
3. ConflictCheckResponse 반환
```

**🧠 Gemini 담당** (API 문서 작성)
```
OpenAPI 문서 보완:
1. 예시 Request/Response
2. 에러 코드 설명 (409 Conflict)
3. Rate limiting 전략
```

**산출물**:
- `docs/planning/api-documentation.md`

---

#### T5.2: 포지션 소유권 조회 API

**🤖 Claude Code 담당** (API 구현)
```
GET /api/v1/positions/ownership 엔드포인트:
1. PositionOwnershipRepository 호출
2. 페이지네이션 구현
```

**🧠 Gemini 담당** (응답 최적화)
```
API 응답 최적화 전략:
1. N+1 쿼리 방지 (JOIN 사용)
2. 캐싱 전략 (Redis)
3. 페이로드 크기 최소화
```

**산출물**:
- `docs/planning/api-optimization.md`

---

#### T5.3: 멀티 전략 대시보드 UI

**🧠 Gemini 담당** (UI 설계 먼저)
```
대시보드 와이어프레임 작성:
1. 레이아웃 구조 (3단 구성: 전략 카드, 포지션 테이블, 충돌 알림)
2. 컴포넌트 계층 구조
3. 상태 관리 전략 (Zustand vs React Query)
4. 실시간 업데이트 방법 (WebSocket vs Polling)
```

**산출물**:
- `docs/planning/dashboard-wireframe.md` (ASCII 다이어그램)

**🤖 Claude Code 담당** (React 구현)
```
frontend-developer 에이전트가:
1. frontend/src/pages/StrategyDashboard.tsx 생성
2. frontend/src/components/StrategyCard.tsx 생성
3. Gemini가 설계한 와이어프레임 기반 구현
```

---

#### T5.4: 포지션 소유권 테이블 컴포넌트

**🤖 Claude Code 담당** (React 구현)
```
frontend/src/components/PositionOwnershipTable.tsx 생성:
1. API 호출 (/api/v1/positions/ownership)
2. 테이블 UI (ticker, strategy, locked_until 표시)
```

**🧠 Gemini 담당** (UX 개선 제안)
```
테이블 UX 개선 아이디어:
1. 정렬 기능 (ticker, strategy, locked_until)
2. 필터 기능 (전략별, 잠금 상태별)
3. 색상 코딩 (잠금 = 빨강, 해제 = 초록)
```

**산출물**:
- `docs/planning/table-ux-improvements.md`

---

#### T5.5: 충돌 경고 컴포넌트

**🤖 Claude Code 담당** (React 구현)
```
frontend/src/components/ConflictAlert.tsx 생성:
1. WebSocket 구독 (CONFLICT_DETECTED 이벤트)
2. 경고 배너 UI (상단 고정)
```

**🧠 Gemini 담당** (알림 전략)
```
알림 우선순위 전략:
1. Critical: 충돌로 인한 주문 차단
2. Warning: 소유권 이전 발생
3. Info: 전략 활성화/비활성화
4. 알림 그룹화 (같은 종목 5건 → "NVDA 외 5건")
```

**산출물**:
- `docs/planning/notification-strategy.md`

---

#### T5.6: E2E 테스트

**🧠 Gemini 담당** (E2E 시나리오 작성)
```
Playwright 시나리오 설계:
1. 사용자 플로우:
   - 로그인 → 전략 대시보드 접속
   - 장기 전략으로 NVDA 매수
   - 단기 전략으로 NVDA 매도 시도
   - 충돌 경고 확인
   - 주문 차단 확인
2. Edge case:
   - 네트워크 지연 시나리오
   - API 타임아웃 처리
```

**산출물**:
- `docs/planning/e2e-scenarios.md`

**🤖 Claude Code 담당** (E2E 테스트 구현)
```
test-engineer 에이전트가:
1. e2e/multi-strategy.spec.ts 생성
2. Gemini가 설계한 시나리오를 Playwright 코드로 변환
3. 테스트 실행 및 통과 확인
```

---

## 🔄 협업 워크플로우

### 표준 사이클 (각 태스크마다)

```
1. [Gemini] 설계 & 시나리오 작성 (30분)
   └─ 산출물: docs/planning/{task-name}-design.md

2. [Claude Code] 구현 (1~2시간)
   └─ 산출물: 코드 파일, 테스트 파일

3. [Gemini] 코드 리뷰 & 개선 제안 (20분)
   └─ 산출물: docs/planning/{task-name}-review.md

4. [Claude Code] 리팩토링 (30분)
   └─ 산출물: 개선된 코드

5. [Human] 승인 및 병합
```

---

## 💰 비용 최적화

| Phase | Claude Code 사용량 | Gemini 사용량 | 예상 비용 |
|-------|-------------------|--------------|-----------|
| Phase 0 | 6개 태스크 (설계) | 6개 태스크 (검토) | Claude: $5, Gemini: $0.5 |
| Phase 1-4 | 11개 태스크 (구현) | 11개 태스크 (검토) | Claude: $15, Gemini: $1 |
| Phase 5 | 6개 태스크 (구현) | 6개 태스크 (검토) | Claude: $8, Gemini: $0.8 |
| **총계** | **23개 태스크** | **23개 검토** | **Claude: $28, Gemini: $2.3** |

**절감 효과**: Gemini 활용으로 약 **80% 비용 절감** (전체 Claude 사용 시 $50 예상)

---

## 📝 문서 구조

```
docs/planning/
├── 01-multi-strategy-orchestration-plan.md        # 전체 기획 (완료)
├── 02-multi-strategy-orchestration-tasks.md       # 태스크 목록 (완료)
├── 03-multi-strategy-ai-division.md               # 이 문서 (AI 분업 전략)
│
├── phase0/
│   ├── schema-review-report.md                    # [Gemini] T0.1 검토
│   ├── orm-review.md                               # [Gemini] T0.2 검토
│   ├── repository-pattern-review.md                # [Gemini] T0.3 검토
│   ├── api-schema-review.md                        # [Gemini] T0.4 검토
│   └── test-scenarios.md                           # [Gemini] T0.6 시나리오
│
├── phase1/
│   ├── phase1-code-review.md                       # [Gemini] T1.1 검토
│   ├── seed-strategies.json                        # [Gemini] T1.2 설계
│   └── api-test-scenarios.md                       # [Gemini] T1.3 시나리오
│
├── phase2/
│   ├── concurrency-analysis.md                     # [Gemini] T2.1 검토
│   ├── transaction-scenarios.md                    # [Gemini] T2.2 검토
│   └── ownership-transfer-rules.md                 # [Gemini] T2.3 설계
│
├── phase3/
│   ├── conflict-detection-algorithm.md             # [Gemini] T3.1 설계
│   ├── priority-rules-matrix.md                    # [Gemini] T3.2 설계
│   └── conflict-log-analysis.md                    # [Gemini] T3.3 분석
│
├── phase4/
│   ├── order-manager-integration.md                # [Gemini] T4.1 검증
│   └── event-subscriber-strategy.md                # [Gemini] T4.2 설계
│
└── phase5/
    ├── api-documentation.md                        # [Gemini] T5.1 문서화
    ├── api-optimization.md                         # [Gemini] T5.2 최적화
    ├── dashboard-wireframe.md                      # [Gemini] T5.3 설계
    ├── table-ux-improvements.md                    # [Gemini] T5.4 UX
    ├── notification-strategy.md                    # [Gemini] T5.5 전략
    └── e2e-scenarios.md                            # [Gemini] T5.6 시나리오
```

---

## 🚀 시작 방법

### Gemini에게 첫 번째 작업 요청:

```
01-multi-strategy-orchestration-plan.md 파일을 읽고,
T0.1 (DB 스키마 정의)에 대한 설계 검토를 해줘.

특히:
1. strategies, position_ownership, conflict_logs 테이블의 인덱스 전략
2. FK 관계 설정 (CASCADE vs RESTRICT)
3. JSONB 사용 타당성 (strategies.config_metadata)
4. 성능 병목 예측

검토 결과를 docs/planning/phase0/schema-review-report.md에 저장할 수 있게
마크다운 형식으로 작성해줘.
```

### Claude Code에게 두 번째 작업 요청:

```
database-orchestrator 에이전트를 사용해서 T0.1을 수행해줘:
1. db-schema-manager로 3개 테이블 스키마 JSON 생성
2. Gemini가 작성한 docs/planning/phase0/schema-review-report.md의
   피드백을 반영해서 스키마 최적화
3. 마이그레이션 SQL 생성
```

---

**Generated by**: Claude Code
**Date**: 2026-01-11
**Status**: ✅ AI 분업 전략 완성
