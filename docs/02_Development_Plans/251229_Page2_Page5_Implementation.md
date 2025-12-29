# Page 2 & 5 Implementation Plan

**목표**: 완전한 5-페이지 AI 리포트 완성

**완료 기한**: 2025-12-29 (3-4시간 예상)

---

## Page 2: AI Decision Logic Transparency

### 목적
> "AI가 어떻게 생각했는가"를 보여주는 페이지

### 핵심 섹션

#### 1. Decision Flow (의사결정 흐름)
```
[시장 데이터] 
    ↓
[8 Agents 분석]
    ↓
[War Room 토론] → [Skeptic 검토]
    ↓
[최종 결정]
```

**구현 방법**:
- 간단한 Text-based diagram
- 각 단계별 핵심 판단 1줄
- 화살표로 흐름 표시

#### 2. 오늘의 트레이드 (Executed + Rejected)

**실행된 트레이드 (Top 3)**:
```
┌──────────────────────────────────────────┐
│ Ticker │ Action │ Reason (한 줄)        │
├──────────────────────────────────────────┤
│ NVDA   │ BUY    │ AI 칩 수요 급증 + 옵션 Call 우세 │
│ TSLA   │ SELL   │ 밸류에이션 리스크 + 거래량 감소  │
└──────────────────────────────────────────┘
```

**거부된 트레이드 (Skeptic이 막은 것)**:
```
┌──────────────────────────────────────────┐
│ Ticker │ Proposed │ Veto Reason         │
├──────────────────────────────────────────┤
│ META   │ BUY      │ Tech 섹터 집중도 과다 │
└──────────────────────────────────────────┘
```

#### 3. War Room 토론 요약

**전환점만 추출** (ChatGPT 피드백):
```
초기 → 전환점 → 최종

예시:
초기: 5/8 Agents가 BUY 제안
전환점: Skeptic이 거래량 부족 지적
최종: 6/8 Agents가 HOLD로 전환
```

**구현**:
- 3단계 요약 (초기/전환점/최종)
- 핵심 구절만 (10단어 이내)
- 전체 로그 ❌

---

## Page 5: Tomorrow Risk Playbook

### 목적
> "내일 뭘 조심해야 하는가" + "AI는 어떤 자세인가"

### 핵심 섹션

#### 1. Top 3 Risks (내일/이번 주)

```
┌──────────────────────────────────────────┐
│ Risk               │ 확률 │ AI 대응     │
├──────────────────────────────────────────┤
│ Fed 매파 발언      │ 30%  │ 포지션 축소 │
│ Tech 실적 부진     │ 25%  │ 방어 섹터   │
│ 금리 급등         │ 20%  │ 현금 확보   │
└──────────────────────────────────────────┘
```

#### 2. AI Stance (오늘의 자세)

**3가지 상태**:
- 🔴 **DEFENSIVE** (방어적): 현금 비중 ↑, 포지션 축소
- 🟡 **NEUTRAL** (중립적): 현 상태 유지
- 🟢 **AGGRESSIVE** (공격적): 포지션 확대, 기회 포착

**시각화**:
```
[DEFENSIVE] ←────●────→ [AGGRESSIVE]
                ↑
            현재 위치
```

#### 3. Tomorrow Scenario Matrix

```
┌─────────────────┬──────────────┬──────────────┐
│ 시나리오        │ 확률         │ AI 행동      │
├─────────────────┼──────────────┼──────────────┤
│ 상승 지속       │ 40%          │ 포지션 유지  │
│ 횡보            │ 35%          │ 관망         │
│ 조정            │ 25%          │ 부분 청산    │
└─────────────────┴──────────────┴──────────────┘
```

#### 4. Action Items Checklist

```
내일 체크할 항목:
□ Fed 위원 발언 (14:00)
□ Tech 실적 발표 (장후)
□ VIX 20 돌파 여부
```

---

## 데이터 요구사항

### Page 2 필요 데이터

```python
{
    "decision_flow": {
        "market_data": "지수 상승 +0.8%, VIX 급락",
        "agents_initial": "5/8 BUY 제안",
        "war_room_pivot": "Skeptic이 거래량 부족 지적",
        "final_decision": "6/8 HOLD로 전환"
    },
    "executed_trades": [
        {
            "ticker": "NVDA",
            "action": "BUY",
            "reason": "AI 칩 수요 급증 + 옵션 Call 우세"
        }
    ],
    "rejected_trades": [
        {
            "ticker": "META",
            "proposed": "BUY",
            "veto_reason": "Tech 섹터 집중도 과다"
        }
    ]
}
```

### Page 5 필요 데이터

```python
{
    "top_risks": [
        {
            "risk": "Fed 매파 발언",
            "probability": 30,
            "ai_response": "포지션 축소"
        }
    ],
    "ai_stance": "NEUTRAL",  # DEFENSIVE | NEUTRAL | AGGRESSIVE
    "tomorrow_scenarios": [
        {
            "scenario": "상승 지속",
            "probability": 40,
            "ai_action": "포지션 유지"
        }
    ],
    "action_items": [
        "Fed 위원 발언 (14:00)",
        "Tech 실적 발표 (장후)",
        "VIX 20 돌파 여부"
    ]
}
```

---

## 디자인 원칙 (Page 1, 3과 동일)

1. **한글 폰트**: 모든 테이블에 `get_korean_font_name()` 사용
2. **줄간격**: `leading=20-28` 유지
3. **용어 해설**: 필요 시 각주 추가
4. **조건부 표현**: 언어 템플릿 활용 (가능한 경우)

---

## 구현 순서

### Step 1: Page2Generator (예상 2시간)
1. Decision Flow 텍스트 다이어그램
2. Executed/Rejected Trades 테이블
3. War Room 요약 (3단계)

### Step 2: Page5Generator (예상 1.5시간)
1. Top 3 Risks 테이블
2. AI Stance 표시기
3. Scenario Matrix
4. Action Items 체크리스트

### Step 3: 5-Page 통합 (예상 0.5시간)
1. CompleteReportGenerator 업데이트
2. Page Break 추가
3. 전체 PDF 생성

### Step 4: 테스트 (예상 0.5시간)
1. Mock 데이터로 전체 PDF 생성
2. Telegram 전송
3. 검증

---

## Mock 데이터 예시

### Page 2 Mock Data
```python
mock_page2 = {
    "decision_flow": {
        "market_data": "지수 상승 +0.8%, VIX -5.2%",
        "agents_initial": "5/8 Agents BUY 제안",
        "war_room_pivot": "Skeptic: 거래량 -18% 경고",
        "final_decision": "6/8 Agents HOLD로 전환"
    },
    "executed_trades": [
        {"ticker": "NVDA", "action": "BUY", "reason": "AI 칩 수요 급증, 옵션 Call 우세"},
        {"ticker": "AAPL", "action": "HOLD", "reason": "안정적 흐름, 추가 신호 대기"},
    ],
    "rejected_trades": [
        {"ticker": "TSLA", "proposed": "BUY", "veto_reason": "밸류에이션 과도, 변동성 높음"},
        {"ticker": "META", "proposed": "BUY", "veto_reason": "Tech 섹터 집중도 30% 초과"},
    ]
}
```

### Page 5 Mock Data
```python
mock_page5 = {
    "top_risks": [
        {"risk": "Fed 위원 매파 발언", "probability": 30, "ai_response": "포지션 10% 축소"},
        {"risk": "Tech 실적 부진", "probability": 25, "ai_response": "방어 섹터 전환"},
        {"risk": "10년물 금리 급등", "probability": 20, "ai_response": "현금 비중 확대"},
    ],
    "ai_stance": "NEUTRAL",
    "tomorrow_scenarios": [
        {"scenario": "상승 지속 (+0.5~1%)", "probability": 40, "ai_action": "현 포지션 유지"},
        {"scenario": "횡보 (±0.3%)", "probability": 35, "ai_action": "관망"},
        {"scenario": "조정 (-0.5~1%)", "probability": 25, "ai_action": "부분 청산 (30%)"},
    ],
    "action_items": [
        "Fed 위원 발언 모니터링 (14:00 KST)",
        "Tech 섹터 실적 발표 확인 (장후)",
        "VIX 20선 돌파 여부",
        "10년물 금리 4.5% 수준 주시",
    ]
}
```

---

## 성공 기준

1. ✅ Page 2, 5 PDF 개별 생성 성공
2. ✅ 5-Page 통합 PDF 생성 성공
3. ✅ 모든 한글 정상 표시
4. ✅ 테이블 폰트 깨짐 없음
5. ✅ Telegram 전송 성공

---

**예상 완료 시간**: 2025-12-29 23:00
**다음 단계**: 자동화 (스케줄러 + 실제 데이터)
