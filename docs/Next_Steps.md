# 다음 단계 계획 (Next Steps)

**작성일**: 2025-12-29  
**현재 진행률**: 70%  
**예상 완료**: 2025-12-31

---

## 📋 진행 중인 작업

### 1. 14일 데이터 수집 🚀 실행 중

**상태**: 백그라운드에서 자동 실행 중
- **시작**: 2025-12-29 09:24
- **종료 예정**: 2026-01-12 09:24
- **티커**: AAPL, NVDA, MSFT
- **간격**: 1시간
- **목표**: 336 사이클

**모니터링**:
```powershell
# 진행 상황 확인
cd d:\code\ai-trading-system\backend
python scripts\monitor_collection.py

# 로그 확인
Get-Content logs\data_collection_20251229.log -Tail 20

# 검증
python scripts\validate_collection.py
```

**다음 체크포인트**: 2025-12-30 아침

---

## 🎯 다음 작업 우선순위

### 우선순위 1: 실거래 환경 Phase 3 (통합 테스트) ⭐⭐⭐

**목표**: War Room → KISBrokerAdapter → KIS API 전체 파이프라인 검증

**예상 시간**: 1-2시간

#### Task 3.1: TWAP Executor 테스트

**목적**: TWAP 알고리즘이 KISBrokerAdapter와 정상 작동하는지 검증

**작업**:
```python
# backend/tests/integration/test_twap_execution.py 생성

from backend.execution.kis_broker_adapter import KISBrokerAdapter
from backend.execution.executors import TWAPExecutor
import os

async def test_twap_with_kis():
    """TWAP + KIS Broker 통합 테스트 (Paper Trading)"""
    
    # 1. Adapter 생성
    account_no = os.getenv("KIS_PAPER_ACCOUNT")
    adapter = KISBrokerAdapter(account_no=account_no, is_virtual=True)
    
    # 2. TWAP Executor 생성
    executor = TWAPExecutor(adapter)
    
    # 3. 소량 주문 실행 (1-2주)
    fills = await executor.execute(
        ticker="AAPL",
        total_quantity=2,  # 소량 테스트
        duration_minutes=5,  # 5분
        slice_interval_seconds=60  # 1분 간격
    )
    
    # 4. 검증
    summary = executor.get_execution_summary()
    assert summary["total_quantity"] == 2
    assert summary["num_slices"] == 5
    
    print(f"✅ TWAP Test Complete")
    print(f"  Avg Price: ${summary['avg_fill_price']:.2f}")
    print(f"  Commission: ${summary['total_commission']:.2f}")
```

**실행**:
```powershell
cd d:\code\ai-trading-system\backend
$env:PYTHONPATH="D:\code\ai-trading-system"
pytest tests/integration/test_twap_execution.py -v
```

**성공 기준**:
- ✅ 주문 5개 슬라이스로 분할됨
- ✅ 모든 슬라이스 실행 성공
- ✅ 평균 체결가 계산 정확
- ✅ Commission 계산 정확

---

#### Task 3.2: War Room 전체 파이프라인 테스트

**목적**: War Room 토론 → Constitutional 검증 → KIS 주문 실행 검증

**작업**:
```python
# backend/tests/integration/test_war_room_execution.py 생성

from backend.api.war_room_router import run_war_room_debate, DebateRequest

async def test_war_room_paper_trading():
    """War Room → KIS Paper Trading 전체 플로우"""
    
    # 1. War Room 토론 실행
    request = DebateRequest(ticker="AAPL")
    
    response = await run_war_room_debate(
        request=request,
        execute_trade=True  # 🎯 실제 주문 실행
    )
    
    # 2. 검증
    assert response.session_id > 0
    assert response.ticker == "AAPL"
    assert len(response.votes) >= 8  # 8 agents
    assert response.consensus["action"] in ["BUY", "SELL", "HOLD"]
    
    # 3. 주문 검증
    if response.consensus["confidence"] >= 0.7:
        if response.consensus["action"] != "HOLD":
            assert response.order_id is not None
            print(f"✅ Order executed: {response.order_id}")
        else:
            print(f"⏸️ HOLD - No order")
    
    print(f"✅ War Room Test Complete")
    print(f"  Action: {response.consensus['action']}")
    print(f"  Confidence: {response.consensus['confidence']:.0%}")
```

**실행**:
```powershell
pytest tests/integration/test_war_room_execution.py -v
```

**성공 기준**:
- ✅ 8 agents 투표 완료
- ✅ PM 중재 정상 작동
- ✅ Constitutional 검증 통과
- ✅ Confidence >= 0.7일 때 주문 실행
- ✅ 주문 ID 반환됨

---

#### Task 3.3: 에러 시나리오 테스트

**목적**: 예외 상황 대응 검증

**시나리오**:
1. **API Rate Limit**
   - 초당 요청 제한 초과 시 재시도
   - 지수 백오프 작동 확인

2. **계좌 잔고 부족**
   - 주문 실행 전 잔고 확인
   - 부족 시 적절한 에러 메시지

3. **시장 마감 시간**
   - `is_market_open()` 체크
   - 마감 시 주문 차단

4. **Constitutional 위반**
   - 포지션 크기 제한 (5% 초과)
   - 일일 거래 횟수 제한
   - 위반 시 주문 차단

**실행**:
```powershell
pytest tests/integration/test_error_scenarios.py -v
```

---

### 우선순위 2: War Room 프론트엔드 통합 ⭐⭐

**목표**: War Room Analytics API를 프론트엔드 대시보드에 연결

**예상 시간**: 3-4시간

#### Task 2.1: Agent 투표 분포 차트
- **Component**: `frontend/src/components/WarRoom/AgentVotingChart.tsx`
- **API**: `GET /api/war-room/debate/{session_id}`
- **Chart**: 바차트 (Agent별 BUY/SELL/HOLD 비율)

#### Task 2.2: Shadow Trading 성과 그래프
- **Component**: `frontend/src/components/WarRoom/ShadowTradingPerformance.tsx`
- **API**: `GET /api/war-room/shadow-trading/performance`
- **Chart**: 라인 차트 (시간별 Win rate, Sharpe ratio)

#### Task 2.3: 토론 타임라인
- **Component**: `frontend/src/components/WarRoom/DebateTimeline.tsx`
- **API**: `GET /api/war-room/debate/timeline`
- **Display**: 시간별 토론 결과 타임라인

---

### 우선순위 3: Production Checklist ⭐

**목표**: 실전투자 전환 전 체크리스트 완료

**예상 시간**: 2-3시간

#### Task 3.1: 모의투자 10회 거래 완료
- [ ] 최소 10회 War Room 토론 실행
- [ ] 주문 실행 성공률 90% 이상
- [ ] Constitutional violation 0건
- [ ] 평균 Confidence >= 0.7

#### Task 3.2: 리스크 관리 시스템 검증
- [ ] 포지션 크기 제한 작동 (5% 이하)
- [ ] 일일 거래 횟수 제한 작동 (10회 이하)
- [ ] Stop-loss 자동 실행 (향후 구현)
- [ ] 손실 한도 알림 (향후 구현)

#### Task 3.3: 모니터링 시스템 구축
- [ ] Slack 알림 설정
- [ ] Email 알림 설정
- [ ] 일일 거래 리포트 자동 생성
- [ ] 이상 거래 탐지 시스템

#### Task 3.4: 문서화
- [ ] API 문서 최신화
- [ ] 배포 가이드 작성
- [ ] 트러블슈팅 가이드 작성
- [ ] 백업/복구 절차 문서화

---

## 📅 타임라인

### Week 1 (2025-12-29 ~ 2026-01-04)
- **Day 1 (12/29)**: ✅ War Room Analytics 완료, Phase 1&2 완료
- **Day 2 (12/30)**: Phase 3 통합 테스트
- **Day 3 (12/31)**: 프론트엔드 통합 시작
- **Day 4 (01/01)**: 프론트엔드 통합 완료
- **Day 5-7**: Production Checklist

### Week 2 (2026-01-05 ~ 2026-01-11)
- **모의투자 10회 거래 완료**
- **리스크 관리 검증**
- **모니터링 시스템 구축**
- **문서화 완료**

### Week 3 (2026-01-12~)
- **14일 데이터 수집 완료**
- **실전투자 전환 검토**
- **소액 실거래 시작 (신중하게)**

---

## 🎯 마일스톤

### Milestone 1: 통합 테스트 완료 (2025-12-31)
- ✅ TWAP/VWAP 테스트 통과
- ✅ War Room 전체 플로우 검증
- ✅ 에러 시나리오 대응 검증

### Milestone 2: 프론트엔드 완성 (2026-01-03)
- ✅ War Room Analytics 대시보드
- ✅ Agent 투표 차트
- ✅ Shadow Trading 성과 그래프

### Milestone 3: Production Ready (2026-01-10)
- ✅ 모의투자 10회 성공
- ✅ 리스크 관리 검증
- ✅ 모니터링 시스템 작동
- ✅ 문서화 완료

### Milestone 4: 실전 전환 (2026-01-15)
- ✅ 14일 데이터 수집 완료
- ✅ Production Checklist 100%
- ✅ 소액 실거래 시작

---

## 🔧 Quick Reference

### 자주 사용하는 명령어

#### 데이터 수집
```powershell
# 모니터링
python backend/scripts/monitor_collection.py

# 검증
python backend/scripts/validate_collection.py

# 로그 확인
Get-Content backend/logs/data_collection_20251229.log -Tail 20
```

#### KIS Broker 테스트
```powershell
cd backend
$env:PYTHONPATH="D:\code\ai-trading-system"
python test_kis.py
```

#### War Room 실행
```powershell
# API 서버 시작
python backend/main.py

# War Room 토론 (Paper Trading)
curl -X POST http://localhost:8001/api/war-room/debate \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}' \
  -d execute_trade=true
```

#### 통합 테스트
```powershell
pytest backend/tests/integration/ -v
```

---

## 📝 주의사항

### ⚠️ 실전 전환 전 필수 확인
1. **KIS_IS_VIRTUAL=false로 변경하기 전**:
   - [ ] Production Checklist 100% 완료
   - [ ] 모의투자 10회 이상 성공
   - [ ] Constitutional violation 0건
   - [ ] 팀원/상사 승인 (해당 시)

2. **실전 거래 시작 시**:
   - [ ] 소액으로 시작 (최대 $100)
   - [ ] 익숙한 종목만 (AAPL, NVDA, MSFT)
   - [ ] Stop-loss 설정
   - [ ] 실시간 모니터링

3. **비상 연락**:
   - KIS 고객센터: 1544-5000
   - 긴급 시 수동으로 주문 취소

---

## 🚀 최종 목표

**2주 후 (2026-01-12)**:
- ✅ 14일 히스토리 데이터 확보
- ✅ War Room 시스템 완전 가동
- ✅ 실거래 환경 100% 준비 완료
- ✅ 소액 실거래 시작 가능

**1개월 후 (2026-01-29)**:
- ✅ 안정적인 실거래 운영
- ✅ 데이터 기반 의사결정
- ✅ 성과 측정 및 개선

---

**작성자**: AI Trading System  
**최종 수정**: 2025-12-29 10:06 KST
