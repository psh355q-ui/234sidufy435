# T5.2 API Response Optimization Plan

## 1. 현황 분석
### 1.1 N+1 Query 문제 감지
현재 `GET /api/v1/positions/ownership` 엔드포인트는 `PositionOwnership` 목록을 조회한 후, 루프 내에서 각 객체의 `strategy` 관계 속성(`o.strategy.name`, `o.strategy.priority` 등)에 접근합니다.

```python
# backend/api/strategy_router.py
for o in ownerships:
    # o.strategy 접근 시 Lazy Loading 발생 가능성 높음
    if o.strategy:
       ...
```

SQLAlchemy의 기본 Lazy Loading 전략으로 인해, 소유권 20개를 조회하면:
- 1개의 소유권 목록 조회 쿼리
- **20개의 개별 전략 조회 쿼리** (최악의 경우)
가 발생하여 성능 저하 원인이 됩니다.

### 1.2 캐싱 부재
포지션 소유권 정보는 변화가 아주 빈번하지는 않지만(몇 초 단위 아님), 대시보드에서 매우 자주 조회되는 데이터입니다. 현재는 매 요청마다 DB를 조회하고 있습니다.

---

## 2. 최적화 전략

### 2.1 N+1 Query 방지 (Eager Loading)
**해결책**: SQLAlchemy의 `joinedload`를 사용하여 `PositionOwnership` 조회 시 `Strategy` 테이블을 JOIN하여 한 번에 가져옵니다.

**구현 가이드**:
```python
from sqlalchemy.orm import joinedload

# Repository 수정 또는 Router 내 쿼리 옵션 추가
query = db.query(PositionOwnership).options(
    joinedload(PositionOwnership.strategy)
)
```
이렇게 하면 단 **1개의 JOIN 쿼리**로 모든 데이터를 가져올 수 있습니다.

### 2.2 캐싱 전략 (Redis)
**전략**: "Write-Through" 또는 "Short TTL Read-Aside".
소유권 변경(`acquire`, `transfer`, `release`)은 중요한 트랜잭션이므로 즉시 반영되어야 합니다. 따라서 **짧은 TTL(예: 3초)**을 가진 캐싱을 적용하여, 대시보드의 과도한 폴링 부하를 줄이되 데이터 신선도를 유지하는 전략을 추천합니다.

**적용 포인트**:
- `GET /api/v1/positions/ownership`: Cache Key `ownership:list:{filter_hash}` (TTL 3~5초)
- 변경 API 호출 시 관련 키 Invalidation (선택적, 구현 복잡도 대비 3초 TTL이 효율적일 수 있음)

### 2.3 페이로드 최적화
현재 응답 구조(`PositionOwnershipResponse`)는 `Strategy` 객체를 중첩하여 반환합니다. 필요한 필드만 선택적으로 직렬화하여 전송 데이터 크기를 줄입니다.

**개선 전**:
Pydantic 모델이 `orm_mode=True`로 모든 필드를 가져올 때 불필요한 내부 메타데이터가 포함될 수 있음.

**개선 후**:
명시적인 Pydantic 스키마(`PositionOwnershipWithStrategy`)를 사용하여 클라이언트(프론트엔드) 데이터 그리드에 꼭 필요한 필드만 노출합니다. (현재 구현된 로직이 이를 수동으로 매핑하고 있어, 이를 Pydantic `from_orm`으로 자동화하되 `exclude` 옵션을 활용하는 것이 코드 유지보수성과 성능 면에서 유리함)

---

## 3. 실행 계획 (Action Items)

1. **[Backend] Repository 쿼리 최적화**:
   - `PositionOwnershipRepository.list_ownerships` 메서드(또는 해당 로직)에 `.options(joinedload(PositionOwnership.strategy))` 추가.

2. **[Backend] Pydantic 최적화**:
   - `strategy_router.py`의 수동 딕셔너리 구성 루프를 제거하고, SQLAlchemy 객체를 직접 Pydantic 모델로 반환하도록 리팩토링 (Speed up execution).

3. **[Frontend] 폴링 주기 조정**:
   - 대시보드 컴포넌트의 폴링 주기를 1초에서 3~5초로 조정하거나/WebSocket 이벤트(`OWNERSHIP_TRANSFERRED`)를 수신하여 `refetch` 하는 하이브리드 방식 적용.

---

## 4. 구현 상태 (2026-01-13)

### ✅ 완료
1. **N+1 Query 방지**: `joinedload(PositionOwnership.strategy)` 적용 완료
   - 위치: `backend/api/strategy_router.py:list_ownerships` (line 372)
2. **Pydantic 최적화**: 수동 딕셔너리 루프 제거 → `from_orm` 사용
3. **캐싱 구현**: `backend/core/cache.py`의 async Redis + InMemory 폴백 활용
   - Cache Key 생성: MD5 해시 기반 (`ownership:list:{hash}`)
   - TTL: **3초** (대시보드 폴링 최적화)
   - 캐시 적용 위치: `list_ownerships` endpoint (line 381-392)

### 📋 권장 사항 (향후 개선)
1. **Frontend 폴링 조정**: 
   - T5.3/T5.4 (Multi-Strategy Dashboard UI) 구현 시 `refetchInterval: 3000` 적용
   - 참고: `frontend/src/pages/Dashboard.tsx` (line 68) - 현재 10초
2. **WebSocket 통합** (선택적):
   - `OWNERSHIP_TRANSFERRED` 이벤트 수신 → 즉시 refetch
   - 폴링 주기를 30초로 늘리고 이벤트를 주요 트리거로 사용

### 🎯 성능 개선 예상치
- **이전**: 소유권 20개 조회 시 21개 쿼리 + 매 요청 DB 조회
- **현재**: 소유권 20개 조회 시 1개 JOIN 쿼리 + 3초 캐싱
- **부하 감소**: 대시보드가 3초 간격 폴링 시 ~67% DB 쿼리 감소
