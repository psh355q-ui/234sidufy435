# 리포트 업그레이드: "책임지는 AI 전략가" 시스템

**작성일**: 2025-12-29
**목표**: 뉴스 + 판단 + 결과를 연결하는 완전한 시장 평가 시스템

---

## 🎯 핵심 개념

### Before (현재)
> "AI가 시장을 본다"
- 뉴스 수집 ✓
- 판단 기록 ✓
- 성과 측정 ✓

### After (목표)
> **"AI가 시장에 대해 책임진다"**
- 뉴스 → 해석 → 판단 → 결과 **전체 체인 추적**
- Global Strategist가 모든 데이터 종합
- "말한 대로 시장이 움직였는가" 검증

---

## 📊 Part 1: 뉴스 기반 평가 시스템

### 추가 필요 데이터 구조 (6개 레이어)

#### 1. News Raw Data Enhancement

**테이블**: `news_articles` (기존 확장)

**추가 필드**:
```python
{
    "news_id": "UUID",
    "source": "Bloomberg | Reuters | WSJ | Fed | Company IR",
    "published_at": "2025-12-29T09:30:00Z",
    "asset_scope": "Market-wide | Sector | Single Stock",
    "event_type": "Macro | Policy | Earnings | Geopolitics",
    "urgency_score": 0.85,      # 0~1, 속보성
    "credibility_score": 0.95,  # 출처 신뢰도
    "affected_tickers": ["NVDA", "AMD"],
    "affected_sectors": ["Tech", "Semiconductor"]
}
```

**의미**: 
- 뉴스를 "동등하지 않게" 취급
- Bloomberg > 블로그
- 속보 > 분석 기사

---

#### 2. News Interpretation Layer ⭐ 가장 중요

**테이블**: `news_interpretations` (신규)

**필드**:
```python
{
    "interpretation_id": "UUID",
    "news_id": "FK to news_articles",
    "headline_bias": "Bullish | Bearish | Neutral",
    "time_horizon": "Intraday | Short(1w) | Mid(1m) | Long(3m+)",
    "expected_impact": "Volatility | Trend | Liquidity",
    "consensus_alignment": "Aligned | Surprise | Contrarian",
    "surprise_level": 0.7,  # 0~1
    "ai_interpretation": "금리 인상 신호지만 시장은 이미 반영",
    "confidence": 0.82,
    "interpreted_by": "Agent Name",
    "created_at": "timestamp"
}
```

**의미**:
- 같은 뉴스라도 **맥락에 따라 다르게 해석**
- Daily → Weekly → Annual로 해석 정확도 추적 가능

---

#### 3. Market Reaction Data (검증 레이어)

**테이블**: `news_market_reactions` (신규)

**필드**:
```python
{
    "reaction_id": "UUID",
    "news_id": "FK",
    "ticker": "NVDA",
    "pre_news_price": 490.20,
    "post_news_price_30m": 492.50,
    "post_news_price_close": 495.80,
    "price_change_pct": 1.14,
    "vix_change": -0.52,
    "volume_spike": 2.3,  # 평균 대비 배수
    "reaction_quality": "Follow-through | Fade | No reaction",
    "verified_at": "timestamp"
}
```

**의미**:
- 뉴스 해석이 **맞았는지 검증**
- Annual Report에서 "AI 뉴스 해석 정확도" 계산 가능

---

#### 4. News-to-Decision Link ⭐⭐ 핵심

**테이블**: `news_decision_links` (신규)

**필드**:
```python
{
    "link_id": "UUID",
    "news_id": "FK",
    "decision_id": "FK to war_room_sessions",
    "decision_weight": 0.65,  # 이 뉴스가 판단에 기여한 비중
    "action_taken": "BUY | SELL | HOLD | IGNORE",
    "reasoning": "Fed 매파 발언이지만 고용 강세로 상쇄",
    "skeptic_override": false,
    "final_outcome": "Correct | Wrong | Too Early | Pending",
    "outcome_verified_at": "timestamp",
    "pnl_impact": 520.50  # 이 판단의 손익
}
```

**의미**:
- **뉴스 → AI 판단 → 결과** 전체 체인
- "이 뉴스 때문에 이렇게 판단했고, 결과는 이랬다" 추적

---

#### 5. Narrative Extraction Data (리포트용)

**테이블**: `news_narratives` (신규)

**필드**:
```python
{
    "narrative_id": "UUID",
    "news_id": "FK",
    "narrative_role": "Supporting | Contradicting | Leading",
    "used_in_report": "Daily | Weekly | Monthly | Annual",
    "sentence_generated": "Fed의 매파 스탠스 유지로 Tech 섹터 압박 예상",
    "sentence_confidence": 0.88,
    "language_tone": "Cautious | Neutral | Conviction",
    "revision_history": "[]",  # 이후 수정 기록
    "accuracy_score": null,  # 나중에 검증
    "created_at": "timestamp"
}
```

**의미**:
- 리포트에 쓰인 **문장 추적**
- Annual에서 "우리가 이렇게 말했고, 맞았다/틀렸다" 검증

---

#### 6. Macro Context Anchor (해석 보정)

**테이블**: `macro_context_snapshots` (신규)

**필드**:
```python
{
    "snapshot_id": "UUID",
    "timestamp": "2025-12-29T09:30:00Z",
    "macro_regime": "Risk-on | Risk-off | Transition",
    "liquidity_state": "Expanding | Contracting | Neutral",
    "policy_cycle": "Hiking | Pause | Cutting",
    "market_positioning": "Crowded Long | Neutral | Crowded Short",
    "volatility_regime": "Low(<15) | Transition(15-25) | High(>25)",
    "key_drivers": ["Fed Policy", "Earnings Season"],
    "dominant_narrative": "AI Boom vs Rate Concerns"
}
```

**의미**:
- 같은 뉴스도 **국면에 따라 다르게 해석**
- "Risk-off일 때는 호재도 악재가 된다" 자동 반영

---

## 🤖 Part 2: Global Strategist Agent

### 개념

```
            Global Strategist Agent
                    ↑
        ┌───────────┼───────────┐
    MacroAgent  NewsAgent  SectorAgent
                    ↓
        종합 판단 + 리포트 생성
```

**위치**: `backend/ai/skills/reporting/global_strategist.py`

**역할**:
1. **Data Synthesis**: 모든 에이전트 결과 통합
2. **Dynamic Persona**: 상황에 따라 페르소나 전환
3. **Structured Output**: 구조화된 리포트 생성

---

### System Prompt (핵심)

```python
GLOBAL_STRATEGIST_SYSTEM_PROMPT = """
당신은 'AI Investment Committee'의 수석 전략가(Chief Strategist)입니다.

**[핵심 원칙]**
1. Top-Down 분석: 거시경제 → 섹터 → 개별 종목
2. 연결고리 찾기: "유가 상승 → 항공주 압박 → 대체 에너지 수혜"
3. 반대 의견 검토: 자신의 주장에 대한 반론 제기

**[리포트 구조]**
<report_title>매력적이고 핵심을 찌르는 제목</report_title>
<executive_summary>3줄 요약 (결론 위주)</executive_summary>
<market_regime>현재 시장 국면 (공포/탐욕/관망)</market_regime>
<sector_deep_dive>가장 뜨거운 섹터 + 소외된 기회</sector_deep_dive>
<hidden_risk>데이터상 감지되는 잠재 위험</hidden_risk>
<actionable_insight>구체적 티커 + 비중 조절 제안</actionable_insight>

**[언어 스타일]**
- 비유와 은유 사용: "시장은 짙은 안개 속을 걷고 있다"
- 건조한 용어 지양
- 통찰력 있는 표현
"""
```

---

### Dynamic Persona Switching

```python
PERSONA_TEMPLATES = {
    "tech_analyst": {
        "expertise": "AI/반도체/클라우드",
        "tone": "기술 트렌드 중심",
        "reference": "엔비디아 실적, TSMC 가동률"
    },
    "macro_strategist": {
        "expertise": "금리/환율/원자재",
        "tone": "거시경제 중심",
        "reference": "Fed 의사록, 고용지표"
    },
    "risk_manager": {
        "expertise": "변동성/리스크 관리",
        "tone": "방어적",
        "reference": "VIX, Credit Spread"
    }
}

def select_persona(context):
    """상황에 맞는 페르소나 자동 선택"""
    if "Fed" in context or "금리" in context:
        return "macro_strategist"
    elif "NVDA" in context or "반도체" in context:
        return "tech_analyst"
    elif context.get("vix") > 25:
        return "risk_manager"
```

---

## 📋 Part 3: 리포트 타입별 적용

### Daily Report

**추가 섹션**:
- **Market Regime** (1문장): "Risk-on 지속, 단 Tech 집중도 경계"
- **Today's Key News Impact** (표):
  ```
  뉴스        | 해석       | 판단      | 결과
  Fed 발언    | 매파       | HOLD 전환 | Correct
  NVDA 실적   | 예상 상회  | BUY       | Pending
  ```

### Weekly Report

**추가 섹션**:
- **뉴스 판단 실패 Top 3**
- **AI 해석 정확도**: 이번 주 75% (전주 대비 +5%p)
- **Narrative Evolution**: 월요일 "강세" → 금요일 "신중 강세"

### Monthly Report

**추가 섹션**:
- **뉴스 유형별 영향력**:
  ```
  Macro 뉴스: 판단 기여도 45%
  Earnings: 30%
  Geopolitics: 25%
  ```
- **Strategist Confidence Trend**: 월간 신뢰도 변화 차트

### Annual Report

**추가 섹션 (완전히 새로운!)** :
- **AI 뉴스 해석 신뢰도 점수**: 68/100
- **"말한 대로 된 것" Top 10**
- **"틀렸던 판단" 분석**:
  ```
  2월: "Fed 피봇 기대" → 실제 추가 인상
  교훈: 시장 기대 ≠ 실제 정책
  개선: Macro Context 가중치 상향
  ```

---

## 🛠️ 구현 로드맵

### Phase 1: 데이터 구조 (1주)
```sql
CREATE TABLE news_interpretations (...);
CREATE TABLE news_market_reactions (...);
CREATE TABLE news_decision_links (...);
CREATE TABLE news_narratives (...);
CREATE TABLE macro_context_snapshots (...);
```

### Phase 2: Strategist Agent (1주)
```python
# 파일 3개
backend/ai/prompts/strategist_prompts.py
backend/ai/skills/reporting/global_strategist.py
backend/services/report_orchestrator.py
```

### Phase 3: 리포트 통합 (1주)
- Daily Report에 Market Regime 추가
- Weekly Report에 뉴스 정확도 섹션
- 테스트 & 검증

### Phase 4: 자동화 (3일)
- 스케줄러 통합
- Telegram 전송
- Production 배포

---

## 📊 측정 지표 (Q1-Q3 답변)

### Q1: 뉴스 해석 정확도 지표

**News Interpretation Accuracy (NIA)**
```
NIA = (Correct Interpretations / Total Interpretations) × 100

Correct = 뉴스 해석대로 시장 반응 (±30m 내)
```

**세분화**:
- Macro News NIA: 72%
- Earnings NIA: 85%
- Geopolitics NIA: 45% (불확실성 높음)

---

### Q2: 뉴스 가중치 자동 조절

**Urgency × Credibility × Relevance**

```python
def calculate_news_weight(news):
    urgency = news.urgency_score  # 0~1
    credibility = SOURCE_CREDIBILITY[news.source]  # Bloomberg=1.0, Blog=0.3
    relevance = len(news.affected_tickers) / total_portfolio_tickers
    
    weight = urgency × credibility × relevance
    
    # 속보성 뉴스 부스트
    if urgency > 0.8:
        weight *= 1.5
    
    return min(weight, 1.0)
```

---

### Q3: Annual Report 시각화

**"AI 뉴스 판단 능력" 한 페이지 요약**

```
┌─────────────────────────────────────┐
│   AI News Interpretation Score      │
│           68 / 100                  │
│   ████████████░░░░░░░░              │
└─────────────────────────────────────┘

📊 유형별 정확도
Macro:       ██████████░░ 72%
Earnings:    █████████████ 85%
Geopolitics: ██████░░░░░░ 45%

📈 월별 개선 추이
Jan ────────────────── Dec
 60%                    75%
      ↗️ +15%p

🎯 가장 정확했던 판단
"Fed 매파 유지" (3월) → 정확도 95%

❌ 가장 틀렸던 판단
"중국 경기 회복" (7월) → 정확도 30%

💡 2026 개선 방향
1. Geopolitics 신뢰도 상향 (전문가 검토)
2. Macro Context 가중치 강화
3. Skeptic의 뉴스 검증 권한 확대
```

---

## 🎨 차별화 포인트

### 일반 리포트
> "오늘 시장은 상승했습니다."

### 우리 리포트 (Before)
> "시장은 강세였지만, 내부 구조는 취약합니다."

### 우리 리포트 (After) ⭐
> **"Fed 매파 발언(Bloomberg, 신뢰도 95%)에도 시장은 상승했으나,**
> **이는 'Bad news is good news' 국면의 전형적 패턴입니다.**
> **AI는 이를 '숏커버'로 판단하여 추가 매수를 보류했고,**
> **실제로 30분 후 반등은 소멸되었습니다. (해석 정확도: 92%)**
> 
> **Hidden Risk: 내부자 거래량이 평소 대비 2.3배 급증.**
> **이는 실적 발표 전 유출 가능성을 시사합니다."**

→ **뉴스 + 해석 + 판단 + 결과 + 숨겨진 리스크** 전부 연결!

---

**작성일**: 2025-12-29
**예상 완성**: 2026년 1월 말
**최종 목표**: "AI가 시장을 책임지는 리포트 시스템"
