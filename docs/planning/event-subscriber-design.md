# Event Subscriber Design (T4.2)

## 1. 개요
본 문서는 **Phase 4 Multi-Strategy Integration**의 일환으로 구현된 **이벤트 구독자(Event Subscriber)** 및 **재처리(Retry) 전략**에 대해 기술합니다.

## 2. 이벤트 구독 모델 (Event-Driven Architecture)

### 2.1 주요 이벤트 및 핸들러

| 이벤트 타입 | 트리거 시점 | 핸들러 (Subscriber) | 동작 (Action) |
| :--- | :--- | :--- | :--- |
| **CONFLICT_DETECTED** | `ConflictDetector`가 충돌 감지 직후 | `handle_conflict_detected` | - 경고 로그 기록 (`WARNING`)<br>- (To-Do) 관리자 대시보드 알림 발송 |
| **ORDER_BLOCKED_BY_CONFLICT** | 충돌로 인해 주문이 차단되었을 때 | `handle_order_blocked` | - 에러 로그 기록 (`ERROR`)<br>- (To-Do) 사용자 피드백(Popup) 생성 |
| **PRIORITY_OVERRIDE** | 우선순위 오버라이드가 발생했을 때 | `handle_priority_override` | - 정보 로그 기록 (`INFO`)<br>- 오버라이드 이력 추적 |
| **OWNERSHIP_TRANSFERRED** | 소유권 이전이 성공적으로 완료되었을 때 | `handle_ownership_transferred` | - 포트폴리오 재계산 트리거 (`PortfolioOptimizer`)<br>- 로그 기록 |

### 2.2 구현 상세
- **모듈 위치**: `backend/events/subscribers.py`
- **등록 위치**: `backend/main.py` (`lifespan` 시작 시 `register_subscribers()` 호출)

## 3. 재처리(Retry) 전략

네트워크 일시 장애나 외부 서비스 지연 등에 대비하기 위해 **Exponential Backoff** 방식의 재시도 로직을 적용했습니다.

### 3.1 Retry Decorator
- **위치**: `backend/utils/retry.py`
- **설정**:
  - `max_retries`: 3회
  - `delay`: 1초 (초기)
  - `backoff`: 2배씩 증가 (1s -> 2s -> 4s)
- **적용**: 모든 이벤트 핸들러(`handle_*`)에 데코레이터(`@retry`) 형태로 적용됨.

### 3.2 예외 처리
- 재시도 횟수 초과 시 최종 실패로 간주하고 로그(`logger.warning`)를 남김으로써 시스템 전체 멈춤 방지.
- 이벤트 버스는 핸들러의 예외를 캐치하여 메인 프로세스(주문 실행 등)에 영향을 주지 않도록 설계됨 (`best-effort` delivery).

## 4. 향후 확장 계획 (Phase 5+)
- **Async Handling**: 현재 동기식(`event_bus.publish`) 처리를 Celery/Redis 기반 비동기 큐(`RabbitMQ`)로 확장하여 처리량 증대.
- **Dead Letter Queue (DLQ)**: 최종 실패한 이벤트를 별도 저장소에 보관하여 수동 재처리 기능 제공.
