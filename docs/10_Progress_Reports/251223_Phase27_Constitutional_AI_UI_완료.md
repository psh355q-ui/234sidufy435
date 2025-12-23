# Phase 27 - Constitutional AI + Frontend UI 완료

**날짜**: 2025-12-23
**Phase**: 27.0 - Constitutional AI 강화 + 프론트엔드 UI 추가
**상태**: ✅ 완료

---

## 📋 완료된 작업

### Part 1: Constitutional AI 강화

#### 1️⃣ Constitutional Validator 통합

**기존 문제**:
- War Room에서 `constitutional_valid=True` 하드코딩됨
- 실제 헌법 검증 없이 모든 제안 통과

**해결**:
- [constitution.py](backend/constitution/constitution.py) 기존 Constitutional Validator 활용
- [war_room_router.py:426-454](backend/api/war_room_router.py#L426-L454) War Room에 통합

**주요 코드** ([war_room_router.py:426-454](backend/api/war_room_router.py#L426-L454)):

```python
# 2. Constitutional 검증
constitution = Constitution()

# 제안서 생성
proposal = {
    "ticker": ticker,
    "action": pm_decision["consensus_action"],
    "confidence": pm_decision["consensus_confidence"],
    "is_approved": not execute_trade,  # execute_trade=False면 인간 승인 필요
}

# Context 생성
context = {
    "total_capital": 100000,  # TODO: 실제 계좌 잔고에서 가져오기
    "daily_trades": 0,  # TODO: 오늘 거래 횟수
    "weekly_trades": 0,  # TODO: 이번주 거래 횟수
}

# Constitutional 검증 실행
is_valid, violations, violated_articles = constitution.validate_proposal(
    proposal=proposal,
    context=context,
    skip_allocation_rules=True  # War Room 단계에서는 배분 규칙 스킵
)

logger.info(f"⚖️ Constitutional validation: {is_valid}")
if not is_valid:
    logger.warning(f"⚠️ Violations: {violations}")
    logger.warning(f"⚠️ Violated articles: {violated_articles}")

# DB 저장
session = AIDebateSession(
    ...
    constitutional_valid=is_valid,  # 🆕 실제 검증 결과
    ...
)
```

#### 2️⃣ Constitutional 조항 (5개 조항)

**헌법 조항** ([constitution.py:31-52](backend/constitution/constitution.py#L31-L52)):

```python
ARTICLES = {
    "제1조": {
        "title": "자본 보존 우선",
        "description": "자본 보존이 수익 추구에 우선한다"
    },
    "제2조": {
        "title": "설명 가능성",
        "description": "설명되지 않는 수익은 취하지 않는다"
    },
    "제3조": {
        "title": "인간 최종 결정권",
        "description": "최종 실행권은 인간에게 있다"
    },
    "제4조": {
        "title": "강제 개입",
        "description": "시장이 위험하면 시스템이 강제 개입한다"
    },
    "제5조": {
        "title": "헌법 개정",
        "description": "헌법 개정은 인간 승인이 필요하다"
    }
}
```

#### 3️⃣ 검증 로직

**주요 검증 항목**:
1. **리스크 검증** (제1조)
   - 포지션 크기 제한 (총 자본 대비)
   - 최대 포지션 크기

2. **자산 배분 검증** (제1조)
   - 주식/현금 배분 비율
   - 시장 상황별 적정 배분

3. **거래 제약 검증** (제3조)
   - 일일 거래 횟수 제한
   - 주간 거래 횟수 제한

4. **주문 크기 검증** (제1조)
   - 주문 금액 vs 총 자본
   - 주문 금액 vs 일일 거래량

5. **인간 승인 필수** (제3조)
   - `execute_trade=False`면 인간 승인 필요
   - `execute_trade=True`면 자동 실행 (단, Constitutional 검증 통과 필수)

---

### Part 2: 프론트엔드 UI 추가

#### 1️⃣ 주문 히스토리 페이지 ([Orders.tsx](frontend/src/pages/Orders.tsx))

**주요 기능**:
- 전체 주문 목록 표시
- 상태별 필터 (전체/대기중/체결/취소)
- 티커 검색
- 실시간 업데이트 (10초 간격)
- 주문 상세 정보 (ID, 티커, 액션, 수량, 가격, 상태, 브로커)

**통계 대시보드**:
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│    전체     │     체결    │    대기     │    취소     │
│      3      │      1      │      1      │      1      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**주문 테이블**:
| 주문 ID | 티커 | 액션 | 수량 | 가격 | 총액 | 상태 | 브로커 | 시그널 | 생성 시각 | 체결 시각 |
|---------|------|------|------|------|------|------|--------|--------|-----------|-----------|
| KIS20251223001 | AAPL | BUY | 10 | $178.50 | $1,785.00 | FILLED | KIS | 14 | 2025-12-23 12:37 | 2025-12-23 12:37 |

**UI 특징**:
- 상태별 색상 구분 (체결=녹색, 대기=주황, 취소=회색)
- 액션별 색상 (BUY=파란색, SELL=빨간색)
- 반응형 디자인 (모바일 지원)
- 검색 & 필터 기능

#### 2️⃣ 포트폴리오 대시보드 ([Portfolio.tsx](frontend/src/pages/Portfolio.tsx))

**주요 기능**:
- 전체 자산 현황 요약
- 보유 종목 목록 (실시간 가격)
- 손익 계산 (총 손익 + 일일 손익)
- 자산 배분 시각화

**요약 카드** (4개):
```
┌────────────────────────┐  ┌────────────────────────┐
│   💰 총 자산            │  │   📈 투자 금액          │
│   $127,580.50          │  │   $82,380.50           │
│   +$1,250.30 (+0.98%)  │  │   64.6% 배분           │
│   오늘                  │  │                        │
└────────────────────────┘  └────────────────────────┘

┌────────────────────────┐  ┌────────────────────────┐
│   💵 현금               │  │   🎯 총 손익            │
│   $45,200.00           │  │   +$7,380.50           │
│   35.4% 보유           │  │   +9.84%               │
└────────────────────────┘  └────────────────────────┘
```

**보유 종목 테이블**:
| 티커 | 수량 | 평균 단가 | 현재가 | 평가액 | 손익 | 수익률 | 일일 손익 | 일일 수익률 |
|------|------|-----------|--------|--------|------|--------|-----------|-------------|
| AAPL | 100 | $175.20 | $178.50 | $17,850.00 | +$330.00 | +1.88% | +$150.00 | +0.84% |
| NVDA | 50 | $480.00 | $495.20 | $24,760.00 | +$760.00 | +3.17% | +$380.00 | +1.56% |
| MSFT | 75 | $385.00 | $392.10 | $29,407.50 | +$532.50 | +1.84% | +$225.00 | +0.77% |
| GOOGL | 80 | $138.50 | $132.90 | $10,632.00 | -$448.00 | -4.04% | -$160.00 | -1.48% |

**자산 배분 차트**:
```
┌────────────────────────────────────────────────────────┐
│ ████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░ │
│         64.6% 투자 중                  35.4% 현금       │
└────────────────────────────────────────────────────────┘
```

**UI 특징**:
- 그라데이션 요약 카드 (각기 다른 색상)
- 손익 색상 구분 (수익=녹색, 손실=빨간색)
- 실시간 업데이트 (30초 간격)
- 반응형 디자인

---

## 🎯 시스템 플로우

### Constitutional 검증 플로우
```
┌─────────────────────────────────────────────────────────┐
│ 1. War Room Debate                                       │
│    - 7 agents vote                                       │
│    - PM makes consensus                                  │
└───────────────┬─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Constitutional Validation                             │
│    - Create proposal                                     │
│    - Validate against 5 articles                         │
│    - Check violations                                    │
└───────────────┬─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Decision                                              │
│    ✅ Valid → Save to DB (constitutional_valid=True)    │
│    ❌ Invalid → Save violations to DB                   │
└───────────────┬─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Signal Generation (if confidence >= 70%)             │
│    - Create TradingSignal                                │
│    - Link to session                                     │
└───────────────┬─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Order Execution (if execute_trade=True & valid)      │
│    - Calculate position size (risk management)           │
│    - Execute KIS order                                   │
│    - Save to orders table                                │
└─────────────────────────────────────────────────────────┘
```

### 전체 시스템 아키텍처
```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (React)                       │
├──────────────────────────────────────────────────────────┤
│ • War Room UI       - 토론 시작 & 결과 표시              │
│ • Orders Page       - 주문 히스토리 관리                 │
│ • Portfolio Page    - 포트폴리오 대시보드                │
└────────────────────┬─────────────────────────────────────┘
                     ↓ REST API
┌──────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                      │
├──────────────────────────────────────────────────────────┤
│ • War Room Router   - 토론 & Constitutional 검증         │
│ • KIS Integration   - 실제 주문 실행                     │
│ • Constitution      - 헌법 조항 검증                     │
└────────────────────┬─────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│              Database (PostgreSQL)                        │
├──────────────────────────────────────────────────────────┤
│ • ai_debate_sessions   - 토론 세션 & Constitutional 결과 │
│ • trading_signals      - 시그널 생성                     │
│ • orders               - 주문 실행 내역                  │
└──────────────────────────────────────────────────────────┘
```

---

## 🔧 주요 파일

### Backend
- [war_room_router.py](backend/api/war_room_router.py) - Constitutional 검증 통합
- [constitution.py](backend/constitution/constitution.py) - 헌법 조항 & 검증 로직
- [risk_limits.py](backend/constitution/risk_limits.py) - 리스크 제한 규칙
- [allocation_rules.py](backend/constitution/allocation_rules.py) - 자산 배분 규칙
- [trading_constraints.py](backend/constitution/trading_constraints.py) - 거래 제약 조건

### Frontend
- [Orders.tsx](frontend/src/pages/Orders.tsx) - 주문 히스토리 페이지
- [Orders.css](frontend/src/pages/Orders.css) - 주문 페이지 스타일
- [Portfolio.tsx](frontend/src/pages/Portfolio.tsx) - 포트폴리오 대시보드
- [Portfolio.css](frontend/src/pages/Portfolio.css) - 포트폴리오 스타일

---

## ✅ Phase 27 완료 체크리스트

### Constitutional AI
- [x] Constitutional Validator 통합
- [x] War Room에 검증 로직 추가
- [x] `is_approved` 파라미터로 인간 승인 제어
- [x] 검증 결과 DB 저장 (`constitutional_valid`)
- [x] 로그 출력 (위반 사항)

### 프론트엔드 UI
- [x] Orders 페이지 구현
- [x] 주문 필터 기능 (상태별, 티커)
- [x] 주문 통계 대시보드
- [x] Portfolio 페이지 구현
- [x] 포트폴리오 요약 카드
- [x] 보유 종목 테이블
- [x] 자산 배분 차트
- [x] 반응형 디자인 (모바일 지원)

---

## 📝 TODO (미완성 항목)

### 1. 실제 API 연결
**현재**: Mock 데이터 사용
**필요**:
- [ ] `/api/orders` 엔드포인트 구현
- [ ] `/api/portfolio` 엔드포인트 구현
- [ ] KIS 계좌 잔고 연동

### 2. Constitutional Context 개선
**현재**: 하드코딩된 값 사용
```python
context = {
    "total_capital": 100000,  # TODO: 실제 계좌 잔고
    "daily_trades": 0,        # TODO: 오늘 거래 횟수
    "weekly_trades": 0,       # TODO: 이번주 거래 횟수
}
```

**필요**:
- [ ] 실제 계좌 잔고 조회
- [ ] 거래 횟수 통계 (DB 쿼리)
- [ ] 시장 상황 (market_regime) 추가

### 3. 주문 상태 추적
**현재**: 주문 생성 후 상태 업데이트 없음
**필요**:
- [ ] KIS 주문 체결 웹훅/폴링
- [ ] PENDING → FILLED 자동 업데이트
- [ ] 체결 시간 기록 (`filled_at`)

### 4. 프론트엔드 라우팅
**필요**:
- [ ] React Router 설정
- [ ] 네비게이션 메뉴 추가
- [ ] `/orders`, `/portfolio` 경로 설정

---

## 🚀 다음 단계 옵션

### Option 1: REAL MODE 실전 테스트
**내용**: `execute_trade=true`로 실제 주문 실행 테스트
- Constitutional 검증 통과 여부 확인
- KIS 주문 체결 확인
- 포트폴리오 업데이트 확인

**명령어**:
```bash
python test_real_mode.py AAPL --execute
```

### Option 2: Phase 25.1 - 24시간 수익률 추적
**내용**: 에이전트 성과 측정 시스템
- 토론 시점 vs 24시간 후 가격 비교
- 에이전트별 정확도 계산
- 자기학습용 피드백 데이터

### Option 3: API 엔드포인트 구현
**내용**: 프론트엔드에 필요한 API 완성
- `/api/orders` - 주문 히스토리 조회
- `/api/portfolio` - 포트폴리오 현황
- `/api/portfolio/positions` - 보유 종목 상세

### Option 4: 프론트엔드 통합
**내용**: React Router + 네비게이션
- 주문/포트폴리오 페이지 라우팅
- 상단 네비게이션 바 추가
- War Room ↔ Orders ↔ Portfolio 이동

---

## 💡 개선 아이디어

### 1. Constitutional 알림
- 위반 사항 발생 시 Telegram 알림
- 사용자에게 승인 요청 (Telegram 버튼)

### 2. Constitutional Dashboard
- 위반 사항 히스토리 페이지
- 조항별 통계 (가장 많이 위반되는 조항)
- 시간대별 위반 트렌드

### 3. 주문 취소/정정 기능
- 프론트엔드에서 주문 취소 버튼
- KIS API 주문 취소 연동
- 상태 업데이트 (CANCELLED)

### 4. 실시간 가격 업데이트
- WebSocket 연동
- 포트폴리오 실시간 손익 업데이트
- 가격 변동 알림

---

**작성**: 2025-12-23
**상태**: ✅ Phase 27 완료, 프론트엔드 UI Mock 구현 완료
**우선순위**: REAL MODE 실전 테스트 or API 엔드포인트 구현
