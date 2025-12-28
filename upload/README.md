# AI Trading System - Claude Project 첨부 파일

**생성일**: 2025-12-28
**목적**: Claude Project에 첨부할 핵심 파일 모음

---

## 📁 포함된 파일

### 📚 핵심 문서 (4개)

#### 1. PROJECT_OVERVIEW.md (38KB) ⭐ **최우선 읽기**
**프로젝트 전체 종합 문서**

- 프로젝트 소개 및 핵심 특징
- 시스템 아키텍처 (전체 흐름도)
- **8개 War Room Agent 상세 소개** (각 Agent별 역할, 로직, 예시)
- 폴더 구조 및 파일 설명 (40개+ 주요 파일)
- 핵심 기능 (Weighted Voting, 7 Actions, 자기학습)
- API 엔드포인트 (10개+ API 예시)
- 데이터베이스 스키마
- 실행 방법 및 테스트 방법

**크기**: 1,200 lines

---

#### 2. 251228_War_Room_Complete.md (20KB) ⭐ **War Room 완료 보고서**
**Spec Kit 공식 문서**

- Executive Summary
- 8개 Agent 구성 및 역할 (상세)
- 7개 Action System
- 투표 프로세스 및 계산 로직
- 완료된 버그 수정 (6개)
- 테스트 결과 (100% 성공)
- Option 3 완료 (자기학습, 성과 대시보드)

**상태**: ✅ Production Ready

---

#### 3. 251228_Development_Status_and_Roadmap.md (31KB)
**개발 현황 및 로드맵**

- 완료된 작업 (Phase 1-4)
- 시스템 아키텍처
- 향후 개발 계획 (우선순위 1-4)
- 참고 문서

---

#### 4. 00_Spec_Kit_README.md (10KB)
**Spec Kit 인덱스**

- 문서 목록 및 설명
- Quick Navigation
- Documentation Changelog

---

### 🤖 War Room Agents (8개)

**폴더**: `agents/`

1. **risk_agent.py** - Risk Agent (20%)
   - VaR 계산, 포지션 크기, 손절매

2. **trader_agent.py** - Trader Agent (15%)
   - 기술적 분석, RSI, MACD, 이동평균

3. **analyst_agent.py** - Analyst Agent (15%)
   - 펀더멘털, P/E Ratio, 실적 분석

4. **chip_war_agent.py** - ChipWar Agent (12%)
   - 반도체 지정학, ChipWarSimulator V2

5. **news_agent.py** - News Agent (10%)
   - 뉴스 감성 분석, Gemini 2.5 Flash

6. **macro_agent.py** - Macro Agent (10%)
   - 거시경제, Fed 금리, CPI, 유가, 달러

7. **institutional_agent.py** - Institutional Agent (10%)
   - 기관 투자자, 13F, 내부자 거래

8. **sentiment_agent.py** - Sentiment Agent (8%)
   - 소셜 감성, Fear & Greed Index

---

### ⚙️ War Room System (3개)

**폴더**: `war_room/`

1. **war_room_router.py** - War Room API
   - 투표 프로세스
   - Weighted voting 로직
   - Action mapping (7 → 3)

2. **war_room_executor.py** - Order Execution
   - Position sizing
   - HOLD/MAINTAIN skip 로직
   - REDUCE/INCREASE/DCA (50% size)

3. **base_schema.py** - SignalAction Enum
   - 7개 Action 정의
   - Pydantic schemas

---

### 🧪 테스트 (1개)

**test_all_agents.py** - 8 Agent 통합 테스트
- 100% 성공률
- Standalone test runner

---

## 📊 파일 요약

| 카테고리 | 파일 수 | 용량 |
|---------|--------|------|
| 핵심 문서 | 4개 | ~99KB |
| War Room Agents | 8개 | ~60KB |
| War Room System | 3개 | ~30KB |
| 테스트 | 1개 | ~10KB |
| **총합** | **16개** | **~199KB** |

---

## 🚀 Claude Project 업로드 순서

### 1단계: 필수 문서 (4개) - 먼저 업로드
1. ✅ PROJECT_OVERVIEW.md
2. ✅ 251228_War_Room_Complete.md
3. ✅ 251228_Development_Status_and_Roadmap.md
4. ✅ 00_Spec_Kit_README.md

**이 4개 파일만 읽어도 프로젝트 전체를 이해 가능!**

---

### 2단계: Agent 코드 (8개) - 용량 여유 있으면 추가
`agents/` 폴더 전체 업로드

---

### 3단계: War Room System (3개) - 필요시 추가
`war_room/` 폴더 전체 업로드

---

### 4단계: 테스트 (1개) - 선택
`test_all_agents.py`

---

## 💡 사용 방법

### Claude Project에 물어볼 질문 예시

**시스템 이해**:
- "War Room 투표 시스템이 어떻게 작동하나요?"
- "8개 Agent가 각각 어떤 역할을 하나요?"
- "7개 Action이 어떻게 BUY/SELL/HOLD로 매핑되나요?"

**코드 관련**:
- "Risk Agent의 VaR 계산 로직을 설명해주세요"
- "ChipWar Agent는 어떤 시나리오를 시뮬레이션하나요?"
- "자기학습 시스템은 어떻게 구현되어 있나요?"

**개발 계획**:
- "다음 단계로 무엇을 개발해야 하나요?"
- "14일 데이터 수집은 어떻게 진행하나요?"
- "실거래 환경 준비에 필요한 작업은?"

---

## 📝 주의사항

1. **문서 우선 읽기**: PROJECT_OVERVIEW.md를 먼저 읽고 전체 구조 파악
2. **Agent 코드**: 각 Agent는 독립적으로 작동하며 공통 인터페이스 사용
3. **War Room System**: 투표 → 집계 → 실행 순서로 진행
4. **테스트**: 100% 성공한 통합 테스트 코드 참고 가능

---

## 🔗 원본 파일 위치

이 파일들은 `d:\code\ai-trading-system` 프로젝트의 복사본입니다.

**원본 경로**:
- 문서: `docs/`
- Agent: `backend/ai/debate/`
- War Room: `backend/api/`, `backend/trading/`, `backend/schemas/`
- 테스트: `backend/tests/integration/`

---

**작성일**: 2025-12-28
**버전**: War Room System v1.0 (Production Ready)
