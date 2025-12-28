# AI Trading System - 프로젝트 전체 개요

**최종 업데이트**: 2025-12-28
**버전**: v1.0 (Production Ready)
**작성자**: AI Trading System Team

---

## 📋 목차

1. [프로젝트 소개](#프로젝트-소개)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [8개 War Room Agent 소개](#8개-war-room-agent-소개)
4. [폴더 구조 및 파일 설명](#폴더-구조-및-파일-설명)
5. [핵심 기능](#핵심-기능)
6. [API 엔드포인트](#api-엔드포인트)
7. [데이터베이스 스키마](#데이터베이스-스키마)
8. [실행 방법](#실행-방법)
9. [테스트 방법](#테스트-방법)
10. [환경 설정](#환경-설정)

---

## 프로젝트 소개

### 개요
**AI Trading System**은 8개의 전문 AI Agent가 협업하여 투자 의사결정을 내리는 자동 트레이딩 시스템입니다.

### 핵심 특징
- ✅ **8개 War Room Agent** - 각기 다른 전문 분야의 AI가 투표로 의사결정
- ✅ **7개 Action System** - BUY/SELL/HOLD/MAINTAIN/REDUCE/INCREASE/DCA
- ✅ **자기학습 시스템** - 매일 자동으로 성과 분석 및 가중치 조정
- ✅ **실시간 데이터 수집** - Yahoo Finance, FRED, FinViz, Social Sentiment
- ✅ **성과 추적 대시보드** - 6개 API 엔드포인트 + Prometheus 메트릭
- ✅ **Hallucination Prevention** - 3-gate 검증으로 AI 환각 방지

### 현재 상태
**Production Ready** - 실거래 환경 투입 가능

### 테스트 성과
- War Room Agent 통합 테스트: 100% (8/8 agents)
- 데이터 수집 파이프라인: 100% (10/10 cycles)
- 자기학습 시스템: 정상 작동 (매일 00:00 UTC)

---

## 시스템 아키텍처

### 전체 흐름도

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. 데이터 수집 (30초 주기)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Yahoo   │  │   FRED   │  │  FinViz  │  │  Social  │       │
│  │ Finance  │  │  (Macro) │  │  (News)  │  │(Sentiment)│       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  주가, RSI     금리, 유가    뉴스 감성    Twitter/Reddit      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         2. War Room (8 AI Agents, Weighted Voting)              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │   Risk   │ │  Trader  │ │ Analyst  │ │ ChipWar  │         │
│  │   20%    │ │   15%    │ │   15%    │ │   12%    │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │   News   │ │  Macro   │ │Instit.   │ │Sentiment │         │
│  │   10%    │ │   10%    │ │   10%    │ │    8%    │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│                                                                 │
│  각 Agent → Action (7개) + Confidence (0.0~1.0)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              3. 투표 집계 (Weighted Voting)                      │
│  • Score = Σ(Agent Weight × Confidence × Action)               │
│  • 최고 점수 액션 선택                                          │
│  • Consensus Confidence 계산                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  4. War Room Executor                           │
│  • Position Sizing (Constitution Rules)                        │
│  • HOLD/MAINTAIN → Skip (주문 없음)                            │
│  • BUY/SELL → 100% size                                        │
│  • REDUCE/INCREASE/DCA → 50% size                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    5. KIS Broker (실거래)                        │
│  • Market orders (BUY/SELL)                                    │
│  • Real-time execution                                         │
│  • Result storage (DB)                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          6. 자기학습 루프 (Daily 00:00 UTC)                      │
│  • 6개 Agent 독립 학습 (News, Trader, Risk, Macro, Instit, Analyst)│
│  • Hallucination Prevention (3-gate validation)                │
│  • Agent 가중치 자동 조정 (30일 성과 기반)                      │
│  • Confidence gap 보정                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              7. 성과 추적 & 모니터링                             │
│  • Performance Dashboard (6 APIs)                              │
│  • Prometheus Metrics                                          │
│  • Grafana Visualization                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8개 War Room Agent 소개

### 1. Risk Agent (20% 가중치) - 리스크 관리 전문가

**역할**: VaR 계산, 포지션 크기 결정, 손절매 시점 판단

**주요 로직**:
- **VaR (Value at Risk)**: 과거 30일 변동성 기반 계산
- **포지션 크기**: 변동성 높을수록 포지션 축소
- **손절매**: -10% 도달 시 SELL 신호
- **베타 조정**: 시장 베타 > 1.5 시 포지션 50% 축소

**파일**: [backend/ai/debate/risk_agent.py](../backend/ai/debate/risk_agent.py)

**예시 출력**:
```
Action: REDUCE
Confidence: 0.75
Reasoning: 중간 변동성 (28%), 베타 1.5 - 포지션 크기 50% 축소 권장
```

---

### 2. Trader Agent (15% 가중치) - 기술적 분석 전문가

**역할**: 차트 패턴, 기술적 지표, 거래량 분석

**주요 로직**:
- **RSI (Relative Strength Index)**:
  - RSI > 70 → 과매수 (SELL)
  - RSI < 30 → 과매도 (BUY)
- **이동평균선 교차**:
  - Golden Cross (SMA20 > SMA50) → BUY
  - Death Cross (SMA20 < SMA50) → SELL
- **MACD**: MACD > Signal → 상승 추세
- **거래량**: 평균 대비 200% 이상 → 강한 신호

**파일**: [backend/ai/debate/trader_agent.py](../backend/ai/debate/trader_agent.py)

**예시 출력**:
```
Action: BUY
Confidence: 0.82
Reasoning: RSI 과매도 (28) + Golden Cross + 거래량 급증 (250%)
```

---

### 3. Analyst Agent (15% 가중치) - 펀더멘털 분석 전문가

**역할**: 재무제표, 밸류에이션, 경쟁사 비교

**주요 로직**:
- **P/E Ratio**:
  - P/E < 15 → 저평가 (BUY)
  - P/E > 30 → 고평가 (SELL)
- **실적 성장**:
  - EPS 성장률 > 15% → STRONG_BUY
  - 매출 성장률 > 10% → BUY
- **이익률**: Profit Margin > 20% → 우량 기업
- **경쟁사 비교**: 상대 밸류에이션 평가

**파일**: [backend/ai/debate/analyst_agent.py](../backend/ai/debate/analyst_agent.py)

**예시 출력**:
```
Action: BUY
Confidence: 0.78
Reasoning: 저평가 (P/E 12.5) + 실적 급성장 (EPS +25%, 매출 +18%) + 높은 이익률 (28%)
```

---

### 4. ChipWar Agent (12% 가중치) - 반도체 지정학 전문가

**역할**: 반도체 산업 지정학, 공급망 리스크, 자기학습

**주요 로직**:
- **티커 필터링**: NVDA, AMD, TSM, INTC, ASML 등 반도체 종목만 분석
- **지정학 시나리오**:
  - 미중 무역 전쟁
  - 대만 긴장
  - 칩스법 (CHIPS Act)
  - 수출 규제
- **ChipWarSimulator V2**: 1,000번 시뮬레이션으로 예상 수익률 계산
- **자기학습**: ChipIntelligence DB에 과거 시나리오 학습 결과 저장

**파일**: [backend/ai/debate/chip_war_agent.py](../backend/ai/debate/chip_war_agent.py)

**예시 출력**:
```
Action: BUY
Confidence: 0.88
Reasoning: 🇺🇸 CHIPS Act 수혜 + 중국 수출 규제 완화 전망 (시뮬레이션 평균 수익률 +15.2%)
```

**비반도체 종목**:
```
Action: MAINTAIN
Confidence: 0.00
Reasoning: AAPL is not a semiconductor ticker (chip war analysis skipped)
```

---

### 5. News Agent (10% 가중치) - 뉴스 감성 분석 전문가

**역할**: 뉴스 수집, 감성 분석, 티커 연관도 평가

**주요 로직**:
- **뉴스 수집**: FinViz, TechCrunch, Reuters 등
- **감성 분석**: Gemini 2.5 Flash로 -1.0 ~ +1.0 점수 계산
- **티커 연관도**: 뉴스가 해당 종목에 미치는 영향도 (0.0 ~ 1.0)
- **최신성**: 최근 15일 뉴스만 사용
- **가중 평균**: Relevance × Sentiment

**파일**: [backend/ai/debate/news_agent.py](../backend/ai/debate/news_agent.py)

**예시 출력**:
```
Action: BUY
Confidence: 0.85
Reasoning: 📰 긍정 뉴스 (평균 감성 +0.72, 3개 기사) - "NVDA announces new AI chip partnership"
```

---

### 6. Macro Agent (10% 가중치) - 거시경제 분석 전문가

**역할**: 금리, 인플레이션, 유가, 달러 지수 분석

**주요 로직**:
- **Fed 금리**:
  - 인하 사이클 → Risk ON (BUY)
  - 인상 사이클 → Risk OFF (SELL)
- **인플레이션 (CPI)**:
  - CPI < 3% → 안정적 (BUY)
  - CPI > 5% → 긴축 우려 (SELL)
- **유가 (WTI Crude)**:
  - 30일 변화율 > +20% → 인플레이션 압력 (SELL)
- **달러 지수 (DXY)**:
  - 30일 변화율 > +5% → 강달러 (SELL 주식)
- **수익률 곡선**:
  - 역전 (2Y > 10Y) → 경기 침체 우려 (SELL)

**파일**: [backend/ai/debate/macro_agent.py](../backend/ai/debate/macro_agent.py)

**예시 출력**:
```
Action: BUY
Confidence: 0.84
Reasoning: Fed 금리 인하 사이클 시작 (5.25% → 4.75% 전망) + CPI 2.8%로 목표치 근접 - Risk ON
```

---

### 7. Institutional Agent (10% 가중치) - 기관 투자자 추적 전문가

**역할**: 스마트 머니 흐름, 기관 매수 압력, 내부자 거래 분석

**주요 로직**:
- **기관 매수 압력**:
  - 13F 파일링 분석
  - 압력 > 70% → STRONG_BUY
  - 압력 < 30% → 기관 이탈 (SELL)
- **주요 기관**:
  - Berkshire Hathaway
  - Vanguard
  - BlackRock
  - Fidelity
- **내부자 거래**:
  - CEO/CFO 매수 → 추가 신뢰도
  - 대량 매도 → 경고 신호
- **스마트 머니 신호 강도**: VERY_BULLISH ~ VERY_BEARISH

**파일**: [backend/ai/debate/institutional_agent.py](../backend/ai/debate/institutional_agent.py)

**예시 출력**:
```
Action: BUY
Confidence: 0.78
Reasoning: 🏦 기관 매수 압력 강함 (75%) | 🎯 주요 기관 참여: Berkshire, Vanguard | 👔 내부자 대량 매수 감지
```

---

### 8. Sentiment Agent (8% 가중치) - 소셜 감성 분석 전문가

**역할**: Twitter/Reddit 감성, Fear & Greed Index, 트렌딩 분석

**주요 로직**:
- **소셜 감성**:
  - Twitter/Reddit 멘션 수집
  - 감성 점수 -1.0 ~ +1.0
- **Fear & Greed Index**:
  - 0-25: Extreme Fear → 역발상 BUY
  - 75-100: Extreme Greed → 과열 조정 SELL
- **트렌딩 순위**:
  - Top 10 → 높은 관심도
- **24시간 감성 변화**: 급격한 변화 감지

**파일**: [backend/ai/debate/sentiment_agent.py](../backend/ai/debate/sentiment_agent.py)

**예시 출력**:
```
Action: SELL
Confidence: 0.80
Reasoning: 부정 소셜 감성 (-0.52) + Extreme Greed (88) - 과열 조정 위험
```

---

## 폴더 구조 및 파일 설명

### 전체 폴더 구조

```
ai-trading-system/
├── backend/                        # 백엔드 코어
│   ├── ai/                         # AI 관련 모듈
│   │   ├── debate/                 # War Room Agents
│   │   │   ├── risk_agent.py       # Risk Agent (20%)
│   │   │   ├── trader_agent.py     # Trader Agent (15%)
│   │   │   ├── analyst_agent.py    # Analyst Agent (15%)
│   │   │   ├── chip_war_agent.py   # ChipWar Agent (12%)
│   │   │   ├── news_agent.py       # News Agent (10%)
│   │   │   ├── macro_agent.py      # Macro Agent (10%)
│   │   │   ├── institutional_agent.py # Institutional Agent (10%)
│   │   │   └── sentiment_agent.py  # Sentiment Agent (8%)
│   │   │
│   │   ├── learning/               # 자기학습 시스템
│   │   │   ├── learning_orchestrator.py      # 6 Agent 학습 조정
│   │   │   ├── daily_learning_scheduler.py   # 매일 00:00 UTC 자동 실행
│   │   │   ├── agent_weight_manager.py       # 가중치 동적 조정
│   │   │   ├── hallucination_detector.py     # Hallucination 방지
│   │   │   ├── statistical_validators.py     # 통계적 검증
│   │   │   ├── walk_forward_validator.py     # Walk-forward 검증
│   │   │   ├── news_agent_learning.py        # News Agent 학습
│   │   │   ├── trader_agent_learning.py      # Trader Agent 학습
│   │   │   ├── risk_agent_learning.py        # Risk Agent 학습
│   │   │   └── remaining_agents_learning.py  # Macro, Instit, Analyst 학습
│   │   │
│   │   └── monitoring/             # AI 성과 모니터링
│   │       └── bias_monitor.py     # 편향 감지
│   │
│   ├── api/                        # FastAPI 라우터
│   │   ├── war_room_router.py      # War Room 투표 API
│   │   ├── performance_router.py   # 성과 추적 API (6개 엔드포인트)
│   │   ├── weight_adjustment_router.py # 가중치 조정 API (4개 엔드포인트)
│   │   ├── monitoring_router.py    # 모니터링 API
│   │   └── ...                     # 기타 라우터
│   │
│   ├── database/                   # 데이터베이스
│   │   ├── models.py               # SQLAlchemy Models
│   │   ├── repository.py           # DB 연결 관리
│   │   └── migrations/             # Alembic 마이그레이션
│   │
│   ├── data/                       # 데이터 수집
│   │   └── collectors/
│   │       ├── yahoo_collector.py  # Yahoo Finance 수집
│   │       ├── fred_collector.py   # FRED 거시 데이터
│   │       ├── finviz_collector.py # FinViz 뉴스
│   │       ├── smart_money_collector.py # 기관 투자자
│   │       └── social_collector.py # Twitter/Reddit 감성
│   │
│   ├── trading/                    # 트레이딩 실행
│   │   ├── war_room_executor.py    # War Room 주문 실행
│   │   ├── broker/
│   │   │   └── kis_broker.py       # KIS Broker 연동
│   │   └── constitution.py         # 트레이딩 룰
│   │
│   ├── monitoring/                 # 시스템 모니터링
│   │   ├── ai_trading_metrics.py   # Prometheus 메트릭
│   │   ├── metrics_collector.py    # 메트릭 수집
│   │   ├── alert_manager.py        # 알림 시스템
│   │   └── circuit_breaker.py      # Circuit Breaker
│   │
│   ├── schemas/                    # Pydantic 스키마
│   │   └── base_schema.py          # SignalAction (7개 액션)
│   │
│   ├── tests/                      # 테스트
│   │   └── integration/
│   │       ├── test_agents_simple.py        # 6 Agent 테스트
│   │       ├── test_all_agents.py           # 8 Agent 테스트
│   │       └── test_data_collection_5min.py # 데이터 수집 테스트
│   │
│   ├── main.py                     # FastAPI 서버 (Daily Scheduler 통합)
│   └── requirements.txt            # Python 패키지
│
├── docs/                           # 문서
│   ├── PROJECT_OVERVIEW.md         # 이 문서 (프로젝트 전체 개요)
│   ├── 251228_War_Room_System_Complete.md      # War Room 완료 보고서
│   ├── 251228_Option3_Verification.md          # Option 3 검증
│   ├── 251228_Option3_Complete.md              # Option 3 완료
│   └── 251228_Development_Status_and_Roadmap.md # 개발 현황 및 로드맵
│
├── .env                            # 환경 변수 (API Keys)
└── README.md                       # 프로젝트 README
```

---

### 주요 폴더 상세 설명

#### 1. `backend/ai/debate/` - War Room Agents

**8개 Agent 파일** (위에서 상세 설명 완료):
- `risk_agent.py` (20%)
- `trader_agent.py` (15%)
- `analyst_agent.py` (15%)
- `chip_war_agent.py` (12%)
- `news_agent.py` (10%)
- `macro_agent.py` (10%)
- `institutional_agent.py` (10%)
- `sentiment_agent.py` (8%)

**공통 인터페이스**:
```python
async def analyze(ticker: str, context: Dict) -> Dict:
    """
    Returns:
        {
            "agent": "risk",
            "action": "BUY",  # 7개 중 하나
            "confidence": 0.75,
            "reasoning": "중간 변동성, 포지션 50% 축소 권장"
        }
    """
```

---

#### 2. `backend/ai/learning/` - 자기학습 시스템

| 파일 | 역할 | 실행 주기 |
|------|------|----------|
| `learning_orchestrator.py` | 6개 Agent 학습 조정 | Daily 00:00 UTC |
| `daily_learning_scheduler.py` | 자동 학습 스케줄러 | 서버 시작 시 |
| `agent_weight_manager.py` | 가중치 동적 조정 (30일 성과 기반) | On-demand API |
| `hallucination_detector.py` | 3-gate 검증 (환각 방지) | 학습 시 |
| `statistical_validators.py` | 통계적 유의성 검증 | 학습 시 |
| `walk_forward_validator.py` | Walk-forward 검증 | 학습 시 |
| `news_agent_learning.py` | News Agent 독립 학습 | Daily |
| `trader_agent_learning.py` | Trader Agent 독립 학습 | Daily |
| `risk_agent_learning.py` | Risk Agent 독립 학습 | Daily |
| `remaining_agents_learning.py` | Macro, Instit, Analyst 학습 | Daily |

**학습 프로세스**:
1. 30일 성과 데이터 수집
2. 통계적 검증 (p-value < 0.05)
3. Walk-forward 검증 (out-of-sample)
4. Cross-agent validation
5. Hallucination 감지 및 제거
6. 학습 결과 DB 저장
7. 가중치 조정

---

#### 3. `backend/api/` - API 라우터

| 라우터 | 엔드포인트 | 역할 |
|--------|-----------|------|
| `war_room_router.py` | `/api/war-room/vote` | War Room 투표 실행 |
| `performance_router.py` | `/api/performance/*` | 성과 추적 (6개 API) |
| `weight_adjustment_router.py` | `/api/weights/*` | 가중치 조정 (4개 API) |
| `monitoring_router.py` | `/api/monitoring/*` | 시스템 모니터링 |

**Performance API (6개)**:
1. `GET /summary` - 전체 성과 요약
2. `GET /by-action` - 액션별 성과
3. `GET /agents` - Agent별 성과
4. `GET /history?days=30` - 일별 추이
5. `GET /top-sessions?limit=10` - 최고/최저 성과
6. `GET /agents/by-action` - Agent × Action 매트릭스

**Weight Adjustment API (4개)**:
1. `POST /adjust` - 가중치 조정 실행
2. `GET /current` - 현재 가중치 조회
3. `GET /low-performers` - 저성과 Agent (accuracy < 50%)
4. `GET /overconfident` - 과신 Agent (confidence gap > 20%)

---

#### 4. `backend/database/` - 데이터베이스

**주요 Models** (`models.py`):
- `NewsArticle` - 뉴스 기사
- `NewsAnalysis` - 뉴스 감성 분석 결과
- `NewsTickerRelevance` - 뉴스-티커 연관도
- `PriceTracking` - 주가 추적 (War Room 투표 결과)
- `AgentVoteTracking` - Agent별 투표 기록
- `ChipIntelligence` - ChipWar Agent 학습 데이터
- `AnalysisResult` - 분석 결과 저장

**DB 연결** (`repository.py`):
```python
# Async session (FastAPI)
async_session = get_async_session()

# Sync session (Learning, Testing)
sync_session = get_sync_session()
```

---

#### 5. `backend/data/collectors/` - 데이터 수집

| Collector | 데이터 소스 | 수집 데이터 |
|-----------|------------|------------|
| `yahoo_collector.py` | Yahoo Finance | 주가, RSI, MACD, SMA, Volume |
| `fred_collector.py` | FRED | Fed Rate, CPI, GDP, Yield Curve, WTI, DXY |
| `finviz_collector.py` | FinViz | 뉴스 (제목, 소스, 감성) |
| `smart_money_collector.py` | SEC 13F | 기관 매수 압력, 내부자 거래 |
| `social_collector.py` | Twitter/Reddit | 소셜 감성, Fear & Greed Index |

**수집 주기**: 30초 (War Room 투표 시마다)

---

#### 6. `backend/trading/` - 트레이딩 실행

**War Room Executor** (`war_room_executor.py`):
```python
async def execute_war_room_decision(
    ticker: str,
    consensus_action: str,  # BUY/SELL/HOLD/...
    consensus_confidence: float
) -> Dict:
    """
    War Room 투표 결과를 실제 주문으로 변환

    Returns:
        {
            "status": "success",
            "order_id": "12345",
            "ticker": "AAPL",
            "action": "BUY",
            "quantity": 10,
            "price": 175.50
        }
    """
```

**Position Sizing Logic**:
- **BUY/SELL**: 100% size
- **REDUCE/INCREASE/DCA**: 50% size (점진적 조정)
- **HOLD/MAINTAIN**: Skip (주문 없음)

**KIS Broker** (`broker/kis_broker.py`):
- 한국투자증권 API 연동
- 모의투자 / 실거래 지원
- Market Order 실행

---

#### 7. `backend/monitoring/` - 시스템 모니터링

**Prometheus Metrics** (`ai_trading_metrics.py`):
```python
# Signal Generation
signals_generated_total
signals_by_type{type="BUY|SELL|HOLD"}
signals_by_ticker{ticker="AAPL|NVDA|MSFT"}

# Performance
agent_accuracy{agent="risk|trader|analyst"}
analysis_duration_seconds

# Cost
api_cost_usd_total
api_cost_daily_usd
```

**Circuit Breaker** (`circuit_breaker.py`):
- 일일 손실 -5% → 거래 중지
- 주간 손실 -10% → 시스템 정지
- 연속 손실 5회 → 알림

---

#### 8. `backend/tests/integration/` - 통합 테스트

| 테스트 파일 | 대상 | 성공률 |
|------------|------|--------|
| `test_agents_simple.py` | 6 Agents (DB 미사용) | 100% |
| `test_all_agents.py` | 8 Agents (전체) | 100% |
| `test_data_collection_5min.py` | 데이터 수집 파이프라인 | 100% |

**실행 방법**:
```bash
cd backend
python tests/integration/test_all_agents.py
python tests/integration/test_data_collection_5min.py
```

---

## 핵심 기능

### 1. War Room Weighted Voting

**투표 프로세스**:
```python
# 1. 각 Agent 분석
results = await asyncio.gather(
    risk_agent.analyze(ticker, context),
    trader_agent.analyze(ticker, context),
    analyst_agent.analyze(ticker, context),
    # ... 8개 Agent
)

# 2. 가중 점수 계산
vote_scores = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0, ...}
for result in results:
    action = result["action"]
    confidence = result["confidence"]
    weight = result["agent_weight"]  # 20%, 15%, ...

    vote_scores[action] += weight * confidence

# 3. 최종 Action 결정
consensus_action = max(vote_scores, key=vote_scores.get)
consensus_confidence = vote_scores[consensus_action]
```

---

### 2. 7개 Action System

| Action | 의미 | Execution | Position Size | 사용 Agent |
|--------|------|-----------|---------------|-----------|
| **BUY** | 신규 매수 | BUY | 100% | All |
| **SELL** | 전량 매도 | SELL | 100% | All |
| **HOLD** | 현상 유지 | SKIP | 0% | All |
| **MAINTAIN** | 포지션 유지 | SKIP | 0% | ChipWar |
| **REDUCE** | 포지션 축소 | SELL | 50% | Risk, Sentiment |
| **INCREASE** | 포지션 확대 | BUY | 50% | Analyst |
| **DCA** | 물타기 | BUY | 50% | Analyst |

**Action Mapping** (War Room Executor):
```python
action_mapping = {
    "BUY": "BUY",
    "SELL": "SELL",
    "HOLD": "HOLD",
    "MAINTAIN": "HOLD",    # Skip
    "REDUCE": "SELL",      # 50% size
    "INCREASE": "BUY",     # 50% size
    "DCA": "BUY"           # 50% size
}
```

---

### 3. 자기학습 시스템

**Daily Learning Cycle** (매일 00:00 UTC):
```
1. LearningOrchestrator 시작
   ↓
2. 6개 Agent 병렬 학습
   - NewsAgentLearning
   - TraderAgentLearning
   - RiskAgentLearning
   - MacroAgentLearning
   - InstitutionalAgentLearning
   - AnalystAgentLearning
   ↓
3. Hallucination Prevention (3-gate)
   - Statistical Validators (p-value < 0.05)
   - Walk-Forward Validator (out-of-sample)
   - Cross-Agent Validation
   ↓
4. 학습 결과 DB 저장
   ↓
5. AgentWeightManager
   - 30일 성과 분석
   - Accuracy 기반 가중치 조정
   - Confidence gap 보정
   ↓
6. 완료 (다음 날 00:00 UTC 대기)
```

---

### 4. Hallucination Prevention (3-Gate)

**Gate 1: Statistical Validators**
```python
# p-value < 0.05 검증
if p_value >= 0.05:
    reject("통계적으로 유의하지 않음")
```

**Gate 2: Walk-Forward Validator**
```python
# Out-of-sample 검증
train_accuracy = 0.72  # In-sample
test_accuracy = 0.45   # Out-of-sample

if test_accuracy < 0.55:
    reject("과적합 (Overfitting)")
```

**Gate 3: Cross-Agent Validation**
```python
# 다른 Agent와 교차 검증
if agent_accuracy < avg_accuracy - 0.15:
    reject("다른 Agent 대비 저성과")
```

---

## API 엔드포인트

### War Room API

**POST `/api/war-room/vote`**
```bash
curl -X POST http://localhost:8000/api/war-room/vote \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "context": {}
  }'

# Response:
{
  "session_id": 125,
  "ticker": "AAPL",
  "consensus_action": "BUY",
  "consensus_confidence": 0.68,
  "agent_votes": [
    {"agent": "risk", "action": "HOLD", "confidence": 0.75},
    {"agent": "trader", "action": "BUY", "confidence": 0.82},
    {"agent": "analyst", "action": "BUY", "confidence": 0.78},
    ...
  ],
  "vote_scores": {
    "BUY": 0.4820,
    "SELL": 0.0640,
    "HOLD": 0.4540
  }
}
```

---

### Performance API

**GET `/api/performance/summary`**
```bash
curl http://localhost:8000/api/performance/summary

# Response:
{
  "total_predictions": 1250,
  "correct_predictions": 875,
  "accuracy": 70.0,
  "avg_return": 0.0452,
  "avg_performance_score": 0.68,
  "best_action": "BUY"
}
```

**GET `/api/performance/agents`**
```bash
curl http://localhost:8000/api/performance/agents

# Response:
[
  {
    "agent_name": "risk",
    "total_votes": 1250,
    "correct_votes": 900,
    "accuracy": 72.0,
    "avg_return": 0.0480
  },
  {
    "agent_name": "trader",
    "total_votes": 1250,
    "correct_votes": 825,
    "accuracy": 66.0,
    "avg_return": 0.0420
  },
  ...
]
```

**GET `/api/performance/by-action`**
```bash
curl http://localhost:8000/api/performance/by-action

# Response:
[
  {
    "action": "BUY",
    "total": 450,
    "correct": 315,
    "accuracy": 70.0,
    "avg_return": 0.0520
  },
  {
    "action": "SELL",
    "total": 300,
    "correct": 195,
    "accuracy": 65.0,
    "avg_return": 0.0380
  },
  ...
]
```

---

### Weight Adjustment API

**POST `/api/weights/adjust`**
```bash
curl -X POST http://localhost:8000/api/weights/adjust

# Response:
{
  "risk": {
    "weight": 1.2,
    "accuracy": 0.72,
    "confidence_gap": 0.035,
    "reason": "strong_performer"
  },
  "trader": {
    "weight": 1.0,
    "accuracy": 0.66,
    "confidence_gap": 0.012,
    "reason": "good_performer"
  },
  "analyst": {
    "weight": 0.8,
    "accuracy": 0.58,
    "confidence_gap": -0.021,
    "reason": "weak_performer"
  }
}
```

**GET `/api/weights/current`**
```bash
curl http://localhost:8000/api/weights/current

# Response:
{
  "risk": 1.2,
  "trader": 1.0,
  "analyst": 0.8,
  "chipwar": 1.0,
  "news": 0.9,
  "macro": 1.1,
  "institutional": 1.0,
  "sentiment": 0.7
}
```

---

## 데이터베이스 스키마

### 주요 테이블

**1. price_tracking** - War Room 투표 결과
```sql
CREATE TABLE price_tracking (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10),
    consensus_action VARCHAR(20),        -- BUY/SELL/HOLD/...
    consensus_confidence FLOAT,
    initial_price FLOAT,
    current_price FLOAT,
    return_pct FLOAT,
    is_correct BOOLEAN,
    performance_score FLOAT,
    status VARCHAR(20),                  -- PENDING/COMPLETED
    initial_timestamp TIMESTAMP,
    completion_timestamp TIMESTAMP
);
```

**2. agent_vote_tracking** - Agent별 투표 기록
```sql
CREATE TABLE agent_vote_tracking (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES price_tracking(id),
    agent_name VARCHAR(50),
    vote_action VARCHAR(20),
    vote_confidence FLOAT,
    is_correct BOOLEAN,
    evaluated_at TIMESTAMP
);
```

**3. news_articles** - 뉴스 기사
```sql
CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    source VARCHAR(100),
    url TEXT,
    published_at TIMESTAMP,
    collected_at TIMESTAMP
);
```

**4. news_analysis** - 뉴스 감성 분석
```sql
CREATE TABLE news_analysis (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES news_articles(id),
    sentiment_score FLOAT,              -- -1.0 ~ +1.0
    model_used VARCHAR(50),
    analyzed_at TIMESTAMP
);
```

**5. news_ticker_relevance** - 뉴스-티커 연관도
```sql
CREATE TABLE news_ticker_relevance (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES news_articles(id),
    ticker VARCHAR(10),
    relevance_score FLOAT,              -- 0.0 ~ 1.0
    created_at TIMESTAMP
);
```

**6. chip_intelligence** - ChipWar Agent 학습 데이터
```sql
CREATE TABLE chip_intelligence (
    id SERIAL PRIMARY KEY,
    scenario_name VARCHAR(100),
    probability FLOAT,
    avg_return FLOAT,
    confidence FLOAT,
    created_at TIMESTAMP
);
```

---

## 실행 방법

### 1. 환경 설정

**필수 패키지 설치**:
```bash
cd backend
pip install -r requirements.txt
```

**환경 변수 설정** (`.env`):
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_trading

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
FRED_API_KEY=your_fred_api_key_here

# KIS Broker (실거래)
KIS_APP_KEY=your_kis_app_key
KIS_APP_SECRET=your_kis_app_secret
KIS_ACCOUNT_NUMBER=your_account_number

# 모의투자
KIS_MOCK_MODE=true
```

---

### 2. 데이터베이스 마이그레이션

```bash
cd backend
alembic upgrade head
```

---

### 3. 서버 시작

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 로그 확인:
# ✅ Daily Learning Scheduler started (00:00 UTC)
# ⏰ Next learning cycle scheduled for: 2025-12-29 00:00:00
```

---

### 4. War Room 투표 실행

```bash
# API 호출
curl -X POST http://localhost:8000/api/war-room/vote \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

# 또는 Python
import requests

response = requests.post(
    "http://localhost:8000/api/war-room/vote",
    json={"ticker": "AAPL"}
)

print(response.json())
```

---

## 테스트 방법

### 1. Agent 통합 테스트

```bash
cd backend

# 6 Agents (DB 미사용, 빠름)
python tests/integration/test_agents_simple.py

# 8 Agents (전체, DB 필요)
python tests/integration/test_all_agents.py

# 예상 출력:
# ================================================================================
# War Room All Agents Integration Test
# ================================================================================
# ✓ Risk Agent (20%)
# ✓ Trader Agent (15%)
# ✓ Analyst Agent (15%)
# ✓ ChipWar Agent (12%)
# ✓ News Agent (10%)
# ✓ Macro Agent (10%)
# ✓ Institutional Agent (10%)
# ✓ Sentiment Agent (8%)
#
# Final Decision: HOLD (Confidence: 0.4450)
# Test Summary: 8 passed, 0 failed
# ================================================================================
```

---

### 2. 데이터 수집 테스트

```bash
cd backend

# 5분 데이터 수집 파이프라인 테스트
python tests/integration/test_data_collection_5min.py

# 예상 출력:
# ================================================================================
# 5-MINUTE TEST COMPLETE
# ================================================================================
# Total Duration: 300.0s
# Total Cycles: 10
# Successful Cycles: 10
# Failed Cycles: 0
# Success Rate: 100.0%
# Total Tickers Collected: 30
# Avg Collection Time/Cycle: 2.54s
# ================================================================================
# ✓ TEST PASSED (100.0% success rate)
```

---

### 3. 자기학습 시스템 테스트

```bash
cd backend

# Daily Learning Scheduler (단일 사이클)
python -m ai.learning.daily_learning_scheduler

# Agent Weight Manager
python -m ai.learning.agent_weight_manager

# 예상 출력:
# ================================================================================
# 🔄 Calculating Agent Weights
# ================================================================================
# 📊 Weight Summary:
# risk            | Weight: 1.20 | Accuracy:  72.0% | Votes: 125 | Gap:  +3.5%
# trader          | Weight: 1.00 | Accuracy:  65.0% | Votes: 125 | Gap:  +1.2%
# analyst         | Weight: 0.80 | Accuracy:  58.0% | Votes: 125 | Gap:  -2.1%
# ================================================================================
```

---

### 4. Performance API 테스트

```bash
# 서버 시작
uvicorn main:app --reload

# 전체 성과 요약
curl http://localhost:8000/api/performance/summary | jq

# Agent별 성과
curl http://localhost:8000/api/performance/agents | jq

# 액션별 성과
curl http://localhost:8000/api/performance/by-action | jq

# 일별 추이 (최근 30일)
curl "http://localhost:8000/api/performance/history?days=30" | jq

# 최고 성과 세션 (Top 10)
curl "http://localhost:8000/api/performance/top-sessions?limit=10&sort=best" | jq

# Agent × Action 성과
curl http://localhost:8000/api/performance/agents/by-action | jq
```

---

## 환경 설정

### 필수 API Keys

1. **Gemini API** (뉴스 감성 분석)
   - https://makersuite.google.com/app/apikey
   - `.env`에 `GEMINI_API_KEY` 설정

2. **FRED API** (거시경제 데이터)
   - https://fred.stlouisfed.org/docs/api/api_key.html
   - `.env`에 `FRED_API_KEY` 설정

3. **KIS API** (실거래, 선택)
   - https://apiportal.koreainvestment.com/
   - `.env`에 `KIS_APP_KEY`, `KIS_APP_SECRET` 설정

---

### 권장 시스템 요구사항

- **OS**: Ubuntu 20.04 LTS 이상 / Windows 10 이상
- **Python**: 3.10 이상
- **메모리**: 8GB 이상 (16GB 권장)
- **디스크**: 50GB 이상 (데이터 축적용)
- **PostgreSQL**: 14 이상

---

### Docker 실행 (선택)

```bash
# Docker Compose로 전체 시스템 실행
docker-compose up -d

# 포함된 서비스:
# - FastAPI (backend)
# - PostgreSQL (database)
# - Prometheus (metrics)
# - Grafana (visualization)
```

---

## 다음 단계

### 1. Option 1: 14일 데이터 수집 🚀
- **목적**: Agent 자기학습 데이터 축적
- **티커**: AAPL, NVDA, MSFT
- **기간**: 14일 × 24시간 = 336시간
- **데이터 포인트**: 1,008개 (3 티커 × 336시간)

### 2. Option 2: 실거래 환경 준비
- KIS Broker 연동
- 모의투자 검증
- 소액 실거래 ($1,000 ~ $5,000)

### 3. 성과 분석 및 최적화
- Agent별 accuracy 분석
- 저성과 Agent 개선
- 가중치 최적화

---

## 문의 및 기여

**프로젝트 GitHub**: (추가 예정)
**이슈 트래커**: (추가 예정)
**문서**: `docs/` 폴더 참조

---

**작성일**: 2025-12-28
**버전**: v1.0 (Production Ready)
**라이선스**: MIT (예정)
