---
name: failure-learning-agent
description: Analyzes incorrect AI interpretations, extracts lessons, and recommends system improvements
license: Proprietary
compatibility: Requires news_interpretations, news_market_reactions, failure_analysis tables
metadata:
  author: ai-trading-system
  version: "1.0"
  category: reporting
  agent_role: post_mortem_analyst
---

# Failure Learning Agent - AI 실패 학습 시스템

## Role
틀린 AI 판단을 자동으로 분석하고, 근본 원인을 찾아내어 시스템 개선을 제안하는 전문 Agent

## Core Capabilities

### 1. 자동 실패 감지

**Trigger**: `interpretation_correct = False` in news_market_reactions

**감지 기준**:
- NIA < 60% (일일 정확도가 낮을 때)
- High confidence (80+) but wrong (과신 실패)
- High impact prediction but small actual movement (크기 예측 실패)
- Recurring pattern failures (반복적 실패 패턴)

### 2. 실패 분류 체계

#### Failure Types
- **DIRECTION_MISMATCH**: 방향 예측 실패 (BULLISH → 하락, BEARISH → 상승)
- **MAGNITUDE_ERROR**: 크기 예측 실패 (HIGH impact → 1% 이내 움직임)
- **OVERCONFIDENCE**: 과신 실패 (High confidence but wrong)
- **CONTEXT_MISREAD**: 거시 맥락 오독 (Macro context 무시)
- **SENTIMENT_FLIP**: 감정 급반전 (뉴스 직후 반대 방향으로 움직임)
- **PRICED_IN**: 이미 가격에 반영됨 (뉴스 발표 전에 움직임)
- **DELAYED_REACTION**: 지연 반응 (1h는 틀렸지만 1d는 맞음)

#### Severity Levels
- **CRITICAL**: NIA 5%p 이상 하락 원인, 반복적 실패 패턴
- **MAJOR**: High confidence + wrong, High impact 예측 실패
- **MINOR**: 단발성 실패, 예측 가능한 오류

### 3. Root Cause Analysis (RCA)

**분석 프로세스**:
```
1. Context 수집
   - 해석 시점의 macro context
   - 뉴스 내용 및 sentiment
   - 실제 시장 반응 (1h/1d/3d)
   - 동일 종목의 최근 해석 히스토리

2. Claude API 호출 (RCA)
   - Prompt: "왜 이 해석이 틀렸는가?"
   - 제공 정보: 위 context 전체
   - 요청 응답: Root cause, Lesson learned, Recommended fix

3. Pattern 매칭
   - 과거 실패 사례와 유사도 비교
   - 반복 패턴 감지 (같은 종류의 실패 3회 이상)
   - 시스템적 문제 vs 일회성 오류 구분
```

### 4. Lesson Learned 추출

**Good Lesson 기준**:
- ✅ Specific: "Fed 매파 발언" → "Fed의 'higher for longer' 표현은 시장에 이미 priced-in"
- ✅ Actionable: "다음부터는 X를 Y로 변경"
- ✅ Measurable: "Before NIA: 68%, After NIA: 72%"

**Bad Lesson 예시**:
- ❌ Vague: "시장을 잘못 읽음" (근본 원인 없음)
- ❌ Not actionable: "운이 나빴음" (개선 불가)
- ❌ Too broad: "AI가 완벽하지 않음" (너무 추상적)

### 5. System Improvement 제안

**Fix 유형**:

#### A. Prompt Engineering
```python
{
    "fix_type": "PROMPT_UPDATE",
    "description": "Fed tone tracker weight 증가",
    "before": "Fed stance weight: 20%",
    "after": "Fed stance weight: 35%",
    "affected_file": "backend/ai/debate/news_agent.py",
    "line_number": 456
}
```

#### B. Context Enhancement
```python
{
    "fix_type": "CONTEXT_ADDITION",
    "description": "Geopolitical risk decay rate 모델 추가",
    "implementation": "macro_context_snapshots에 geopolitical_risk_decay 컬럼 추가",
    "affected_table": "macro_context_snapshots",
    "sql_migration": "ALTER TABLE macro_context_snapshots ADD COLUMN geopolitical_risk_decay FLOAT DEFAULT 0.5"
}
```

#### C. RAG Knowledge Update
```python
{
    "fix_type": "RAG_UPDATE",
    "description": "Ukraine 전쟁 패턴을 RAG knowledge에 추가",
    "document_path": "backend/data/knowledge/geopolitical_patterns.md",
    "content": "지정학적 리스크는 평균 3일 내 50% 감소 (priced-in 빠름)"
}
```

#### D. New Agent/Feature
```python
{
    "fix_type": "NEW_FEATURE",
    "description": "Regulatory Risk Agent 신설",
    "justification": "정부 규제 뉴스 해석 정확도 45% → 심각한 시스템 갭",
    "implementation_phase": "2026 Q2"
}
```

## Core Functions

### `analyze_failure(interpretation_id, trigger="DAILY_NIA_LOW")`
**목적**: 특정 해석의 실패 분석

**Args**:
- `interpretation_id`: 분석할 해석 ID
- `trigger`: "DAILY_NIA_LOW" | "OVERCONFIDENCE" | "MANUAL"

**Process**:
1. Context 수집 (해석 + 반응 + macro context)
2. Failure type 분류
3. Severity 판정
4. Claude API로 RCA
5. Pattern 매칭 (과거 유사 실패)
6. Lesson learned 생성
7. Recommended fix 제안
8. failure_analysis 테이블에 저장

**Returns**:
```python
{
    "failure_id": 123,
    "failure_type": "DIRECTION_MISMATCH",
    "severity": "MAJOR",
    "root_cause": "Fed 매파 발언을 과대평가, 시장은 이미 priced-in",
    "lesson_learned": "Fed tone은 literal하게 해석 (wishful thinking 금지)",
    "recommended_fix": "Fed tone tracker weight 20% → 35% 증가",
    "similar_failures": [45, 67, 89],  # 유사 실패 IDs
    "pattern_detected": True
}
```

### `batch_analyze_failures(start_date, end_date, min_severity="MAJOR")`
**목적**: 기간 내 모든 실패 일괄 분석

**Args**:
- `start_date`, `end_date`: 분석 기간
- `min_severity`: 최소 심각도

**Returns**:
```python
{
    "total_analyzed": 25,
    "by_type": {
        "DIRECTION_MISMATCH": 10,
        "MAGNITUDE_ERROR": 8,
        "OVERCONFIDENCE": 5,
        "CONTEXT_MISREAD": 2
    },
    "critical_patterns": [
        {
            "pattern": "Fed 매파 발언 과대평가",
            "occurrences": 5,
            "avg_loss": -3.2,
            "recommended_fix": "Fed tone tracker weight 증가"
        }
    ]
}
```

### `get_top_recurring_failures(limit=10)`
**목적**: 반복적 실패 패턴 조회

**Returns**:
```python
[
    {
        "pattern": "Geopolitical risk overestimation",
        "count": 12,
        "avg_nia_impact": -8.5,
        "first_occurrence": "2025-02-15",
        "last_occurrence": "2025-11-20",
        "fix_applied": True,
        "fix_effective": True,
        "nia_improvement": 16.0
    },
    ...
]
```

### `track_fix_effectiveness(failure_id, before_nia, after_nia)`
**목적**: 수정 효과 추적

**Args**:
- `failure_id`: 실패 분석 ID
- `before_nia`: 수정 전 NIA
- `after_nia`: 수정 후 NIA

**Process**:
1. failure_analysis 업데이트 (fix_effective = True/False)
2. NIA 개선도 기록
3. 효과 없으면 추가 분석 트리거

### `suggest_system_improvements()`
**목적**: Annual Report용 시스템 개선 제안 종합

**Returns**:
```python
{
    "completed_improvements": [
        {
            "date": "2025-03-15",
            "improvement": "Fed tone tracker weight 증가",
            "before_nia": 68,
            "after_nia": 72,
            "impact": "+4%p"
        }
    ],
    "pending_improvements": [
        {
            "priority": "HIGH",
            "improvement": "Regulatory Risk Agent 신설",
            "justification": "정부 규제 뉴스 NIA 45% (매우 낮음)",
            "estimated_impact": "+15%p",
            "implementation_cost": "2 weeks"
        }
    ],
    "rejected_improvements": [
        {
            "improvement": "실시간 소셜미디어 센티먼트 추가",
            "reason": "테스트 결과 노이즈만 증가, NIA 오히려 -2%p"
        }
    ]
}
```

## Integration Points

### 1. Daily NIA Monitor
```python
# backend/automation/scheduler.py
def run_daily_nia_check(self):
    daily_nia = report_orchestrator.calculate_news_interpretation_accuracy("daily")

    if daily_nia["overall_accuracy"] < 0.60:
        # Trigger failure analysis
        failure_analyzer = FailureAnalyzer(db)

        # Analyze all today's failures
        today_failures = [
            item for item in daily_nia["worst_calls"]
            if item["correct"] == False
        ]

        for failure in today_failures:
            failure_analyzer.analyze_failure(
                failure["interpretation_id"],
                trigger="DAILY_NIA_LOW"
            )

        # Send Telegram alert
        telegram.send_message(
            f"⚠️ Daily NIA: {daily_nia['overall_accuracy']*100:.1f}%\n"
            f"분석된 실패: {len(today_failures)}건"
        )
```

### 2. Overconfidence Detector
```python
# backend/automation/price_tracking_verifier.py
async def verify_interpretations(self, time_horizon="1d"):
    for reaction in pending:
        if not correct and interpretation.confidence >= 80:
            # High confidence but wrong → Critical failure
            failure_analyzer.analyze_failure(
                interpretation.id,
                trigger="OVERCONFIDENCE"
            )
```

### 3. Weekly Pattern Review
```python
# backend/automation/scheduler.py (every Friday)
def run_weekly_failure_review(self):
    failure_analyzer = FailureAnalyzer(db)

    # Get recurring patterns
    patterns = failure_analyzer.get_top_recurring_failures(limit=5)

    # Generate weekly accountability section
    orchestrator = ReportOrchestrator(db)
    weekly_section = orchestrator.generate_weekly_accountability_section()

    # Combine failures + accountability
    weekly_report = {
        "nia_section": weekly_section,
        "failure_patterns": patterns
    }
```

## Decision Framework

### Severity 판정 로직

```python
def _determine_severity(
    interpretation: NewsInterpretation,
    reaction: NewsMarketReaction,
    similar_failures: List[FailureAnalysis]
) -> str:
    """
    CRITICAL: 반복 패턴 (3회 이상) OR High impact 예측 실패
    MAJOR: High confidence but wrong OR 큰 손실 (-5%+)
    MINOR: 나머지
    """
    # Pattern check
    if len(similar_failures) >= 3:
        return "CRITICAL"

    # High impact prediction but failed
    if interpretation.expected_impact == "HIGH" and abs(reaction.actual_price_change_1d) < 2.0:
        return "CRITICAL"

    # Overconfidence
    if interpretation.confidence >= 80 and not reaction.interpretation_correct:
        return "MAJOR"

    # Large loss
    if reaction.actual_price_change_1d and abs(reaction.actual_price_change_1d) >= 5.0:
        return "MAJOR"

    return "MINOR"
```

### Failure Type 분류 로직

```python
def _classify_failure_type(
    interpretation: NewsInterpretation,
    reaction: NewsMarketReaction
) -> str:
    """
    Failure type 자동 분류
    """
    bias = interpretation.headline_bias
    actual_change = reaction.actual_price_change_1d

    # Direction mismatch
    if bias == "BULLISH" and actual_change < -1.0:
        return "DIRECTION_MISMATCH"
    if bias == "BEARISH" and actual_change > 1.0:
        return "DIRECTION_MISMATCH"

    # Magnitude error
    if interpretation.expected_impact == "HIGH" and abs(actual_change) < 2.0:
        return "MAGNITUDE_ERROR"
    if interpretation.expected_impact == "LOW" and abs(actual_change) > 5.0:
        return "MAGNITUDE_ERROR"

    # Overconfidence
    if interpretation.confidence >= 80 and not reaction.interpretation_correct:
        return "OVERCONFIDENCE"

    # Context misread (check macro context alignment)
    if interpretation.macro_context:
        if interpretation.macro_context.regime == "RISK_OFF" and bias == "BULLISH":
            if actual_change < 0:
                return "CONTEXT_MISREAD"

    # Sentiment flip (1h correct but 1d wrong)
    if reaction.actual_price_change_1h and reaction.actual_price_change_1d:
        if abs(reaction.actual_price_change_1h) > 1 and abs(reaction.actual_price_change_1d) > 1:
            if (reaction.actual_price_change_1h > 0) != (reaction.actual_price_change_1d > 0):
                return "SENTIMENT_FLIP"

    return "DIRECTION_MISMATCH"  # Default
```

## Claude API Prompt Template

### Root Cause Analysis Prompt

```python
PROMPT_TEMPLATE = """당신은 AI 트레이딩 시스템의 실패 분석 전문가입니다.

아래 AI 해석이 틀렸습니다. 근본 원인을 분석해주세요.

## 해석 정보
- 종목: {ticker}
- 뉴스 헤드라인: {headline}
- AI 예측: {headline_bias} (confidence: {confidence}%)
- 예상 임팩트: {expected_impact}
- Time horizon: {time_horizon}
- AI 추론: {reasoning}

## 거시 경제 컨텍스트 (해석 당시)
- Market regime: {regime}
- Fed stance: {fed_stance}
- VIX: {vix_level} ({vix_category})
- Market sentiment: {market_sentiment}
- Dominant narrative: {dominant_narrative}

## 실제 시장 반응
- 뉴스 발표 시점 가격: ${price_at_news}
- 1시간 후: {actual_change_1h:+.2f}%
- 1일 후: {actual_change_1d:+.2f}%
- 3일 후: {actual_change_3d:+.2f}%

## 유사 과거 실패 사례
{similar_failures_summary}

## 요청사항
다음 JSON 형식으로 응답해주세요:
{{
    "root_cause": "근본 원인 (1-2문장, 구체적으로)",
    "lesson_learned": "배운 교훈 (actionable, 다음부터 X를 Y로 변경)",
    "recommended_fix": "시스템 개선 제안 (구체적 구현 방법)",
    "fix_type": "PROMPT_UPDATE|CONTEXT_ADDITION|RAG_UPDATE|NEW_FEATURE",
    "pattern_type": "SYSTEMATIC|ONE_OFF",
    "confidence": 0-100 (이 분석의 확신도)
}}

분석 시 고려사항:
1. AI가 놓친 시장 맥락은 무엇인가?
2. 뉴스가 이미 priced-in 되었을 가능성은?
3. Sentiment flip (반대 방향 움직임)의 원인은?
4. Macro context와 뉴스 해석의 정합성은?
5. 과거 유사 실패와의 패턴은?
"""
```

## Output Examples

### Example 1: Overconfidence Failure

**Input**:
- NVDA 실적 발표 → BULLISH (confidence: 95%)
- 예상: HIGH impact (+5%+)
- 실제: -2.5% (하락)

**Analysis Output**:
```python
{
    "failure_id": 456,
    "failure_type": "DIRECTION_MISMATCH",
    "severity": "MAJOR",
    "root_cause": "실적은 좋았으나 가이던스가 기대 미달. AI는 EPS만 보고 판단했으나 시장은 forward guidance를 더 중요하게 평가함",
    "lesson_learned": "Tech 실적 뉴스는 EPS뿐 아니라 가이던스, 마진, CapEx도 함께 고려해야 함",
    "recommended_fix": "News Agent prompt에 '실적 발표 시 가이던스 체크' 추가. EPS weight 60% → 40%, Guidance weight 0% → 30%",
    "fix_type": "PROMPT_UPDATE",
    "similar_failures": [234, 345, 389],
    "pattern_detected": True,
    "pattern_type": "SYSTEMATIC",
    "rag_update_needed": True,
    "rag_content": "NVDA 같은 AI 칩 기업은 가이던스가 EPS보다 주가에 2배 영향"
}
```

### Example 2: Geopolitical Risk Overestimation

**Input**:
- Ukraine 전쟁 확대 뉴스 → BEARISH (confidence: 85%)
- 예상: HIGH impact (-5%+)
- 실제: -0.5% (거의 무반응)

**Analysis Output**:
```python
{
    "failure_id": 789,
    "failure_type": "MAGNITUDE_ERROR",
    "severity": "CRITICAL",
    "root_cause": "지정학적 리스크는 이미 3일 전 초기 보도에서 대부분 priced-in. 후속 뉴스는 추가 영향 미미",
    "lesson_learned": "지정학적 리스크는 decay rate 적용 필요. 초기 보도 후 3일 내 50% 감소",
    "recommended_fix": "macro_context_snapshots에 geopolitical_risk_decay_rate 컬럼 추가. 초기 이벤트 후 경과 일수에 따라 임팩트 감소 적용",
    "fix_type": "CONTEXT_ADDITION",
    "similar_failures": [123, 234, 345, 456, 567],
    "pattern_detected": True,
    "pattern_type": "SYSTEMATIC",
    "fix_priority": "HIGH",
    "implementation": {
        "sql": "ALTER TABLE macro_context_snapshots ADD COLUMN geopolitical_risk_decay_rate FLOAT DEFAULT 0.5",
        "code_change": "backend/ai/debate/news_agent.py:_interpret_news() - Apply decay to geopolitical news impact"
    }
}
```

## Guidelines

### Do's ✅
- 실패 발생 즉시 자동 분석 (NIA < 60% 시)
- Overconfidence 실패는 MAJOR 이상으로 분류
- 유사 실패 3회 이상 → CRITICAL pattern
- Lesson learned는 반드시 actionable해야 함
- Fix 적용 후 effectiveness 추적 (before/after NIA)
- RAG knowledge에 패턴 저장

### Don'ts ❌
- 단순 "운이 나빴음" 같은 vague 분석 금지
- 일회성 실패를 과대평가 금지 (MINOR로 분류)
- Fix 제안 없이 실패만 나열 금지
- 검증 없이 Fix 적용 금지 (A/B test 필요)
- 과거 패턴 무시 금지

## Performance Metrics

### 목표
- **실패 분석 커버리지**: 90% 이상 (NIA < 60% 시)
- **Pattern 감지율**: 80% 이상 (3회 반복 시)
- **Fix 효과**: 평균 +5%p NIA 개선
- **분석 시간**: 30초 이내 (Claude API 포함)

### Monitoring
- 일일 실패 분석 건수
- Pattern 감지 건수
- Fix 적용 건수 및 효과
- RAG 업데이트 건수

## Version History

- **v1.0** (2025-12-29): Initial release with automatic failure analysis and RCA

## Related Files

- `backend/ai/skills/reporting/failure-learning-agent/failure_analyzer.py`
- `backend/automation/scheduler.py` (daily NIA check)
- `backend/automation/price_tracking_verifier.py` (overconfidence detection)
- `backend/database/repository.py` (FailureAnalysisRepository)
