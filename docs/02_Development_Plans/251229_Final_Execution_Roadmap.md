# 최종 구현 로드맵: "책임지는 AI 투자 시스템"

**작성일**: 2025-12-29
**검증 완료**: ChatGPT + Gemini × 2 리뷰 통합
**상태**: 설계 완료, 구현 준비 완료

---

## 🎯 최종 판정

> **"이 설계는 더 이상 개선하면 오히려 퇴보한다.**
> **지금이 코드로 옮길 최적 시점이다."**

### 시스템 정체성

```
"우리는 맞추는 AI를 만들지 않는다.
 우리는 책임지는 판단 주체를 만든다."
```

**Before**: AI가 시장을 본다
**After**: **AI가 시장에 대해 책임지고, 실패로부터 배운다**

---

## 📊 Phase별 구조 (4단계)

### Phase 0: 현재 상태 (완료 ✅)

**완성된 것**:
- Daily Report (5 pages)
- Page 1: Market Narrative (언어 템플릿 63개)
- Page 2: Decision Logic
- Page 3: Skeptic Analysis
- Page 5: Risk Playbook
- 한글 폰트 시스템
- Report 폴더 구조

**생성된 PDF**: `complete_5page_report.pdf`

---

### Phase 1: 데이터 기반 구축 (2주)

**목표**: 뉴스 → 해석 → 판단 → 결과 체인 구축

#### 1.1 데이터베이스 스키마 (1주)

**필수 테이블 6개**:

```sql
-- ① News Interpretation Layer (가장 중요)
CREATE TABLE news_interpretations (
    interpretation_id UUID PRIMARY KEY,
    news_id UUID REFERENCES news_articles(id),
    
    -- ChatGPT: 해석 기본
    headline_bias VARCHAR(20), -- 'Bullish' | 'Bearish' | 'Neutral'
    time_horizon VARCHAR(20),  -- 'Intraday' | 'Short' | 'Mid' | 'Long'
    expected_impact VARCHAR(50), -- 'Volatility' | 'Trend' | 'Liquidity'
    consensus_alignment VARCHAR(20), -- 'Aligned' | 'Surprise' | 'Contrarian'
    surprise_level DECIMAL(3,2), -- 0~1
    
    -- 해석 내용
    ai_interpretation TEXT,
    confidence DECIMAL(3,2),
    interpreted_by VARCHAR(100),
    created_at TIMESTAMP
);

-- ② Market Reaction Data (검증 레이어)
CREATE TABLE news_market_reactions (
    reaction_id UUID PRIMARY KEY,
    news_id UUID REFERENCES news_articles(id),
    ticker VARCHAR(10),
    
    -- 가격 반응
    pre_news_price DECIMAL(10,2),
    post_news_price_30m DECIMAL(10,2),
    post_news_price_close DECIMAL(10,2),
    price_change_pct DECIMAL(5,2),
    
    -- ChatGPT: 방향 vs 타이밍 분리
    outcome_direction VARCHAR(20), -- 'CORRECT' | 'WRONG'
    outcome_timing VARCHAR(20),    -- 'PERFECT' | 'EARLY' | 'LATE'
    
    -- Gemini: Alpha Impact (시장 대비 초과 수익)
    alpha_impact_pct DECIMAL(5,2), -- (종목 수익률 - 섹터 수익률)
    sector_etf VARCHAR(10),         -- 'SOXX' | 'XLK'
    sector_move_pct DECIMAL(5,2),
    market_move_pct DECIMAL(5,2),
    market_context VARCHAR(50),     -- 'BULLISH_DAY' | 'BEARISH_DAY'
    
    -- ChatGPT: 뉴스 유형별 검증 윈도우
    validation_window VARCHAR(10),  -- '30m' | '1D' | '3D' | '1W'
    
    -- 기타
    vix_change DECIMAL(5,2),
    volume_spike DECIMAL(4,2),
    reaction_quality VARCHAR(50),   -- 'Follow-through' | 'Fade'
    verified_at TIMESTAMP
);

-- ③ News-to-Decision Link (핵심 연결)
CREATE TABLE news_decision_links (
    link_id UUID PRIMARY KEY,
    news_id UUID REFERENCES news_articles(id),
    decision_id UUID REFERENCES war_room_sessions(id),
    
    -- 판단 연결
    decision_weight DECIMAL(3,2),   -- 이 뉴스가 판단에 기여한 비중
    action_taken VARCHAR(20),       -- 'BUY' | 'SELL' | 'HOLD' | 'IGNORE'
    reasoning TEXT,
    
    -- Skeptic 개입
    skeptic_override BOOLEAN,
    
    -- ChatGPT: 방향/타이밍 분리
    final_outcome_direction VARCHAR(20),
    final_outcome_timing VARCHAR(20),
    final_outcome_combined VARCHAR(50), -- 'Correct+Perfect' | 'Correct+Early'
    
    -- 손익
    pnl_impact DECIMAL(10,2),
    outcome_verified_at TIMESTAMP,
    created_at TIMESTAMP
);

-- ④ News Narratives (리포트 문장 추적)
CREATE TABLE news_narratives (
    narrative_id UUID PRIMARY KEY,
    news_id UUID REFERENCES news_articles(id),
    
    -- 역할
    narrative_role VARCHAR(50),     -- 'Supporting' | 'Contradicting' | 'Leading'
    used_in_report VARCHAR(20),     -- 'Daily' | 'Weekly' | 'Monthly' | 'Annual'
    
    -- ChatGPT: Narrative Revision History
    sentence_generated TEXT,
    sentence_confidence DECIMAL(3,2),
    language_tone VARCHAR(20),      -- 'Cautious' | 'Neutral' | 'Conviction'
    revision_history JSONB,         -- [{date, old, new, reason}]
    
    -- 검증
    accuracy_score DECIMAL(3,2),    -- 나중에 검증
    created_at TIMESTAMP
);

-- ⑤ Macro Context Snapshots (국면별 해석)
CREATE TABLE macro_context_snapshots (
    snapshot_id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    
    -- ChatGPT: Macro Context
    macro_regime VARCHAR(50),       -- 'Risk-on' | 'Risk-off' | 'Transition'
    liquidity_state VARCHAR(50),    -- 'Expanding' | 'Contracting' | 'Neutral'
    policy_cycle VARCHAR(50),       -- 'Hiking' | 'Pause' | 'Cutting'
    market_positioning VARCHAR(50), -- 'Crowded Long' | 'Neutral' | 'Crowded Short'
    volatility_regime VARCHAR(50),  -- 'Low(<15)' | 'Transition(15-25)' | 'High(>25)'
    
    -- Gemini: Narrative Drift
    dominant_narratives JSONB,      -- [{theme, role, shift_detected}]
    key_drivers TEXT[],
    dominant_narrative TEXT
);

-- ⑥ Failure Analysis (실패 금고)
CREATE TABLE failure_analysis (
    failure_id UUID PRIMARY KEY,
    decision_id UUID REFERENCES news_decision_links(link_id),
    
    -- Gemini: Real-time Post-Mortem
    failure_type VARCHAR(50),       -- 'Overconfidence' | 'Timing' | 'Direction'
    root_cause TEXT,
    lesson_learned TEXT,
    
    -- 시스템 조치
    system_adjustment JSONB,        -- {weight_change, confidence_cap, etc}
    applied_at TIMESTAMP,
    
    -- ChatGPT: 재발 방지
    similar_case_detected BOOLEAN,
    rag_context_updated BOOLEAN,
    
    created_at TIMESTAMP
);
```

---

#### 1.2 데이터 수집 파이프라인 (1주)

**구현 파일**:
```
backend/services/news_pipeline.py
    - fetch_news()
    - interpret_news()  # Claude API 호출
    - verify_reaction()
    - link_to_decision()
```

**핵심 로직**:
```python
async def interpret_news(news):
    """뉴스 해석"""
    # Macro Context 조회
    context = await get_macro_context_snapshot()
    
    # Claude에게 해석 요청
    interpretation = await claude_client.interpret_news(
        news=news,
        context=context,
        previous_failures=get_similar_failures(news)  # RAG
    )
    
    return interpretation
```

---

### Phase 2: Global Strategist Agent (2주)

**목표**: 판단 주체 구축 + 책임 메커니즘

#### 2.1 Strategist 핵심 구현

**파일**: `backend/ai/skills/reporting/global_strategist.py`

**System Prompt (최종)**:
```python
GLOBAL_STRATEGIST_SYSTEM_PROMPT = """
당신은 'AI Investment Committee'의 수석 전략가입니다.

**[핵심 원칙]**
1. Top-Down 분석: 거시 → 섹터 → 종목
2. 연결고리: "유가 상승 → 항공주 압박 → 대체 에너지 수혜"
3. 반대 의견 검토 (Devil's Advocate)

**[ChatGPT: 책임 메커니즘]**
매일 아침 반드시 Stance Declaration:
<stance>
  <bias>Bullish | Neutral | Defensive</bias>
  <confidence>0.73</confidence>
  <key_assumption>금리 동결 유지</key_assumption>
</stance>

**[Gemini: Shadow Trade]**
HOLD 선언 시, 가상 포지션 자동 생성:
- 시장 +2% 이상: Missed Opportunity 벌점
- 3일 연속 HOLD: 강제 Shadow Trade (0.25x size)

**[언어 스타일]**
- 비유와 은유: "시장은 안개 속"
- 조건부 표현: "가능성이 우세하나..."
"""
```

---

#### 2.2 책임 메커니즘 구현

**① Stance Declaration (ChatGPT)**:
```python
class GlobalStrategist:
    async def declare_daily_stance(self, data):
        """매일 필수 선언"""
        stance = {
            "bias": "Bullish",
            "confidence": 0.73,
            "key_assumption": "Fed 금리 동결 유지",
            "timestamp": datetime.now()
        }
        
        # DB 저장
        await db.save_stance(stance)
        
        return stance
```

**② Shadow Penalty (Gemini)**:
```python
async def apply_shadow_penalty(stance):
    """HOLD 선언 시 검증"""
    if stance["bias"] == "Neutral":
        # 가상 포지션 생성 (0.25x)
        shadow_trade = {
            "type": "SHADOW",
            "size_multiplier": 0.25,
            "purpose": "Opportunity Cost Tracking"
        }
        
        # 시장 +2% 이상이면 벌점
        if market_return > 0.02:
            penalty = {
                "type": "Missed Opportunity",
                "cost": market_return * portfolio_value * 0.25
            }
            await db.save_penalty(penalty)
```

**③ Decision Irreversibility (Gemini)**:
```python
async def change_stance(old_stance, new_stance, reason):
    """스탠스 변경 시 비용"""
    if old_stance != new_stance:
        # 신뢰도 페널티
        confidence_penalty = 0.15
        new_stance["confidence"] -= confidence_penalty
        
        # 변경 이유 필수
        if not reason:
            raise ValueError("Stance change requires explicit reason")
        
        await db.log_stance_change({
            "from": old_stance,
            "to": new_stance,
            "reason": reason,
            "penalty": confidence_penalty
        })
```

---

#### 2.3 Dynamic Persona Switching

```python
PERSONA_TEMPLATES = {
    "macro_strategist": {
        "trigger": ["Fed", "금리", "CPI", "고용"],
        "tone": "거시경제 중심",
        "reference_data": ["Fed 의사록", "고용지표"]
    },
    "tech_analyst": {
        "trigger": ["NVDA", "반도체", "AI"],
        "tone": "기술 트렌드 중심",
        "reference_data": ["TSMC 가동률", "GPU 수요"]
    },
    "risk_manager": {
        "trigger_condition": lambda ctx: ctx.get("vix") > 25,
        "tone": "방어적",
        "reference_data": ["VIX", "Credit Spread"]
    }
}

def select_persona(context):
    """상황별 페르소나 자동 선택"""
    for persona, config in PERSONA_TEMPLATES.items():
        # 키워드 매칭
        if any(kw in context for kw in config.get("trigger", [])):
            return persona
        
        # 조건 검사
        trigger_fn = config.get("trigger_condition")
        if trigger_fn and trigger_fn(context):
            return persona
    
    return "macro_strategist"  # 기본값
```

---

### Phase 3: 실패 학습 시스템 (1주)

**목표**: 틀렸을 때 더 똑똑해지는 구조

#### 3.1 Real-time Post-Mortem (Gemini)

```python
async def trigger_post_mortem(decision_link):
    """판단 실패 시 즉시 반성문"""
    if decision_link["final_outcome"] == "WRONG":
        # Claude에게 반성 요청
        analysis = await claude_client.analyze_failure(
            decision=decision_link,
            context=get_decision_context(decision_link),
            similar_failures=get_similar_failures_rag(decision_link)
        )
        
        # Failure Vault에 저장
        await db.save_failure_analysis({
            "decision_id": decision_link["link_id"],
            "failure_type": analysis["type"],
            "root_cause": analysis["cause"],
            "lesson_learned": analysis["lesson"],
            "system_adjustment": {
                "news_weight_multiplier": 0.85,  # 다음엔 가중치 낮춤
                "confidence_cap": 0.7
            }
        })
        
        # RAG 컨텍스트 업데이트
        await update_rag_context(analysis)
```

---

#### 3.2 Narrative Revision Tracking (ChatGPT)

```python
async def track_narrative_revision(narrative_id, new_sentence, reason):
    """문장 수정 추적"""
    old_narrative = await db.get_narrative(narrative_id)
    
    revision = {
        "date": datetime.now(),
        "old": old_narrative["sentence_generated"],
        "new": new_sentence,
        "reason": reason
    }
    
    # Revision History에 추가
    old_narrative["revision_history"].append(revision)
    await db.update_narrative(narrative_id, old_narrative)
```

---

### Phase 4: 리포트 통합 (1주)

**목표**: 모든 데이터를 리포트에 반영

#### 4.1 Daily Report 업데이트

**추가 섹션**:
```python
# Page 1.5: Market Regime (새 페이지)
{
    "regime": "Risk-on (전환 중)",
    "key_news_impact": [
        {
            "news": "Fed 발언",
            "interpretation": "매파 (70% 확신)",
            "decision": "HOLD 전환",
            "outcome": "Correct (방향) + Early (타이밍)",
            "alpha_impact": "+1.2%"
        }
    ]
}
```

---

#### 4.2 Weekly Report

**New Section**: **"AI 판단 진화 로그"**
```
┌─────────────────────────────────┐
│ 이번 주 해석 정확도: 75%        │
│ (전주 대비 +5%p)                │
├─────────────────────────────────┤
│ 가장 정확했던 판단:             │
│ "Fed 매파 유지" → 92% 정확도    │
│                                 │
│ 가장 틀렸던 판단:               │
│ "Tech 수요 회복" → 35% 정확도   │
│ 교훈: Geopolitics 변수 간과     │
└─────────────────────────────────┘
```

---

#### 4.3 Annual Report

**핵심 페이지**: **"AI Accountability Report"**

```
📊 News Interpretation Accuracy (NIA)
──────────────────────────────────
Overall: 68/100

유형별:
Macro:       ██████████░░ 72%
Earnings:    █████████████ 85%
Geopolitics: ██████░░░░░░ 45%

📉 가장 틀렸던 판단 Top 3
──────────────────────────────────
1. "중국 경기 회복" (7월)
   - 정확도: 30%
   - 손실: -$2,450
   - 교훈: Geopolitics 가중치 상향
   - 조치: 전문가 검토 추가

2. "Fed 조기 피봇" (3월)
   - 정확도: 35%
   - 손실: -$1,850
   - 교훈: 시장 기대 ≠ 실제 정책
   - 조치: Macro Context 강화

💡 시스템 개선 track record
──────────────────────────────────
• Geopolitics 신뢰도: 45% → 58% (+13%p)
• Skeptic 권한 강화 후 False Positive -23%
• Narrative Drift 감지 후 적응 속도 2.3배
```

---

## 🎯 Q1-Q3 최종 답변

### Q1: AI가 하루 동안 반드시 책임져야 하는 결정 단위

**답**: **"Daily Stance Declaration" (일일 스탠스 선언)**

```python
{
    "date": "2025-12-29",
    "bias": "Bullish",
    "confidence": 0.73,
    "key_assumption": "Fed 금리 동결",
    "invalidation_trigger": "CPI > 3.5%"
}
```

**왜 이것인가**:
- 매일 한 번, 회피 불가능
- 측정 가능 (다음 날 검증)
- 학습 가능 (틀렸을 때 패턴 분석)

**검증 기준**:
- 방향: 맞음/틀림
- 타이밍: 완벽/조기/후행
- Alpha Impact: 시장 대비 초과 수익

---

### Q2: Shadow Penalty vs Skeptic 충돌 시 최종 결정권

**답**: **"Skeptic이 우선, 단 벌점은 공유"**

**시나리오**:
```
Strategist: "BUY NVDA" (Bullish)
Skeptic: "VETO" (Tech 집중도 과다)
→ 최종 결정: HOLD
→ 시장 결과: +3%
```

**책임 분배**:
```python
{
    "strategist_penalty": {
        "type": "Shadow Loss",
        "amount": 시장 수익 × 0.25
    },
    "skeptic_review": {
        "type": "Veto Accuracy Check",
        "was_correct": False,  # 막지 말았어야 함
        "accuracy_impact": -0.02
    }
}
```

**원칙**:
- Skeptic 권한 > Strategist 제안
- 하지만 양쪽 모두 성과 추적
- **"안전하게 막았는데 기회 놓침"**도 기록

---

### Q3: 외부 투자자에게 보여줄 가장 설득력 있는 한 페이지

**답**: **"AI Self-Correction Track Record" (자기 교정 이력)**

```
┌─────────────────────────────────────────────────────┐
│   AI Self-Correction Performance (2025)            │
│                                                     │
│   총 실수: 47건                                     │
│   교정 완료: 43건 (91%)                             │
│   재발 방지율: 87%                                  │
└─────────────────────────────────────────────────────┘

📉 실수 → 학습 → 개선 사례

[Case 1: Fed 피봇 과신]
├ 실수 (3월): "Fed 조기 피봇" ← 틀림
├ 손실: -$1,850
├ 시스템 조치: Macro Context 가중치 +15%
└ 결과: 이후 유사 상황 정확도 78%

[Case 2: Geopolitics 무시]
├ 실수 (7월): "중국 경기 회복" ← 틀림
├ 손실: -$2,450
├ 시스템 조치: 전문가 검토 레이어 추가
└ 결과: Geopolitics NIA 45% → 58%

💡 핵심 메시지
────────────────────────────────────────
"이 AI는 틀리지만,
 같은 실수를 반복하지 않습니다."

2025년 47번 실수 중 43번을 코드로 수정.
같은 유형 재발률 13%.
```

**왜 이 페이지인가**:
- 완벽함을 주장 ❌
- **진화를 증명** ✅
- 투자자는 "완벽한 AI"보다 **"배우는 AI"**를 신뢰

---

## 🚀 실행 명령어 (최종)

```bash
# Phase 1: 데이터베이스
cd d:\code\ai-trading-system
python scripts/init_accountability_db.py

# Phase 2: Strategist Agent
python backend/ai/skills/reporting/global_strategist.py --test

# Phase 3: Failure Learning
python backend/services/failure_learning_engine.py --backfill

# Phase 4: Report Integration
python backend/services/complete_5page_report_generator.py --with-accountability
```

---

## 📅 타임라인

| Phase | 기간 | 완료 기준 |
|-------|------|-----------|
| 1. 데이터 | 2주 | 6개 테이블 + 파이프라인 |
| 2. Strategist | 2주 | Stance Declaration + Shadow |
| 3. Failure | 1주 | Post-Mortem + RAG |
| 4. Report | 1주 | Weekly/Annual 통합 |
| **Total** | **6주** | **Production Ready** |

---

**작성일**: 2025-12-29
**상태**: **실행 준비 완료 (Green Light)**
**다음 단계**: Phase 1 착수
