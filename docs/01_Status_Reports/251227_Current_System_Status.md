# AI Trading System - 현재 시스템 상태 및 실거래 준비 현황

**날짜**: 2025-12-27
**작성자**: Claude Code
**전체 진행률**: 98%
**목표**: DB 데이터 축적 후 실제 거래 테스트

---

## 📊 시스템 완료 현황

### ✅ 완료된 핵심 Phase (0-27)

| Phase | 내용 | 완료율 | 비고 |
|-------|------|--------|------|
| **0-19** | 기반 시스템 (Feature Store, AI Agent, RAG, KIS 연동) | 100% | ✅ |
| **20** | 실시간 뉴스 (Finviz + SEC EDGAR) | 100% | ✅ |
| **21** | SEC CIK-Ticker 매핑 | 100% | ✅ |
| **22** | War Room 프론트엔드 | 100% | ✅ |
| **23** | ChipWarSimulator | 100% | ✅ |
| **24** | ChipWarAgent (8번째 에이전트) | 100% | ✅ |
| **25.0** | 프론트엔드 UI 통합 | 100% | ✅ |
| **25.1** | 24시간 수익률 추적 | 100% | ✅ |
| **25.2** | 성과 대시보드 | 100% | ✅ |
| **25.3** | 에이전트별 성과 추적 | 100% | ✅ |
| **25.4** | 가중치 자동 조정 & 알림 | 100% | ✅ 방금 완료 |
| **26** | REAL MODE (KIS 주문 실행) | 100% | ✅ |
| **27** | Constitutional AI | 100% | ✅ |

---

## 🎯 현재 목표: DB 데이터 축적

### 실거래 테스트를 위한 필수 데이터

실제 거래를 안전하게 테스트하려면 다음 데이터가 충분히 쌓여야 합니다:

#### 1. 에이전트 성과 데이터 (`agent_vote_tracking`)

**필요 데이터**:
- 최소 20개 투표 / 에이전트 (가중치 계산 가능)
- 24시간 후 평가 완료된 투표
- 에이전트별 정확도 측정

**현재 상태 확인 필요**:
```sql
-- 에이전트별 투표 수
SELECT agent_name, COUNT(*) as vote_count,
       COUNT(*) FILTER (WHERE status = 'EVALUATED') as evaluated_count
FROM agent_vote_tracking
GROUP BY agent_name;

-- 평가 완료된 투표 중 정확도
SELECT agent_name,
       AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as accuracy
FROM agent_vote_tracking
WHERE status = 'EVALUATED'
GROUP BY agent_name;
```

#### 2. 합의 성과 데이터 (`price_tracking`)

**필요 데이터**:
- War Room 합의 결과 추적
- 24시간 후 실제 수익률
- 합의 신뢰도와 성과의 상관관계

**현재 상태 확인 필요**:
```sql
-- 평가 완료된 합의
SELECT consensus_action,
       COUNT(*) as count,
       AVG(return_pct) as avg_return,
       AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as accuracy
FROM price_tracking
WHERE status = 'EVALUATED'
GROUP BY consensus_action;
```

#### 3. War Room 토론 기록 (`ai_debate_sessions`)

**필요 데이터**:
- 최소 50개 이상의 토론 세션
- 다양한 종목에 대한 토론
- Constitutional 검증 통과율

**현재 상태 확인 필요**:
```sql
-- 토론 세션 통계
SELECT
    COUNT(*) as total_sessions,
    COUNT(DISTINCT ticker) as unique_tickers,
    AVG(CASE WHEN constitutional_valid THEN 1.0 ELSE 0.0 END) as pass_rate,
    COUNT(*) FILTER (WHERE signal_id IS NOT NULL) as signals_generated
FROM ai_debate_sessions;
```

---

## 📋 데이터 축적 전략

### Phase 1: 데이터 수집 기간 (1-2주)

**목표**: 충분한 성과 데이터 축적

**작업 내용**:
1. **War Room 자동 실행 스케줄러 설정**
   - 매일 오전 9시, 오후 3시 주요 종목 토론
   - 대상: NVDA, GOOGL, AAPL, MSFT, TSLA (5종목)
   - 하루 10개 세션 × 14일 = 140개 세션

2. **24시간 자동 평가**
   - `price_tracking_scheduler.py` 실행
   - 매일 자정 전날 세션 평가
   - 에이전트별 투표 평가

3. **데이터 모니터링 대시보드**
   - 실시간 데이터 축적 현황
   - 에이전트별 투표 수
   - 평가 완료율

### Phase 2: 데이터 분석 (3-5일)

**목표**: 축적된 데이터로 시스템 검증

**작업 내용**:
1. **에이전트 성과 분석**
   - 각 에이전트의 정확도 측정
   - 과신/저평가 에이전트 탐지
   - 가중치 계산 실행

2. **합의 메커니즘 검증**
   - 합의 신뢰도 vs 실제 성과
   - Constitutional 검증 효과 측정
   - 최적 신뢰도 임계값 결정

3. **리스크 평가**
   - 최대 손실 시나리오 분석
   - 포지션 크기 최적화
   - 손절 전략 검증

### Phase 3: 모의 거래 테스트 (1주)

**목표**: KIS 모의투자 계좌로 실전 테스트

**작업 내용**:
1. **모의투자 환경 설정**
   - KIS_IS_VIRTUAL=true 확인
   - 초기 자금: $10,000 (가상)
   - 포지션 제한: 종목당 5% 이하

2. **자동 거래 실행**
   - War Room 합의 → 자동 주문
   - Constitutional 검증 통과 필수
   - 신뢰도 >= 70% 종목만 거래

3. **성과 추적**
   - 일일 손익 기록
   - 승률 측정
   - 최대 낙폭 (Max Drawdown) 모니터링

### Phase 4: 실거래 전환 (준비 완료 후)

**목표**: 실제 자금으로 소액 거래

**필수 조건**:
- [ ] 모의 거래 승률 >= 60%
- [ ] 최대 낙폭 <= -15%
- [ ] Constitutional 검증 통과율 >= 95%
- [ ] 에이전트 가중치 안정화 (변동 < 10%)

**실거래 전략**:
- 초기 자금: $1,000 (최소)
- 포지션 크기: 종목당 $50-100
- 일일 거래 제한: 최대 3건
- 손절 라인: -5% 자동 청산

---

## 🔧 즉시 실행 가능한 작업

### 1. DB 상태 확인 스크립트 작성

```python
# backend/scripts/check_data_readiness.py
"""
실거래 준비 상태 확인

📊 Data Sources:
    - PostgreSQL: agent_vote_tracking, price_tracking, ai_debate_sessions

🔗 External Dependencies:
    - sqlalchemy: DB 연결
    - pandas: 데이터 분석
"""

from sqlalchemy import text
from backend.database.repository import get_sync_session
import pandas as pd

def check_agent_votes():
    """에이전트별 투표 데이터 확인"""
    db = get_sync_session()

    query = text("""
        SELECT
            agent_name,
            COUNT(*) as total_votes,
            COUNT(*) FILTER (WHERE status = 'EVALUATED') as evaluated,
            AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as accuracy
        FROM agent_vote_tracking
        WHERE status = 'EVALUATED'
        GROUP BY agent_name
        ORDER BY total_votes DESC
    """)

    result = db.execute(query).fetchall()
    df = pd.DataFrame(result, columns=['agent', 'total', 'evaluated', 'accuracy'])

    print("\n📊 에이전트별 투표 현황:")
    print(df.to_string(index=False))
    print(f"\n✅ 가중치 계산 가능 에이전트: {len(df[df['total'] >= 20])}/8")

    db.close()
    return df

def check_consensus_performance():
    """합의 성과 확인"""
    db = get_sync_session()

    query = text("""
        SELECT
            consensus_action,
            COUNT(*) as count,
            AVG(return_pct) as avg_return,
            AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as accuracy
        FROM price_tracking
        WHERE status = 'EVALUATED'
        GROUP BY consensus_action
    """)

    result = db.execute(query).fetchall()
    df = pd.DataFrame(result, columns=['action', 'count', 'avg_return', 'accuracy'])

    print("\n📈 합의 성과:")
    print(df.to_string(index=False))

    db.close()
    return df

def check_debate_sessions():
    """토론 세션 확인"""
    db = get_sync_session()

    query = text("""
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT ticker) as tickers,
            AVG(CASE WHEN constitutional_valid THEN 1.0 ELSE 0.0 END) as pass_rate,
            COUNT(*) FILTER (WHERE signal_id IS NOT NULL) as signals
        FROM ai_debate_sessions
    """)

    result = db.execute(query).fetchone()

    print("\n🏛️ War Room 토론 통계:")
    print(f"  총 세션: {result[0]}")
    print(f"  종목 수: {result[1]}")
    print(f"  검증 통과율: {result[2]:.1%}")
    print(f"  시그널 생성: {result[3]}")

    db.close()

    # 실거래 준비 상태 판단
    ready = (
        result[0] >= 50 and  # 최소 50개 세션
        result[1] >= 5 and   # 최소 5개 종목
        result[2] >= 0.90    # 90% 이상 통과
    )

    print(f"\n{'✅' if ready else '⚠️'} 실거래 준비: {'완료' if ready else '데이터 부족'}")

    return ready

if __name__ == "__main__":
    print("=" * 80)
    print("실거래 준비 상태 점검")
    print("=" * 80)

    check_agent_votes()
    check_consensus_performance()
    ready = check_debate_sessions()

    print("\n" + "=" * 80)
    if ready:
        print("✅ 모의 거래 테스트 가능!")
        print("다음 단계: backend/scripts/run_paper_trading.py")
    else:
        print("⚠️ 데이터 축적 필요")
        print("다음 단계: War Room 자동 실행 스케줄러 설정")
    print("=" * 80)
```

### 2. War Room 자동 실행 스케줄러

```python
# backend/automation/war_room_scheduler.py
"""
War Room 자동 실행 스케줄러

📊 Data Sources:
    - FastAPI: War Room API (/api/war-room/debate)
    - PostgreSQL: 토론 결과 저장

🔗 External Dependencies:
    - schedule: 스케줄링
    - requests: API 호출
"""

import schedule
import time
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 주요 종목 리스트
TICKERS = ["NVDA", "GOOGL", "AAPL", "MSFT", "TSLA"]
API_BASE = "http://localhost:8000"

def run_war_room_debate(ticker: str):
    """War Room 토론 실행"""
    try:
        logger.info(f"🏛️ Starting War Room debate for {ticker}")

        response = requests.post(
            f"{API_BASE}/api/war-room/debate",
            json={"ticker": ticker},
            timeout=300  # 5분 타임아웃
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ {ticker} - {result['consensus']['action']} "
                       f"(confidence: {result['consensus']['confidence']:.2%})")
        else:
            logger.error(f"❌ {ticker} - Error: {response.status_code}")

    except Exception as e:
        logger.error(f"❌ {ticker} - Exception: {e}")

def morning_debates():
    """오전 토론 (9시)"""
    logger.info("🌅 Morning debates starting...")
    for ticker in TICKERS:
        run_war_room_debate(ticker)
        time.sleep(60)  # 1분 간격

def afternoon_debates():
    """오후 토론 (3시)"""
    logger.info("🌆 Afternoon debates starting...")
    for ticker in TICKERS:
        run_war_room_debate(ticker)
        time.sleep(60)

# 스케줄 설정
schedule.every().day.at("09:00").do(morning_debates)
schedule.every().day.at("15:00").do(afternoon_debates)

if __name__ == "__main__":
    logger.info("🤖 War Room Auto Scheduler Started")
    logger.info(f"Tickers: {TICKERS}")
    logger.info("Schedule: 09:00, 15:00 daily")

    # 즉시 한 번 실행 (테스트)
    logger.info("🧪 Running test debate...")
    run_war_room_debate("NVDA")

    # 스케줄 루프
    while True:
        schedule.run_pending()
        time.sleep(60)
```

### 3. 24시간 평가 스케줄러 확인

**이미 구현됨**: `backend/automation/price_tracking_scheduler.py`

확인 사항:
- [ ] 스케줄러가 실행 중인지 확인
- [ ] 평가 로직이 정상 작동하는지 테스트
- [ ] 로그 파일 확인

---

## 📊 다음 단계 액션 플랜

### 즉시 실행 (오늘)

1. **DB 상태 확인**
   ```bash
   python backend/scripts/check_data_readiness.py
   ```

2. **War Room 수동 테스트**
   ```bash
   # 프론트엔드에서 NVDA, GOOGL, AAPL 토론 실행
   # 결과 확인: agent_vote_tracking, price_tracking 테이블
   ```

3. **24시간 후 평가 대기**
   - 내일 같은 시간에 평가 결과 확인
   - 에이전트별 정확도 측정

### 1주차 (데이터 축적)

1. **War Room 스케줄러 실행**
   ```bash
   python backend/automation/war_room_scheduler.py
   ```

2. **매일 데이터 확인**
   - 투표 수 증가 확인
   - 평가 완료율 모니터링
   - 오류 로그 점검

3. **1주 후 분석**
   - 에이전트 성과 리포트
   - 가중치 계산 실행
   - 최적화 포인트 발견

### 2주차 (검증 및 테스트)

1. **모의 거래 시작**
   - KIS_IS_VIRTUAL=true 설정
   - 소액 자동 거래
   - 성과 추적

2. **리스크 검증**
   - 최대 낙폭 측정
   - 승률 계산
   - 전략 조정

3. **실거래 결정**
   - 조건 충족 시 실거래 전환
   - 미충족 시 추가 데이터 축적

---

## 🎯 성공 기준

### 데이터 축적 완료 조건

- [x] Phase 25.4 완료 (가중치 자동 조정)
- [ ] 에이전트별 최소 20개 평가 완료 투표
- [ ] 최소 50개 War Room 세션
- [ ] 24시간 평가 시스템 안정 작동

### 모의 거래 성공 조건

- [ ] 1주일 승률 >= 60%
- [ ] 최대 낙폭 <= -15%
- [ ] Constitutional 검증 통과율 >= 95%
- [ ] 일평균 수익률 >= 0.5%

### 실거래 전환 조건

- [ ] 2주 모의 거래 누적 수익률 >= 5%
- [ ] 샤프 비율 >= 1.0
- [ ] 에이전트 가중치 안정화
- [ ] 리스크 관리 시스템 검증 완료

---

## 📝 요약

**현재 상태**:
- ✅ 모든 Phase (0-27) 완료
- ✅ 자기학습 시스템 구축 완료 (Phase 25.4)
- ⚠️ 실제 성과 데이터 부족 (축적 필요)

**즉시 할 일**:
1. DB 상태 확인 스크립트 실행
2. War Room 수동 테스트 (5종목)
3. 24시간 후 평가 결과 확인

**목표 달성 시점**:
- 1주 후: 충분한 데이터 축적
- 2주 후: 모의 거래 검증
- 3주 후: 실거래 준비 완료 (조건 충족 시)

**최종 목표**:
📈 **안전하고 수익성 있는 자동 트레이딩 시스템 실거래 시작**

---

**작성일**: 2025-12-27
**다음 업데이트**: 데이터 축적 1주 후 (2026-01-03)
