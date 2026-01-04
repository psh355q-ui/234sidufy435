# 00_Spec_Kit 업데이트 계획

**작성일**: 2026-01-04
**목적**: 00_Spec_Kit 폴더 전체 업데이트 전략 및 변경점 검토
**기준 문서**: `260104_Complete_Development_History_and_Structure.md`

---

## 📋 현재 상태 분석

### 현재 파일 목록 (19개)

#### 🟢 최신 상태 유지 필요 (4개)
1. **README.md** (2025-12-28)
   - 상태: 업데이트 필요 ⚠️
   - 이유: MVP 전환, Skills Migration, 2026 업데이트 미반영

2. **251228_War_Room_Complete.md**
   - 상태: Legacy 8-Agent 기준 (MVP 전환 전)
   - 이유: 2025-12-31 MVP 전환으로 인해 구조 변경됨

3. **2025_System_Overview.md**
   - 상태: 업데이트 필요 ⚠️
   - 이유: MVP 구조, Shadow Trading, Position Sizing 미반영

4. **2025_Agent_Catalog.md**
   - 상태: 업데이트 필요 ⚠️
   - 이유: 8-Agent → 3+1 MVP Agent로 변경됨

#### 🟡 참고용 유지 (15개)
- `251210_*` 시리즈 (4개) - Historical
- `251214_*` 시리즈 (1개) - Historical
- `251215_*` 시리즈 (6개) - Historical
- `2025_Implementation_Progress.md` - Phase 진행 상황 (업데이트 가능)
- 기타 분석 문서 (3개)

---

## 🎯 주요 변경 사항 (2025-12-28 → 2026-01-04)

### 1. MVP 시스템 전환 (2025-12-31) 🔥

**Legacy (8-Agent)**:
```
8개 독립 Agent → Weighted Voting → Consensus
- Trader (15%)
- Risk (20%)
- Sentiment (8%)
- News (10%)
- Analyst (15%)
- Macro (10%)
- Institutional (10%)
- ChipWar (12%)
```

**MVP (3+1 Agent)**:
```
3+1 통합 Agent → Weighted Voting → PM Final Decision
- Trader MVP (35%) - Attack (흡수: Trader, ChipWar opportunity)
- Risk MVP (35%) - Defense + Position Sizing (흡수: Risk, Sentiment, DividendRisk)
- Analyst MVP (30%) - Information (흡수: News, Macro, Institutional, ChipWar geopolitics)
- PM Agent MVP - Final Decision Maker (NEW)
```

**성과**:
- 비용: 67% 절감
- 속도: 67% 향상 (30초 → 10초)
- API 호출: 8회 → 3회

---

### 2. Execution Layer 추가 (2025-12-31)

**새로운 컴포넌트**:
1. **Execution Router**
   - Fast Track (< 1s): Stop Loss hit, 일일 손실 > -5%, VIX > 40
   - Deep Dive (~10s): 신규 포지션, 리밸런싱, 대형 포지션

2. **Order Validator**
   - 8개 Hard Rules (Code-enforced)
   - Position size > 30% → REJECT
   - No Stop Loss → REJECT

3. **Shadow Trading Engine**
   - 조건부 실행 (3개월 검증)
   - Initial Capital: $100,000
   - 현재 (2026-01-04): +$1,274.85 (+1.27%)

---

### 3. Position Sizing 시스템 (NEW)

Risk Agent MVP의 핵심 기능:
```python
# Step 1: Risk-based sizing
base_size = (Account Risk / Stop Loss Distance) × Account Value

# Step 2: Confidence adjustment
confidence_adjusted = base_size × Agent Confidence

# Step 3: Volatility adjustment
risk_adjusted = confidence_adjusted × Risk Multiplier

# Step 4: Hard cap
final_size = min(risk_adjusted, 10% of portfolio)
```

---

### 4. Skills Migration (2026-01-02)

**새로운 구조**:
```
backend/ai/skills/war_room_mvp/
├── trader_agent_mvp/
│   ├── SKILL.md
│   └── handler.py
├── risk_agent_mvp/
│   ├── SKILL.md
│   └── handler.py
├── analyst_agent_mvp/
│   ├── SKILL.md
│   └── handler.py
├── pm_agent_mvp/
│   ├── SKILL.md
│   └── handler.py
└── orchestrator_mvp/
    ├── SKILL.md
    └── handler.py
```

**Dual Mode 지원**:
- Direct Class Mode (기본값)
- Skill Handler Mode (환경 변수로 전환)
- 환경 변수: `WAR_ROOM_MVP_USE_SKILLS=true/false`

---

### 5. 데이터베이스 최적화 (2026-01-02)

**Phase 1 완료**:
- 복합 인덱스 추가 (6개)
- N+1 쿼리 제거 (repository.py)
- TTL 캐싱 구현 (5분 캐시)

**성과**:
- War Room MVP DB 쿼리: 0.5-1.0s → 0.3-0.5s
- 전체 응답 시간: 12.76s (목표 <15s 달성)

**새로운 테이블 (2026-01-03)**:
- `shadow_trading_sessions`
- `shadow_trading_positions`
- `agent_weights_history`

---

### 6. 신규 기능 (2026-01-01 ~ 01-04)

**Deep Reasoning 통합** (2026-01-01):
- 분석 이력 DB 저장
- REST API 제공

**Macro Context Updater** (2026-01-04 검증):
- 매일 09:00 KST 자동 실행
- Claude API로 서사 생성
- Market Regime, Fed Stance, VIX 분석

**Shadow Trading 모니터링** (2026-01-04):
- 실시간 포지션 정보
- Stop Loss 체크
- P&L 계산

---

## 📝 업데이트 전략

### Phase 1: 긴급 업데이트 (즉시)

#### 1.1 README.md 업데이트
**변경 사항**:
- "Last Updated": 2026-01-04로 변경
- "Latest" 문서: `260104_Current_System_State.md`로 변경
- MVP 전환 내용 추가
- Shadow Trading 현황 추가
- 2026 시리즈 문서 추가

#### 1.2 260104_Current_System_State.md 생성 (NEW)
**목적**: 251228_War_Room_Complete.md 대체

**주요 섹션**:
1. Executive Summary
   - MVP 시스템 (3+1 Agent)
   - Shadow Trading 현황 (Day 4)
   - Production Ready 상태

2. MVP Agent 구성
   - Trader MVP (35%)
   - Risk MVP (35%) + Position Sizing
   - Analyst MVP (30%)
   - PM Agent MVP

3. Execution Layer
   - Execution Router
   - Order Validator (8 Hard Rules)
   - Shadow Trading Engine

4. Skills Architecture
   - Dual Mode 지원
   - SKILL.md + handler.py 구조

5. Database Optimization
   - 복합 인덱스
   - N+1 쿼리 제거
   - TTL 캐싱

6. 현재 상태
   - Shadow Trading: +$1,274.85 (+1.27%)
   - War Room MVP 응답 시간: 12.76s
   - Production Ready

---

### Phase 2: 기존 문서 업데이트 (단기)

#### 2.1 2025_System_Overview.md 업데이트
**변경 사항**:
- Agent 구조: 8-Agent → 3+1 MVP
- Execution Layer 추가
- Position Sizing 설명 추가
- Database 스키마: 14개 → 17개 테이블
- Shadow Trading 섹션 추가

#### 2.2 2025_Agent_Catalog.md 업데이트
**변경 사항**:
- War Room Agents: 8개 → 3+1 MVP
- 각 MVP Agent 상세 설명:
  - Trader MVP (흡수된 Agent 명시)
  - Risk MVP + Position Sizing
  - Analyst MVP
  - PM Agent MVP (NEW)
- Legacy Agent는 "Deprecated" 섹션으로 이동

#### 2.3 2025_Implementation_Progress.md 업데이트
**변경 사항**:
- Progress: 88% → 95%
- Phase J: MVP Migration (100%)
- Phase K: Shadow Trading Phase 1 (5% - Day 4/90)
- Cost tracking 업데이트 (67% 절감 반영)

---

### Phase 3: 새로운 문서 생성 (중기)

#### 3.1 260104_MVP_Architecture.md (NEW)
**목적**: MVP 시스템 아키텍처 상세 설명

**주요 섹션**:
- MVP 전환 배경
- 3+1 Agent 설계 철학
- Position Sizing 알고리즘
- Execution Router 로직
- Order Validator Rules
- Shadow Trading 검증 전략

#### 3.2 260104_Database_Schema.md (NEW)
**목적**: 데이터베이스 스키마 전체 문서화

**주요 섹션**:
- 17개 테이블 ERD
- 복합 인덱스 전략
- 최적화 히스토리
- 쿼리 성능 분석

---

### Phase 4: Legacy 문서 정리 (장기)

#### 4.1 Legacy 폴더 이동
**대상**:
- `251210_*` 시리즈 → `00_Spec_Kit/legacy/`
- `251214_*` 시리즈 → `00_Spec_Kit/legacy/`
- `251215_*` 시리즈 → `00_Spec_Kit/legacy/`

#### 4.2 251228_War_Room_Complete.md 처리
**옵션 1**: Legacy로 이동
**옵션 2**: "Legacy 8-Agent" 섹션 추가 후 유지
**권장**: 옵션 2 (참고용 가치 있음)

---

## 🔄 변경점 매트릭스

### 핵심 개념 변경

| 항목 | Before (251228) | After (260104) | 변경 유형 |
|------|-----------------|----------------|-----------|
| **Agent 구조** | 8 독립 Agent | 3+1 MVP Agent | 🔥 Major |
| **비용** | 기준 | -67% | 🔥 Major |
| **응답 시간** | ~30초 | ~10초 | 🔥 Major |
| **API 호출** | 8회 | 3회 | 🔥 Major |
| **Position Sizing** | 없음 | Risk MVP 포함 | 🔥 Major |
| **Execution Router** | 없음 | Fast Track/Deep Dive | ✨ New |
| **Order Validator** | 없음 | 8 Hard Rules | ✨ New |
| **Shadow Trading** | 계획 | 진행 중 (Day 4) | ✨ New |
| **Skills Architecture** | 없음 | SKILL.md + handler.py | ✨ New |
| **DB Tables** | 14개 | 17개 | 📊 Update |
| **DB 최적화** | 없음 | 복합 인덱스, 캐싱 | ✨ New |

---

## 📅 실행 일정

### 즉시 (2026-01-04)
- [ ] README.md 업데이트
- [ ] 260104_Current_System_State.md 생성
- [ ] 이 업데이트 계획 문서 검토

### 단기 (2026-01-05)
- [ ] 2025_System_Overview.md 업데이트
- [ ] 2025_Agent_Catalog.md 업데이트
- [ ] 2025_Implementation_Progress.md 업데이트

### 중기 (2026-01-06 ~ 01-10)
- [ ] 260104_MVP_Architecture.md 생성
- [ ] 260104_Database_Schema.md 생성

### 장기 (2026-01-11 ~ 01-15)
- [ ] Legacy 문서 정리
- [ ] 전체 문서 검증

---

## ⚠️ 주의사항

### DO NOT Update (절대 수정 금지)
- `251210_*` 시리즈 (Historical snapshot)
- `251214_*` 시리즈 (Historical snapshot)
- `251215_*` 시리즈 (Historical snapshot)
- `00_Project_Summary.md`, `01_DB_Storage_Analysis.md`, `02_SpecKit_Progress_Report.md` (Legacy 참고용)

### 업데이트 시 필수 체크리스트
- [ ] "Last Updated" 날짜 변경
- [ ] Version 번호 증가 (2.1 → 2.2)
- [ ] Changelog 섹션 추가
- [ ] Cross-reference 링크 확인
- [ ] 기존 섹션과의 일관성 확인

---

## 📊 변경 영향도 분석

### High Impact (즉시 업데이트 필요)
1. **README.md** - 모든 문서의 진입점
2. **260104_Current_System_State.md** - 최신 상태 반영

### Medium Impact (단기 업데이트)
3. **2025_System_Overview.md** - 시스템 아키텍처 이해
4. **2025_Agent_Catalog.md** - Agent 개발/운영

### Low Impact (중장기 업데이트)
5. **2025_Implementation_Progress.md** - 진행 상황 추적
6. **260104_MVP_Architecture.md** - MVP 상세 이해

---

## 🎯 성공 기준

### 문서 품질
- [ ] 모든 링크 정상 작동
- [ ] 코드 예제 최신 상태 반영
- [ ] 날짜/버전 정보 정확
- [ ] 용어 일관성 유지 (8-Agent → MVP, Legacy 등)

### 사용자 경험
- [ ] 신규 개발자가 README에서 최신 정보 확인 가능
- [ ] MVP 시스템 이해를 위한 충분한 설명
- [ ] Legacy 시스템과의 차이점 명확

### 유지보수성
- [ ] 향후 업데이트 용이성
- [ ] 문서 간 중복 최소화
- [ ] 명확한 파일명 규칙

---

**작성 완료**: 2026-01-04
**검토 필요**: 즉시
**실행 시작**: 사용자 승인 후
**예상 소요**: 2-3일 (전체 완료)

---

## 다음 단계

1. 이 계획 문서 검토
2. Phase 1 (긴급 업데이트) 실행
3. Phase 2-4 순차 진행
