# Phase 3 완료 보고서 (Report Orchestrator Agent)

**작성일**: 2025-12-29
**Phase**: Phase 3 (Week 5-6) - Report Orchestrator Agent
**Status**: ✅ 완료

---

## 📋 목표

Report Orchestrator Agent 구현으로 AI 판단의 정확도 측정 및 리포트 accountability 섹션 생성

---

## ✅ 완료된 작업

### 1. Report Orchestrator Agent SKILL.md 작성

**위치**: `backend/ai/skills/reporting/report-orchestrator-agent/SKILL.md`

**내용**:
- **Role**: "AI 판단의 정확도를 측정하고, 리포트에 accountability 섹션을 생성하는 전문 Agent"
- **Core Capabilities**:
  - NIA (News Interpretation Accuracy) 계산
  - Timeframe별 NIA (Daily/Weekly/Annual)
  - 리포트 섹션 생성
- **Core Functions**: 4개 함수 상세 스펙
  - `calculate_news_interpretation_accuracy(timeframe)`
  - `generate_weekly_accountability_section()`
  - `generate_annual_accountability_report()`
  - `enhance_daily_report_with_accountability(report_data)`
- **Decision Framework**: 해석 정확도 판정 로직
- **Integration Points**: Price Tracking Scheduler 연동 방법
- **Output Examples**: Daily/Weekly/Annual 리포트 예시
- **Guidelines**: Do's & Don'ts

**핵심 로직**:
```
NIA = (정확한 해석 수) / (검증된 전체 해석 수) × 100

정확한 해석:
- BULLISH → actual price change > 1%
- BEARISH → actual price change < -1%
- NEUTRAL → -1% ≤ actual change ≤ 1%

Time Horizon별 검증:
- IMMEDIATE: 1시간 후 가격
- INTRADAY: 1일 후 가격
- MULTI_DAY: 3일 후 가격
```

---

### 2. Report Orchestrator 구현

**파일**: `backend/ai/skills/reporting/report-orchestrator-agent/report_orchestrator.py` (424 lines)

#### 2.1 ReportOrchestrator 클래스

**초기화**:
```python
def __init__(self, db: Session):
    self.interpretation_repo = NewsInterpretationRepository(db)
    self.reaction_repo = NewsMarketReactionRepository(db)
    self.link_repo = NewsDecisionLinkRepository(db)
    self.narrative_repo = NewsNarrativeRepository(db)
    self.failure_repo = FailureAnalysisRepository(db)
    self.db = db
```

#### 2.2 Core Functions

**`calculate_news_interpretation_accuracy(timeframe="daily")`** (lines 40-105)
- Date range 결정 (daily/weekly/annual)
- 검증된 해석 조회 (verified_at NOT NULL)
- Overall accuracy 계산
- By impact 분석 (HIGH/MEDIUM/LOW)
- By type 분석 (EARNINGS/MACRO/GEOPOLITICS)
- Best/Worst call 추출

**Returns**:
```python
{
    "overall_accuracy": 0.75,
    "by_impact": {"HIGH": 0.85, "MEDIUM": 0.72, "LOW": 0.68},
    "by_type": {"EARNINGS": 0.85, "MACRO": 0.72, "GEOPOLITICS": 0.45},
    "best_call": {...},
    "worst_call": {...},
    "total_verified": 25
}
```

**`generate_weekly_accountability_section()`** (lines 107-159)
- 이번 주 NIA 계산
- 지난 주 NIA와 비교 → improvement
- Best/worst judgment 포맷팅
- Lesson learned 추출

**Returns**:
```python
{
    "nia_score": 75,
    "improvement": "+5%p",
    "best_judgment": "NVDA 실적 발표 → 상승 예측 → 실제 +8% (정확도: 100%)",
    "worst_judgment": "Fed 발언 → 하락 예측 → 실제 +2% (정확도: 0%)",
    "lesson_learned": "숏커버 가능성을 고려 못함. 다음 주부터 단기 포지션 청산 패턴 모니터링 강화"
}
```

**`generate_annual_accountability_report()`** (lines 161-221)
- 연간 NIA 계산
- By type 백분율 변환
- Top 3 failures 조회 (severity 기준)
- System improvements 추적 (fix_applied & fix_effective)

**Returns**:
```python
{
    "nia_overall": 68,
    "by_type": {"EARNINGS": 85, "MACRO": 72, "GEOPOLITICS": 45},
    "top_3_failures": [
        {
            "description": "Ukraine 전쟁 초기 → 과도한 비관",
            "lesson": "지정학적 리스크는 priced-in 빠름",
            "fix": "macro_context에 geopolitical_risk_decay_rate 추가"
        },
        ...
    ],
    "system_improvements": [...]
}
```

**`enhance_daily_report_with_accountability(report_data)`** (lines 223-244)
- 오늘 NIA 계산
- Narratives에 정확도 추가
- Accountability 섹션 삽입

#### 2.3 Helper Methods (lines 246-424)

- `_get_date_range(timeframe)` - 날짜 범위 결정
- `_calculate_by_impact(verified_data)` - Impact별 정확도
- `_calculate_by_type(verified_data)` - Type별 정확도 (reasoning 키워드 기반)
- `_find_best_call(verified_data)` - 정확하면서 가장 큰 움직임
- `_find_worst_call(verified_data)` - 틀리면서 가장 높은 confidence
- `_format_call(item)` - Call 요약 포맷팅
- `_format_judgment(call)` - 사람이 읽기 쉬운 판단 문자열
- `_extract_lesson(call)` - 실패에서 교훈 추출
- `_severity_score(severity)` - 심각도 점수화
- `_check_interpretation_accuracy(bias, change)` - 해석 정확도 판정

**구문 검증**: ✅ `python -m py_compile` 통과

---

### 3. Price Tracking Verifier 구현

**파일**: `backend/automation/price_tracking_verifier.py` (275 lines)

#### 3.1 PriceTrackingVerifier 클래스

**역할**:
1. 1h/1d/3d 전에 생성된 해석 중 검증 대기 중인 것 조회
2. 현재 가격 조회 (KIS API - TODO)
3. 가격 변화율 계산
4. AI 해석 정확도 판정
5. DB 업데이트 (price_*_after, actual_price_change_*, interpretation_correct, etc.)

#### 3.2 Main Methods

**`verify_interpretations(time_horizon="1h")`** (lines 46-137)
- Pending verifications 조회
- 각 reaction별:
  - 현재 가격 조회 (Mock for now, KIS API 필요)
  - 가격 변화율 계산
  - Correctness 판정
  - Confidence justification 체크
  - Magnitude accuracy 계산
  - DB 업데이트

**Returns**:
```python
{
    "verified_count": 5,
    "correct_count": 4,
    "accuracy": 0.8
}
```

**`verify_all_horizons()`** (lines 139-157)
- 1h, 1d, 3d 모두 검증
- 각 horizon별 결과 반환

#### 3.3 Helper Methods

**`_get_current_price(ticker)`** (lines 161-177)
- TODO: KIS API 연동
- 현재는 Mock 가격 반환

**`_check_correctness(bias, change)`** (lines 179-195)
- BULLISH: change > 1.0%
- BEARISH: change < -1.0%
- NEUTRAL: -1.0% ≤ change ≤ 1.0%

**`_check_confidence_justified(confidence, impact, magnitude)`** (lines 197-224)
- High confidence (80+): HIGH → 5%+, else → 2%+
- Medium confidence (50-79): 2%+
- Low confidence (<50): always justified

**`_calculate_magnitude_accuracy(impact, magnitude)`** (lines 226-264)
- HIGH: 5%+ → 1.0, 2%+ → 0.5, else → 0.0
- MEDIUM: 2-5% → 1.0, 1%+ → 0.7, else → 0.3
- LOW: <2% → 1.0, <5% → 0.5, else → 0.0

**구문 검증**: ✅ `python -m py_compile` 통과

---

### 4. Scheduler 업데이트

**파일**: `backend/automation/scheduler.py`

**변경사항**:
- Import 추가: `PriceTrackingVerifier` (line 24)
- `__init__()` 수정: `self.price_verifier = PriceTrackingVerifier()` (line 38)
- `setup_schedules()` 수정:
  - Price Tracking 검증 스케줄 활성화 (line 58)
  - `schedule.every().hour.do(self.run_price_tracking_verification)`
- `run_price_tracking_verification()` 구현 (lines 92-114):
  - Async verification 실행
  - 모든 horizons (1h/1d/3d) 검증
  - 결과 로깅

**스케줄 현황**:
- ✅ Macro Context Update: 매일 09:00 KST
- ✅ Price Tracking Verification: 1시간마다
- ⏳ Daily Report Generation: Phase 4
- ⏳ Weekly Report Generation: Phase 4

**구문 검증**: ✅ `python -m py_compile` 통과

---

### 5. Module 초기화 파일

**`backend/ai/skills/reporting/report-orchestrator-agent/__init__.py`**
- ReportOrchestrator export

**`backend/automation/__init__.py`**
- PriceTrackingVerifier export 추가

---

### 6. Unit Tests 작성

**파일**: `tests/test_nia_calculation.py` (229 lines)

#### 6.1 Test Functions

**`test_check_interpretation_accuracy()`**
- 13개 테스트 케이스
- BULLISH/BEARISH/NEUTRAL 모든 시나리오
- ✅ 13/13 passed

**`test_magnitude_accuracy()`**
- 9개 테스트 케이스
- HIGH/MEDIUM/LOW impact 모든 시나리오
- ✅ 9/9 passed

**`test_confidence_justification()`**
- 8개 테스트 케이스
- High/Medium/Low confidence 시나리오
- ✅ 8/8 passed

**실행 결과**:
```bash
✅ ALL TESTS PASSED
📊 Total: 30 tests, 30 passed, 0 failed
```

---

## 📊 통계

### 코드 변경
- **SKILL.md**: 428 lines (신규 생성)
- **report_orchestrator.py**: 424 lines (신규 생성)
- **price_tracking_verifier.py**: 275 lines (신규 생성)
- **scheduler.py**: +24 lines (수정)
- **__init__.py**: 2개 파일 수정
- **test_nia_calculation.py**: 229 lines (신규 생성)

**총 추가 코드**: ~1,380 lines

### 구현된 기능
- **Report Orchestrator**: 4개 core functions + 10개 helper methods
- **Price Tracking Verifier**: 2개 main methods + 4개 helper methods
- **Unit Tests**: 3개 test functions, 30개 test cases

---

## 🧪 검증 결과

### Python 구문 검증
```bash
✅ report_orchestrator.py: No syntax errors
✅ price_tracking_verifier.py: No syntax errors
✅ scheduler.py: No syntax errors
```

### Unit Tests
```bash
✅ test_check_interpretation_accuracy: 13/13 passed
✅ test_magnitude_accuracy: 9/9 passed
✅ test_confidence_justification: 8/8 passed

✅ OVERALL: 30/30 passed (100%)
```

---

## 🔄 Accountability Chain (완성)

```
1. 뉴스 발생 (NewsArticle)
   ↓
2. News Agent 해석 (NewsInterpretation) + Macro Context 참조 ✅ Phase 2
   ↓
3. War Room 의사결정 (AIDebateSession) ✅ 기존
   ↓
4. Decision Link 생성 (NewsDecisionLink) ✅ Phase 1
   ↓
5. 시장 반응 검증 (NewsMarketReaction) - 1h/1d/3d 후 ✅ Phase 3
   ↓ (Price Tracking Verifier - 매시간 실행)
6. 리포트 서술 (NewsNarrative) ✅ Phase 1
   ↓
7. NIA 계산 & 정확도 계산 ✅ Phase 3
   ↓ (Report Orchestrator)
8. 실패 분석 (FailureAnalysis) ⏳ Phase 4
```

---

## ⏭️ 다음 단계 (Phase 4: Week 7-8)

### Task 4.1: Failure Learning Agent 구현
- **파일**: `backend/ai/skills/reporting/failure-learning-agent/failure_analyzer.py`
- **기능**:
  - 틀린 판단 자동 분석 (interpretation_correct = False)
  - Root cause 추론 (Claude API)
  - Lesson learned 생성
  - Recommended fix 제안
  - failure_analysis 테이블에 저장

### Task 4.2: Daily Report Integration
- **파일**: `backend/services/complete_5page_report_generator.py` (수정)
- **추가 기능**:
  - Report Orchestrator 호출
  - `enhance_daily_report_with_accountability()` 적용
  - 각 뉴스 해석에 정확도 표시

### Task 4.3: Weekly/Annual Report Integration
- **파일**: 새 파일 생성 (weekly/annual report generators)
- **추가 기능**:
  - `generate_weekly_accountability_section()` 호출
  - `generate_annual_accountability_report()` 호출
  - PDF 생성 (reportlab)

---

## 📝 Notes

### 핵심 원칙 준수
- ✅ **Repository Pattern**: 모든 DB 접근은 Repository 통해 진행
- ✅ **Async 처리**: Price Tracking Verifier는 async/await 사용
- ✅ **Feature Flag**: News Agent의 interpretation 기능은 환경변수로 on/off 가능
- ✅ **Mock Data**: KIS API 미연동 시 Mock 가격 사용 (TODO 명시)
- ✅ **Error Handling**: 모든 주요 함수에 try-except 적용

### 리스크 & 대응
- **KIS API 미연동**: Price Tracking Verifier가 Mock 가격 사용 중
  - **대응**: Phase 4에서 KIS API 연동 필요 (`_get_current_price()` 수정)
- **News Type 추론**: 현재 reasoning 키워드 기반으로 EARNINGS/MACRO/GEOPOLITICS 분류
  - **대응**: Phase 4에서 news_interpretations 테이블에 news_type 컬럼 추가 고려
- **시간대 처리**: 현재 로컬 시간 사용, KST 명시적 처리 필요
  - **대응**: Phase 4에서 timezone aware datetime 사용

### 개선 가능 사항
- **Caching**: NIA 계산 결과를 캐싱하여 성능 향상 (Redis)
- **Notification**: NIA가 60% 미만 시 Telegram 알림 (SKILL.md에 명시)
- **Visualization**: NIA 추이 그래프 생성 (matplotlib)
- **A/B Testing**: 다른 정확도 threshold 테스트 (현재 1%)

---

**Phase 3 완료일**: 2025-12-29 23:45 (약 1.5시간 소요)
**Phase 4 시작 예정**: 사용자 승인 후

---

## 🎯 성공 기준 달성

- ✅ Report Orchestrator Agent SKILL.md 작성 완료 (428 lines)
- ✅ ReportOrchestrator 클래스 구현 완료 (4 core functions, 10 helpers)
- ✅ PriceTrackingVerifier 구현 완료 (2 main methods, 4 helpers)
- ✅ Scheduler 통합 완료 (1시간마다 검증)
- ✅ Unit Tests 작성 및 통과 (30/30 passed)
- ✅ Python 구문 오류 0건
- ✅ SKILL.md 예시 출력 포맷 정의

**Status**: ✅ **Phase 3 Complete - Ready for Phase 4**
