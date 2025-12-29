# 리포트 관리 시스템 설계

**작성일**: 2025-12-29

---

## 📁 폴더 구조

```
d:\code\ai-trading-system\reports\
├── TEST\                    # 테스트용 리포트
│   ├── test_daily.pdf
│   ├── test_weekly.pdf
│   └── ...
│
├── Daily\                   # 일일 리포트
│   ├── 251229_Daily_Report.pdf
│   ├── 251230_Daily_Report.pdf
│   └── ...
│
├── Weekly\                  # 주간 리포트
│   ├── 251229_Weekly_Report.pdf  (W52)
│   ├── 260105_Weekly_Report.pdf  (W01)
│   └── ...
│
├── Monthly\                 # 월간 리포트
│   ├── 251229_Monthly_Report.pdf (Dec)
│   ├── 260131_Monthly_Report.pdf (Jan)
│   └── ...
│
├── Quarterly\               # 분기 리포트
│   ├── 251229_Quarterly_Report_Q4.pdf
│   ├── 260331_Quarterly_Report_Q1.pdf
│   └── ...
│
├── Half-Yearly\             # 반기 리포트
│   ├── 250630_Half_Year_Report_H1.pdf
│   ├── 251229_Half_Year_Report_H2.pdf
│   └── ...
│
└── Annual\                  # 연간 리포트
    ├── 251229_Annual_Report_2025.pdf
    └── 251229_2025_Total_&_2026_Forecast.pdf
```

---

## 📊 리포트 타입별 특징

### 1. Daily Report (일일 리포트) ⭐ 기본

**파일명**: `YYMMDD_Daily_Report.pdf`

**페이지 수**: 5 pages (현재 완성됨)

**내용**:
- Page 1: 시장 서사 (Market Narrative)
- Page 2: AI 의사결정 로직
- Page 3: 회의론자 분석
- Page 4: (Reserved for Charts)
- Page 5: 내일의 리스크

**생성 시점**: 매일 16:30 (장 마감 후)

**목적**: 
- 오늘 무슨 일이 있었나?
- AI는 어떻게 판단했나?
- 내일은 뭘 조심해야 하나?

---

### 2. Weekly Report (주간 리포트)

**파일명**: `YYMMDD_Weekly_Report.pdf` (주 마지막 날짜)

**페이지 수**: 8-10 pages

**내용**:
- **Executive Summary** (1 page)
  - 이번 주 한 문장 요약
  - 주요 이벤트 3가지
  - 수익률 요약

- **Judgment Evolution Log** (2-3 pages)
  - 월요일 vs 금요일 판단 변화
  - AI가 틀렸던 순간
  - AI가 옳았던 순간
  - 학습한 내용

- **Performance Analysis** (2 pages)
  - 주간 수익률 차트
  - 섹터별 성과
  - 베스트/워스트 트레이드

- **Skeptic Weekly Review** (1 page)
  - 이번 주 Veto 총정리
  - 회피 손실 누계
  - Skeptic Accuracy

- **Next Week Preview** (2 pages)
  - 다음 주 주요 이벤트
  - 리스크 캘린더
  - AI Positioning

**생성 시점**: 매주 금요일 17:00

**목적**:
- AI의 판단이 어떻게 진화했나?
- 이번 주에서 배운 교훈은?

---

### 3. Monthly Report (월간 리포트)

**파일명**: `YYMMDD_Monthly_Report.pdf` (월 마지막 날짜)

**페이지 수**: 15-20 pages

**내용**:
- **Executive Summary** (1 page)
  - 이번 달 시장 서사
  - 월간 수익률

- **Performance Deep Dive** (5 pages)
  - 일별 수익률 차트
  - 섹터 분석
  - 리스크 지표 변화
  - 포트폴리오 변동 추이

- **AI Learning Report** (3 pages)
  - 월간 판단 정확도
  - 개선된 점
  - 여전히 약한 부분

- **Skeptic Monthly Performance** (2 pages)
  - 월간 Veto 통계
  - 누적 회피 손실
  - Skeptic vs Market 비교

- **Strategy Review** (3 pages)
  - 이번 달 전략 효과
  - 조정 필요 사항
  - 다음 달 전략

**생성 시점**: 매월 마지막 거래일 17:00

**목적**:
- 한 달 동안 무슨 일이?
- 전략이 먹혔나?
- 다음 달은 어떻게?

---

### 4. Quarterly Report (분기 리포트)

**파일명**: `YYMMDD_Quarterly_Report_Q#.pdf`

**페이지 수**: 25-30 pages

**내용**:
- **Executive Summary** (2 pages)
  - 분기 시장 리뷰
  - 분기 수익률
  - 벤치마크 대비 성과

- **Comprehensive Performance** (8 pages)
  - 일별/주별 수익률
  - 최대 낙폭(MDD) 분석
  - 샤프 비율
  - 승률 & 손익 비율

- **AI System Evolution** (5 pages)
  - 분기별 Agent Weight 변화
  - Constitutional 변경 이력
  - 주요 버그 & 수정

- **Skeptic Quarterly Review** (3 pages)
  - 분기별 Veto 패턴
  - 계절성 분석
  - 향상된 정확도

- **Strategy Effectiveness** (5 pages)
  - 전략별 성과
  - 실패한 전략
  - 다음 분기 조정안

- **Risk Management** (2 pages)
  - 분기별 최대 리스크
  - 어떻게 관리했나
  - 개선 필요 사항

**생성 시점**: 분기 마지막 거래일 17:00 (3/31, 6/30, 9/30, 12/31)

**목적**:
- 3개월간의 전체 그림
- 전략이 장기적으로 유효한가?
- 시스템 개선 방향은?

---

### 5. Half-Yearly Report (반기 리포트)

**파일명**: `YYMMDD_Half_Year_Report_H#.pdf`

**페이지 수**: 35-40 pages

**내용**:
- **Executive Summary** (3 pages)
  - 반기 시장 환경
  - 반기 수익률
  - 주요 전환점 3개

- **Full Performance Analysis** (10 pages)
  - 월별 수익률 히트맵
  - 섹터 로테이션
  - 리스크 관리 효과
  - 포트폴리오 진화

- **AI System Deep Dive** (8 pages)
  - 6개월간 Agent 성과
  - War Room 패턴 분석
  - Constitutional 효과
  - 시스템 신뢰도 변화

- **Skeptic Half-Year Review** (4 pages)
  - 반기 Veto 전체 분석
  - 계절성 & 패턴
  - Skeptic의 진화
  - 향후 개선 방향

- **Portfolio Rebalancing** (5 pages)
  - 현재 포지션 분석
  - 리밸런싱 필요성
  - 제안 포트폴리오
  - 예상 효과

- **Macro & Market Outlook** (5 pages)
  - 하반기 전망
  - 주요 리스크
  - 기회 섹터

**생성 시점**: 6/30, 12/31 17:00

**목적**:
- 반년간의 종합 평가
- 리밸런싱 의사결정
- 하반기 전략 수립

---

### 6. Annual Report (연간 리포트) 🎯 최중요

**파일명**: `YYMMDD_Annual_Report_YYYY.pdf`

**페이지 수**: 50-60 pages

**내용**:

#### Part 1: 2025년 전체 리뷰 (30 pages)

- **Executive Summary** (5 pages)
  - 한 해 요약
  - 최종 수익률
  - 주요 사건 10개
  - 성공/실패 사례

- **Full Year Performance** (12 pages)
  - 월별/분기별 수익률
  - 벤치마크 대비
  - MDD & 변동성
  - 샤프/소르티노 비율
  - 승률 & 손익비
  - 섹터별 기여도

- **AI System Annual Review** (8 pages)
  - 연간 Agent 성과 랭킹
  - War Room 의사결정 패턴
  - Constitutional 변경 이력
  - 시스템 업그레이드
  - Trust Score 변화

- **Skeptic Full Year Analysis** (3 pages)
  - 연간 Veto 통계
  - 회피 손실 총계
  - 가장 중요했던 Veto
  - Skeptic Accuracy 진화

- **Lessons Learned** (2 pages)
  - 올해 배운 점
  - 여전히 약한 점
  - 내년 개선 방향

#### Part 2: 2026년 전망 (20 pages)

- **Market Forecast** (5 pages)
  - 글로벌 경제 전망
  - 섹터별 전망
  - 주요 리스크 Top 5
  - 기회 영역

- **AI Strategy 2026** (5 pages)
  - 내년 트레이딩 전략
  - 포트폴리오 구성안
  - 리스크 관리 계획
  - Constitutional 개정안

- **Quantitative Targets** (3 pages)
  - 목표 수익률
  - 최대 허용 MDD
  - 승률 목표
  - 샤프 비율 목표

- **Monthly Action Plan** (5 pages)
  - 1월~12월 월별 전략
  - 주요 이벤트 캘린더
  - 리밸런싱 계획

- **Risk Management 2026** (2 pages)
  - 시나리오별 대응
  - Circuit Breaker 업그레이드
  - Skeptic 권한 강화

**생성 시점**: 12/31 17:00

**목적**:
- 한 해 전체 평가
- 다음 해 전략 수립
- 투자자 보고용

---

## 🤖 자동화 계획

### 생성 스케줄

```python
# Daily
schedule.every().day.at("16:30").do(generate_daily_report)

# Weekly (금요일)
schedule.every().friday.at("17:00").do(generate_weekly_report)

# Monthly (마지막 거래일)
schedule.every().month.at("17:00").do(generate_monthly_report)

# Quarterly (3, 6, 9, 12월 말)
# 분기별로 체크

# Half-Yearly (6, 12월 말)
# 반기별로 체크

# Annual (12월 31일)
schedule.on("12/31").at("17:00").do(generate_annual_report)
```

### Telegram 전송

```python
# Daily: 무조건 전송
# Weekly: 금요일에만
# Monthly: 월 말에만
# Quarterly: 분기 말에만
# Half-Yearly: 반기 말에만
# Annual: 12/31에만
```

---

## 📝 파일명 규칙

### 형식
```
YYMMDD_[Type]_Report[_Suffix].pdf
```

### 예시
```
251229_Daily_Report.pdf
251229_Weekly_Report.pdf
251229_Monthly_Report.pdf
251229_Quarterly_Report_Q4.pdf
251229_Half_Year_Report_H2.pdf
251229_Annual_Report_2025.pdf
251229_2025_Total_&_2026_Forecast.pdf
```

---

## 🎯 구현 우선순위

### Phase 1 (완료) ✅
- Daily Report (5 pages)

### Phase 2 (다음 단계)
- Weekly Report
- 실제 데이터 연동

### Phase 3 (중기)
- Monthly Report
- Quarterly Report

### Phase 4 (장기)
- Half-Yearly Report
- Annual Report

---

## 💾 데이터 요구사항

### Daily → 실시간 데이터
- KIS API (시장 데이터)
- War Room DB (의사결정)
- Skeptic Tracker (Veto)

### Weekly → 일주일 데이터
- Daily 데이터 누적
- 주간 통계 계산

### Monthly → 한 달 데이터
- Weekly 데이터 누적
- 월간 통계 & 차트

### Quarterly → 분기 데이터
- Monthly 데이터 누적
- 전략 효과 분석

### Half-Yearly → 반기 데이터
- Quarterly 데이터 누적
- 리밸런싱 분석

### Annual → 연간 데이터
- 전체 데이터 종합
- 다음 해 전망 (외부 데이터)

---

**작성일**: 2025-12-29
**다음 단계**: Weekly Report 설계 시작
