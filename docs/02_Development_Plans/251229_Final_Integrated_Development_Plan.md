# 최종 통합 개발 계획 (Final Integrated Development Plan)

**작성일**: 2025-12-29
**목적**: Report 고급화 + 발견된 Agent 인프라 통합 로드맵

---

## 📋 Executive Summary

### 오늘 검토 결과

**원래 목표**:
- Report 정확도 상승 ("AI가 말한 대로 시장이 움직였는가?")
- Daily/Weekly/Annual 리포트에 책임 추적(Accountability) 기능 추가

**검토 중 발견된 필요사항**:
- News Agent 강화 (뉴스 해석 기능 추가)
- Report Orchestrator Agent (NIA 계산 + 책임 섹션 생성)
- Failure Learning Agent (틀린 판단 학습)
- 6개 신규 DB 테이블 (accountability chain 저장)

**핵심 통찰**:
- 두 가지 모두 필요하며 상호 보완적
- Report 고급화를 위해서는 Agent 인프라가 필수
- Agent 인프라는 Report에 데이터를 제공하는 구조

---

## 🎯 Two-Track Approach

### Track 1: Report Enhancement (리포트 고급화)
**최종 목표**: AI 판단 책임 추적이 담긴 고급 리포트

**현재 상태**:
- ✅ Daily Report (5 pages, Korean) 완성
- ✅ PDF 생성 시스템 완성 (Korean fonts 지원)
- ✅ Language Templates (63개 동적 문장 패턴)
- ❌ Mock 데이터 사용 중 (실제 데이터 연동 필요)

**목표 산출물**:

#### Daily Report 강화
```
기존: "Fed 매파 발언으로 시장 하락"

신규: "Fed 매파 발언(Bloomberg, 신뢰도 95%)에도 시장은 상승했으나,
      AI는 이를 '숏커버'로 판단하여 추가 매수를 보류했고,
      실제로 30분 후 반등은 소멸되었습니다. (해석 정확도: 92%)"
```

#### Weekly Report 강화
```
┌──────────────────────────────────────────┐
│ 📊 이번 주 AI 판단 진화 로그             │
├──────────────────────────────────────────┤
│ News Interpretation Accuracy: 75%        │
│ (전주 대비 +5%p)                         │
│                                          │
│ ✅ 가장 정확했던 판단:                   │
│    NVDA 실적 발표 → 상승 예측 → 실제 +8%│
│                                          │
│ ❌ 가장 틀렸던 판단:                     │
│    Fed 발언 → 하락 예측 → 실제 +2%      │
│    교훈: 숏커버 가능성을 고려 못함       │
└──────────────────────────────────────────┘
```

#### Annual Report 강화
```
📊 AI Accountability Report (전체 연간)

┌─────────────────────────────────────────┐
│ News Interpretation Accuracy (NIA)      │
│ Overall: 68/100                         │
├─────────────────────────────────────────┤
│ 유형별:                                 │
│   • Earnings News: 85% ✅               │
│   • Macro News: 72%                     │
│   • Geopolitics: 45% ❌ (개선 필요)     │
└─────────────────────────────────────────┘

가장 틀렸던 판단 Top 3:
1. Ukraine 전쟁 초기 → 과도한 비관
   교훈: 지정학적 리스크는 priced-in 빠름
   개선: macro_context에 geopolitical_risk_decay_rate 추가

2. Fed pivot 예측 → 6개월 일찍 판단
   교훈: 중앙은행 발언은 literal하게 해석
   개선: Fed tone tracker weight 증가

3. AI 칩 규제 → 과소평가
   교훈: 정부 규제는 산업 게임 체인저
   개선: regulatory_risk agent 신설 (2026 Q2)
```

---

### Track 2: Agent Infrastructure (Agent 인프라)

**목적**: Track 1을 가능하게 하는 데이터 생성 + 계산

**필요 Agent**:

#### 1. Enhanced News Agent (최우선)
- **위치**: `backend/ai/debate/news_agent.py` (기존 파일 수정)
- **역할**: War Room 실행 중 뉴스 해석 생성
- **추가 기능**:
  - Macro context 조회
  - Claude API로 뉴스 해석
  - `news_interpretations` 테이블에 저장
- **실행 시점**: War Room 토론 중 (매 트레이딩 신호 전)

#### 2. Report Orchestrator Agent (중우선)
- **위치**: `backend/ai/skills/reporting/report-orchestrator-agent/`
- **역할**: NIA 계산 + 책임 섹션 생성
- **핵심 기능**:
  ```python
  calculate_news_interpretation_accuracy(timeframe="daily|weekly|annual")
  generate_weekly_accountability_section()
  generate_annual_accountability_report()
  enhance_daily_report_with_accountability(data)
  ```
- **실행 시점**: 리포트 생성 직전 (Daily 16:30, Weekly 금요일 17:00)

#### 3. Failure Learning Agent (차우선)
- **위치**: `backend/ai/skills/system/failure-learning-agent/`
- **역할**: 틀린 판단 실시간 분석 + 시스템 조정
- **핵심 기능**:
  ```python
  analyze_failure(interpretation_id, actual_outcome)
  update_rag_context(lesson_learned)
  adjust_system_weights(failed_agent)
  ```
- **실행 시점**: `price_tracking_scheduler`에서 실제 결과 확인 후

---

## 🗄️ Database Foundation (모든 것의 전제조건)

### 신규 테이블 6개 (db-schema-manager 규칙 준수)

#### 1. news_interpretations
```json
{
  "table_name": "news_interpretations",
  "description": "AI의 뉴스 해석 저장",
  "columns": [
    {"name": "id", "type": "INTEGER", "primary_key": true},
    {"name": "news_article_id", "type": "INTEGER", "foreign_key": "news_articles.id"},
    {"name": "ticker", "type": "VARCHAR(20)"},
    {"name": "headline_bias", "type": "VARCHAR(20)", "enum": ["BULLISH", "BEARISH", "NEUTRAL"]},
    {"name": "expected_impact", "type": "VARCHAR(20)", "enum": ["HIGH", "MEDIUM", "LOW"]},
    {"name": "time_horizon", "type": "VARCHAR(20)", "enum": ["IMMEDIATE", "INTRADAY", "MULTI_DAY"]},
    {"name": "confidence", "type": "FLOAT"},
    {"name": "reasoning", "type": "TEXT"},
    {"name": "macro_context_id", "type": "INTEGER", "foreign_key": "macro_context_snapshots.id"},
    {"name": "interpreted_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
  ]
}
```

#### 2. news_market_reactions
```json
{
  "table_name": "news_market_reactions",
  "description": "뉴스 후 실제 시장 반응 검증",
  "columns": [
    {"name": "id", "type": "INTEGER", "primary_key": true},
    {"name": "interpretation_id", "type": "INTEGER", "foreign_key": "news_interpretations.id"},
    {"name": "actual_price_change_1h", "type": "FLOAT"},
    {"name": "actual_price_change_1d", "type": "FLOAT"},
    {"name": "actual_price_change_3d", "type": "FLOAT"},
    {"name": "interpretation_correct", "type": "BOOLEAN"},
    {"name": "confidence_justified", "type": "BOOLEAN"},
    {"name": "verified_at", "type": "TIMESTAMP"}
  ]
}
```

#### 3. news_decision_links
```json
{
  "table_name": "news_decision_links",
  "description": "뉴스 → 의사결정 → 결과 연결",
  "columns": [
    {"name": "id", "type": "INTEGER", "primary_key": true},
    {"name": "interpretation_id", "type": "INTEGER", "foreign_key": "news_interpretations.id"},
    {"name": "debate_session_id", "type": "INTEGER", "foreign_key": "ai_debate_sessions.id"},
    {"name": "trading_signal_id", "type": "INTEGER", "foreign_key": "trading_signals.id"},
    {"name": "final_decision", "type": "VARCHAR(10)", "enum": ["BUY", "SELL", "HOLD"]},
    {"name": "decision_outcome", "type": "VARCHAR(20)", "enum": ["SUCCESS", "FAILURE", "PENDING"]},
    {"name": "created_at", "type": "TIMESTAMP"}
  ]
}
```

#### 4. news_narratives
```json
{
  "table_name": "news_narratives",
  "description": "리포트에 사용된 문장 추적",
  "columns": [
    {"name": "id", "type": "INTEGER", "primary_key": true},
    {"name": "report_date", "type": "DATE"},
    {"name": "report_type", "type": "VARCHAR(20)", "enum": ["DAILY", "WEEKLY", "ANNUAL"]},
    {"name": "page_number", "type": "INTEGER"},
    {"name": "section", "type": "VARCHAR(50)"},
    {"name": "narrative_text", "type": "TEXT"},
    {"name": "interpretation_id", "type": "INTEGER", "foreign_key": "news_interpretations.id"},
    {"name": "accuracy_score", "type": "FLOAT", "nullable": true},
    {"name": "created_at", "type": "TIMESTAMP"}
  ]
}
```

#### 5. macro_context_snapshots
```json
{
  "table_name": "macro_context_snapshots",
  "description": "거시 경제 상황 스냅샷 (일일)",
  "columns": [
    {"name": "id", "type": "INTEGER", "primary_key": true},
    {"name": "snapshot_date", "type": "DATE", "unique": true},
    {"name": "regime", "type": "VARCHAR(30)", "enum": ["RISK_ON", "RISK_OFF", "ROTATION", "UNCERTAINTY"]},
    {"name": "fed_stance", "type": "VARCHAR(20)", "enum": ["HAWKISH", "DOVISH", "NEUTRAL"]},
    {"name": "vix_level", "type": "FLOAT"},
    {"name": "sector_rotation", "type": "VARCHAR(50)"},
    {"name": "dominant_narrative", "type": "TEXT"},
    {"name": "geopolitical_risk", "type": "VARCHAR(20)", "enum": ["HIGH", "MEDIUM", "LOW"]},
    {"name": "created_at", "type": "TIMESTAMP"}
  ]
}
```

#### 6. failure_analysis
```json
{
  "table_name": "failure_analysis",
  "description": "실패 분석 및 학습 저장소",
  "columns": [
    {"name": "id", "type": "INTEGER", "primary_key": true},
    {"name": "interpretation_id", "type": "INTEGER", "foreign_key": "news_interpretations.id"},
    {"name": "failure_type", "type": "VARCHAR(50)", "enum": ["WRONG_DIRECTION", "WRONG_MAGNITUDE", "WRONG_TIMING"]},
    {"name": "root_cause", "type": "TEXT"},
    {"name": "lesson_learned", "type": "TEXT"},
    {"name": "recommended_fix", "type": "TEXT"},
    {"name": "fix_applied", "type": "BOOLEAN", "default": false},
    {"name": "fix_effective", "type": "BOOLEAN", "nullable": true},
    {"name": "analyzed_at", "type": "TIMESTAMP"}
  ]
}
```

---

## 📅 8-Week Phased Roadmap

### Week 1-2: Database Foundation ✅
**목표**: 6개 테이블 + Repository 완성

**Task 1.1**: JSON 스키마 작성 (위 6개 테이블)
- 위치: `backend/ai/skills/system/db-schema-manager/schemas/`
- 파일:
  - `news_interpretations.json`
  - `news_market_reactions.json`
  - `news_decision_links.json`
  - `news_narratives.json`
  - `macro_context_snapshots.json`
  - `failure_analysis.json`

**Task 1.2**: 스키마 검증
```bash
cd backend/ai/skills/system/db-schema-manager
python scripts/validate_schema.py news_interpretations
python scripts/validate_schema.py news_market_reactions
python scripts/validate_schema.py news_decision_links
python scripts/validate_schema.py news_narratives
python scripts/validate_schema.py macro_context_snapshots
python scripts/validate_schema.py failure_analysis
```

**Task 1.3**: SQL 마이그레이션 생성
```bash
python scripts/generate_migration.py news_interpretations
# ... (각 테이블마다 실행)
```

**Task 1.4**: SQLAlchemy 모델 추가
- 파일: `backend/database/models.py`
- 6개 클래스 추가:
  ```python
  class NewsInterpretation(Base):
      __tablename__ = 'news_interpretations'
      # ...

  class NewsMarketReaction(Base):
      __tablename__ = 'news_market_reactions'
      # ...

  # ... (나머지 4개)
  ```

**Task 1.5**: Repository 클래스 추가
- 파일: `backend/database/repository.py`
- 6개 Repository 클래스:
  ```python
  class NewsInterpretationRepository(BaseRepository):
      def __init__(self, db: Session):
          super().__init__(db, NewsInterpretation)

      async def get_by_news_article(self, news_id: int):
          # ...

  # ... (나머지 5개)
  ```

**Task 1.6**: 마이그레이션 실행
```bash
cd backend
alembic upgrade head
```

**성공 기준**:
- ✅ 모든 스키마 검증 통과
- ✅ PostgreSQL에 6개 테이블 생성 완료
- ✅ Repository로 CRUD 테스트 성공

---

### Week 3-4: News Agent Enhancement 🔧
**목표**: War Room 실행 중 뉴스 해석 자동 생성

**Task 2.1**: Macro Context Updater 생성
- 파일: `backend/automation/macro_context_updater.py`
- 기능:
  ```python
  class MacroContextUpdater:
      async def update_daily_snapshot(self):
          """매일 09:00 KST 실행"""
          regime = await self._determine_regime()
          fed_stance = await self._analyze_fed_stance()
          vix = await self._get_vix_level()

          snapshot = {
              "snapshot_date": datetime.today().date(),
              "regime": regime,
              "fed_stance": fed_stance,
              "vix_level": vix,
              # ...
          }

          await macro_repo.create(snapshot)
  ```

**Task 2.2**: News Agent 수정
- 파일: `backend/ai/debate/news_agent.py`
- 새 메서드 추가:
  ```python
  class NewsAgent:
      async def _get_macro_context(self) -> Dict:
          """오늘 macro context 조회"""
          today = datetime.today().date()
          return await macro_repo.get_by_date(today)

      async def _interpret_news(
          self,
          news: NewsArticle,
          macro_context: Dict
      ) -> Dict:
          """Claude API로 뉴스 해석"""
          prompt = f"""
          Macro Context: {macro_context['regime']}, Fed: {macro_context['fed_stance']}

          News: {news.headline}
          Content: {news.content}

          Interpret this news:
          1. Headline Bias (BULLISH/BEARISH/NEUTRAL)
          2. Expected Impact (HIGH/MEDIUM/LOW)
          3. Time Horizon (IMMEDIATE/INTRADAY/MULTI_DAY)
          4. Confidence (0-1)
          5. Reasoning
          """

          response = await claude_api.messages.create(
              model="claude-sonnet-4-5",
              messages=[{"role": "user", "content": prompt}]
          )

          return parse_interpretation(response.content)

      async def _save_interpretation(
          self,
          news_id: int,
          interpretation: Dict
      ):
          """DB에 저장"""
          await interpretation_repo.create({
              "news_article_id": news_id,
              "headline_bias": interpretation["bias"],
              "expected_impact": interpretation["impact"],
              # ...
          })

      async def analyze(self, ticker: str, context: Dict) -> Dict:
          """기존 메서드 확장"""
          # [기존] Emergency + General News 수집
          emergency_news = await self._get_emergency_news(ticker)
          general_news = await self._get_general_news(ticker)

          # [신규] Macro context 조회
          macro_context = await self._get_macro_context()

          # [신규] 중요 뉴스 5개 해석
          important_news = self._select_important_news(
              emergency_news + general_news,
              limit=5
          )

          for news in important_news:
              interpretation = await self._interpret_news(news, macro_context)
              await self._save_interpretation(news.id, interpretation)

          # [기존] Vote 리턴
          return {
              "agent": "news",
              "action": self._determine_action(important_news),
              "confidence": 0.85,
              # ...
          }
  ```

**Task 2.3**: 스케줄러에 Macro Context Updater 추가
- 파일: `backend/automation/scheduler.py`
```python
schedule.every().day.at("09:00").do(macro_context_updater.update_daily_snapshot)
```

**성공 기준**:
- ✅ War Room 실행 시 `news_interpretations` 테이블에 자동 저장
- ✅ Macro context가 매일 09:00에 업데이트
- ✅ News Agent 기존 기능 정상 작동

---

### Week 5-6: Report Orchestrator Agent 📊
**목표**: NIA 계산 + 책임 섹션 생성

**Task 3.1**: SKILL.md 작성
- 위치: `backend/ai/skills/reporting/report-orchestrator-agent/SKILL.md`
- 내용:
  ```markdown
  # Report Orchestrator Agent

  ## Role
  AI 판단 책임 추적 및 리포트 정확도 향상 시스템

  ## Core Capabilities
  1. News Interpretation Accuracy (NIA) 계산
  2. AI 판단 → 실제 결과 연결
  3. 틀린 판단 추적 + 학습
  4. 리포트에 정확도 삽입

  ## Output Format
  Daily: {"accuracy_percentage": 92, "narrative_enhancement": "..."}
  Weekly: {"nia_score": 75, "evolution_log": {...}}
  Annual: {"full_accountability_report": {...}}
  ```

**Task 3.2**: 구현
- 위치: `backend/ai/skills/reporting/report-orchestrator-agent/report_orchestrator.py`
```python
class ReportOrchestrator:
    def __init__(self, db: Session):
        self.interpretation_repo = NewsInterpretationRepository(db)
        self.reaction_repo = NewsMarketReactionRepository(db)
        self.link_repo = NewsDecisionLinkRepository(db)

    async def calculate_news_interpretation_accuracy(
        self,
        timeframe: str = "daily"
    ) -> Dict:
        """
        NIA 계산

        Args:
            timeframe: "daily" | "weekly" | "annual"

        Returns:
            {
                "overall_accuracy": 0.75,
                "by_impact": {"HIGH": 0.85, "MEDIUM": 0.72, "LOW": 0.68},
                "by_type": {"EARNINGS": 0.85, "MACRO": 0.72, "GEOPOLITICS": 0.45},
                "best_call": {...},
                "worst_call": {...}
            }
        """
        if timeframe == "daily":
            start_date = datetime.today().date()
        elif timeframe == "weekly":
            start_date = datetime.today().date() - timedelta(days=7)
        elif timeframe == "annual":
            start_date = datetime(datetime.today().year, 1, 1).date()

        # 해석 가져오기
        interpretations = await self.interpretation_repo.get_by_date_range(
            start_date,
            datetime.today().date()
        )

        # 검증된 해석만 필터
        verified = []
        for interp in interpretations:
            reaction = await self.reaction_repo.get_by_interpretation_id(interp.id)
            if reaction and reaction.verified_at:
                verified.append({
                    "interpretation": interp,
                    "reaction": reaction
                })

        # 정확도 계산
        correct = sum(1 for v in verified if v["reaction"].interpretation_correct)
        overall_accuracy = correct / len(verified) if verified else 0.5

        # 유형별 정확도
        by_impact = self._calculate_by_impact(verified)
        by_type = self._calculate_by_type(verified)

        # Best/Worst call
        best = max(verified, key=lambda v: v["reaction"].confidence_justified)
        worst = min(verified, key=lambda v: v["reaction"].confidence_justified)

        return {
            "overall_accuracy": overall_accuracy,
            "by_impact": by_impact,
            "by_type": by_type,
            "best_call": self._format_call(best),
            "worst_call": self._format_call(worst)
        }

    async def generate_weekly_accountability_section(self) -> Dict:
        """
        주간 AI 판단 진화 로그 생성

        Returns:
            {
                "nia_score": 75,
                "improvement": "+5%p",
                "best_judgment": "...",
                "worst_judgment": "...",
                "lesson_learned": "..."
            }
        """
        current_week = await self.calculate_news_interpretation_accuracy("weekly")
        last_week = await self._get_last_week_nia()

        improvement = current_week["overall_accuracy"] - last_week["overall_accuracy"]

        return {
            "nia_score": int(current_week["overall_accuracy"] * 100),
            "improvement": f"{improvement:+.0%}p",
            "best_judgment": current_week["best_call"]["description"],
            "worst_judgment": current_week["worst_call"]["description"],
            "lesson_learned": await self._extract_lesson(current_week["worst_call"])
        }

    async def generate_annual_accountability_report(self) -> Dict:
        """
        연간 AI Accountability Report 생성

        Returns:
            {
                "nia_overall": 68,
                "by_type": {...},
                "top_3_failures": [...],
                "system_improvements": [...]
            }
        """
        annual = await self.calculate_news_interpretation_accuracy("annual")

        # 가장 틀렸던 판단 Top 3
        failures = await self.reaction_repo.get_worst_failures(limit=3)
        top_3_failures = []

        for failure in failures:
            analysis = await self._analyze_failure(failure)
            top_3_failures.append({
                "description": analysis["what_happened"],
                "lesson": analysis["lesson_learned"],
                "fix": analysis["system_improvement"]
            })

        # 시스템 개선 track record
        improvements = await self._get_system_improvements()

        return {
            "nia_overall": int(annual["overall_accuracy"] * 100),
            "by_type": {k: int(v*100) for k, v in annual["by_type"].items()},
            "top_3_failures": top_3_failures,
            "system_improvements": improvements
        }

    async def enhance_daily_report_with_accountability(
        self,
        report_data: Dict
    ) -> Dict:
        """
        Daily Report에 정확도 삽입

        Args:
            report_data: 기존 리포트 데이터

        Returns:
            정확도가 강화된 리포트 데이터
        """
        today_nia = await self.calculate_news_interpretation_accuracy("daily")

        # Page 1 narratives에 정확도 추가
        for narrative in report_data["page1"]["narratives"]:
            if narrative.get("interpretation_id"):
                reaction = await self.reaction_repo.get_by_interpretation_id(
                    narrative["interpretation_id"]
                )

                if reaction and reaction.verified_at:
                    accuracy_text = f" (해석 정확도: {int(reaction.confidence_justified*100)}%)"
                    narrative["text"] += accuracy_text

        return report_data
```

**성공 기준**:
- ✅ Daily NIA 계산 성공
- ✅ Weekly Accountability Section 생성 성공
- ✅ Annual Accountability Report 생성 성공

---

### Week 7: Daily Report Integration 📄
**목표**: Daily Report에 실제 데이터 + 정확도 삽입

**Task 4.1**: Report Generator 수정
- 파일: `backend/services/complete_5page_report_generator.py`
- 변경:
  ```python
  class Complete5PageReportGenerator:
      def __init__(self):
          self.orchestrator = ReportOrchestrator(get_db())

      def _get_report_data(self) -> dict:
          # [기존] Mock 데이터 제거
          # [신규] 실제 데이터 조회

          # War Room 결과 조회
          latest_session = debate_repo.get_latest_session()

          # News interpretations 조회
          interpretations = interpretation_repo.get_today()

          # 정확도 강화
          report_data = {
              "page1": self._get_page1_data(latest_session, interpretations),
              "page2": self._get_page2_data(latest_session),
              # ...
          }

          # Orchestrator로 정확도 삽입
          enhanced = await self.orchestrator.enhance_daily_report_with_accountability(
              report_data
          )

          return enhanced
  ```

**성공 기준**:
- ✅ Mock 데이터 0개
- ✅ 실제 War Room 결과 반영
- ✅ 정확도 퍼센트 표시

---

### Week 8: Weekly/Annual Report Integration 📈
**목표**: Weekly/Annual 리포트에 Accountability 섹션 추가

**Task 5.1**: Weekly Report Generator 생성
- 파일: `backend/services/weekly_report_generator.py`
```python
class WeeklyReportGenerator:
    async def generate(self) -> bytes:
        """주간 리포트 PDF 생성"""

        # Executive Summary
        executive_summary = await self._get_executive_summary()

        # [신규] AI 판단 진화 로그
        evolution_log = await orchestrator.generate_weekly_accountability_section()

        # Performance Analysis
        performance = await self._get_performance_analysis()

        # ... (나머지 섹션)

        # PDF 생성
        pdf = self._create_pdf({
            "executive_summary": executive_summary,
            "evolution_log": evolution_log,  # ← 신규 섹션
            "performance": performance,
            # ...
        })

        return pdf
```

**Task 5.2**: Annual Report Generator 생성
- 파일: `backend/services/annual_report_generator.py`
```python
class AnnualReportGenerator:
    async def generate(self) -> bytes:
        """연간 리포트 PDF 생성"""

        # Part 1: 2025년 전체 리뷰
        # ...

        # [신규] AI Accountability Report
        accountability = await orchestrator.generate_annual_accountability_report()

        # Part 2: 2026년 전망
        # ...

        pdf = self._create_pdf({
            # ...
            "accountability_report": accountability,  # ← 신규 섹션
            # ...
        })

        return pdf
```

**성공 기준**:
- ✅ Weekly Report에 "AI 판단 진화 로그" 섹션 포함
- ✅ Annual Report에 "AI Accountability Report" 섹션 포함
- ✅ Telegram 전송 성공

---

## 🧪 Testing Strategy

### Unit Tests
```python
# test_news_interpretation.py
async def test_news_agent_saves_interpretation():
    news = create_mock_news()
    agent = NewsAgent(db)

    await agent.analyze("NVDA", {})

    interpretation = await interpretation_repo.get_latest()
    assert interpretation is not None
    assert interpretation.headline_bias in ["BULLISH", "BEARISH", "NEUTRAL"]

# test_report_orchestrator.py
async def test_calculate_nia_daily():
    orchestrator = ReportOrchestrator(db)

    nia = await orchestrator.calculate_news_interpretation_accuracy("daily")

    assert 0 <= nia["overall_accuracy"] <= 1
    assert "by_impact" in nia
    assert "best_call" in nia
```

### Integration Tests
```python
# test_end_to_end.py
async def test_full_accountability_chain():
    # 1. News Agent 실행
    news_agent = NewsAgent(db)
    await news_agent.analyze("NVDA", {})

    # 2. War Room 실행
    war_room = WarRoomEngine(db)
    decision = await war_room.run_debate("NVDA")

    # 3. Decision Link 생성
    link = await link_repo.create({
        "interpretation_id": 1,
        "debate_session_id": decision["session_id"],
        "final_decision": decision["action"]
    })

    # 4. Market Reaction 검증 (1시간 후)
    await asyncio.sleep(3600)
    reaction = await reaction_repo.get_by_interpretation_id(1)

    assert reaction.verified_at is not None
    assert reaction.interpretation_correct in [True, False]

    # 5. NIA 계산
    nia = await orchestrator.calculate_news_interpretation_accuracy("daily")

    assert nia["overall_accuracy"] > 0
```

---

## 🚨 Rollback Plans

### Phase 1 Rollback (DB)
```bash
# 만약 문제 발생 시
alembic downgrade -1  # 1 step back
# 또는
alembic downgrade <revision_id>  # 특정 리비전으로
```

### Phase 2 Rollback (News Agent)
```python
# news_agent.py에 feature flag 추가
ENABLE_NEWS_INTERPRETATION = os.getenv("ENABLE_NEWS_INTERPRETATION", "false")

class NewsAgent:
    async def analyze(self, ticker: str, context: Dict) -> Dict:
        if ENABLE_NEWS_INTERPRETATION == "true":
            # [신규] 해석 로직
            pass
        else:
            # [기존] 기존 로직만
            pass
```

### Phase 3-5 Rollback (Reports)
- Report Generator에서 orchestrator 호출 제거
- Mock 데이터로 되돌리기

---

## 📊 Success Metrics

### Phase 1 (DB)
- ✅ 6개 테이블 모두 생성 완료
- ✅ Repository CRUD 테스트 100% 통과

### Phase 2 (News Agent)
- ✅ `news_interpretations` 테이블에 하루 평균 20+ row 저장
- ✅ Macro context 매일 업데이트 성공률 100%
- ✅ News Agent 기존 기능 정상 작동 (regression 0건)

### Phase 3 (Report Orchestrator)
- ✅ NIA 계산 시간 < 5초
- ✅ Weekly/Annual 섹션 생성 성공

### Phase 4-5 (Report Integration)
- ✅ Daily Report Mock 데이터 0%
- ✅ Weekly Report "AI 판단 진화 로그" 포함
- ✅ Annual Report "AI Accountability Report" 포함
- ✅ Telegram 전송 성공률 100%

---

## 🔄 Integration Points with Existing System

### 1. War Room (변경 없음)
- News Agent 내부 로직만 확장
- War Room orchestration 코드 변경 없음

### 2. Scheduler
- 신규 추가: `macro_context_updater` (매일 09:00)
- 기존 유지: `generate_daily_report` (매일 16:30)

### 3. Database
- 기존 20개 테이블 유지
- 신규 6개 테이블 추가
- Foreign key로 연결

### 4. Telegram Bot
- 기존 전송 로직 유지
- Report 내용만 강화됨

---

## 🎯 Final Deliverables

### Week 8 종료 후:

1. **Database**:
   - ✅ 26개 테이블 (기존 20 + 신규 6)
   - ✅ 완전한 accountability chain

2. **Agents**:
   - ✅ Enhanced News Agent (해석 기능)
   - ✅ Report Orchestrator Agent (NIA 계산)
   - ⏳ Failure Learning Agent (추후 구현)

3. **Reports**:
   - ✅ Daily Report (정확도 포함)
   - ✅ Weekly Report (AI 판단 진화 로그)
   - ✅ Annual Report (AI Accountability Report)

4. **Automation**:
   - ✅ Macro context 자동 업데이트
   - ✅ News interpretation 자동 생성
   - ✅ Market reaction 자동 검증
   - ✅ Report 자동 생성 + 전송

---

## 📝 Notes

### 핵심 원칙
1. **Zero Tolerance**: DB 변경은 반드시 db-schema-manager 거쳐야 함
2. **War Room 불가침**: News Agent 내부만 수정, War Room orchestration 변경 금지
3. **Repository Pattern**: 모든 DB 접근은 Repository를 통해서만
4. **Incremental**: 각 Phase 독립적으로 테스트 가능해야 함

### 리스크
1. **Week 3-4**: Claude API 호출 비용 증가 가능
   - Mitigation: 중요 뉴스 5개로 제한
2. **Week 5-6**: NIA 계산 로직 복잡도
   - Mitigation: 단계별 검증 + unit test
3. **Week 7-8**: Report 생성 시간 증가
   - Mitigation: 캐싱 + 비동기 처리

---

**작성일**: 2025-12-29
**다음 액션**: Phase 1 (Week 1-2) 시작 → JSON 스키마 작성부터
