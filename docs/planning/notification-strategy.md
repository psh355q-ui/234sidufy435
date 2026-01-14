# Conflict Alert Notification Strategy (T5.5)

**작성일**: 2026-01-13  
**담당**: Gemini (설계), Claude Code (구현 완료 ✅)

---

## 1. 알림 우선순위 전략

### 1.1 우선순위 레벨 정의

| Level | Name | Trigger Event | Color | Icon | Auto-Dismiss | Example |
|-------|------|---------------|-------|------|--------------|---------|
| **🔴 Critical** | 차단됨 | 충돌로 인한 주문 차단 (`ORDER_BLOCKED_BY_CONFLICT`) | Red | 🚫 | 30초 | "NVDA 주문이 차단됨: long_term 전략이 소유 중" |
| **🟡 Warning** | 경고 | 소유권 이전 발생 (`OWNERSHIP_TRANSFERRED`, `PRIORITY_OVERRIDE`) | Yellow | ⚠️ | 15초 | "AAPL 소유권이 dividend에서 long_term으로 이전됨" |
| **🔵 Info** | 정보 | 전략 활성화/비활성화 | Blue | ℹ️ | 10초 | "trading 전략이 활성화됨" |

### 1.2 우선순위 규칙
1. **Critical > Warning > Info** (화면 최상단 우선 표시)
2. **같은 레벨 내**: 최신 알림이 위로
3. **최대 동시 표시**: 5개 (초과 시 "더보기" 버튼)

---

## 2. 알림 그룹화 전략

### 2.1 그룹화 조건
같은 **Ticker**의 충돌 알림이 **5초 이내**에 연속 발생하면 그룹화합니다.

**예시**:
```
Before (5개 개별 알림):
🚫 NVDA 주문 차단 (trading)
🚫 NVDA 주문 차단 (aggressive)
🚫 AAPL 주문 차단 (trading)
🚫 TSLA 주문 차단 (dividend)
🚫 MSFT 주문 차단 (trading)

After (그룹화):
🚫 NVDA 외 3개 종목에서 5건의 주문이 차단됨 [상세보기 ▼]
```

### 2.2 그룹화 로직
```typescript
// Grouping Algorithm
interface GroupedAlert {
  ticker: string;      // 대표 종목 (첫 번째 또는 가장 빈번한 것)
  count: number;       // 총 알림 수
  additionalTickers: string[];  // 나머지 종목들
  alerts: OrderConflict[];      // 원본 알림 리스트
}

function groupAlerts(alerts: OrderConflict[]): GroupedAlert[] {
  const tickerMap = new Map<string, OrderConflict[]>();
  
  alerts.forEach(alert => {
    const key = alert.ticker;
    if (!tickerMap.has(key)) {
      tickerMap.set(key, []);
    }
    tickerMap.get(key)!.push(alert);
  });
  
  // 2개 이상의 같은 ticker → 그룹화
  const groups = Array.from(tickerMap.entries())
    .filter(([_, alerts]) => alerts.length >= 2)
    .map(([ticker, alerts]) => ({
      ticker,
      count: alerts.length,
      additionalTickers: [],
      alerts
    }));
  
  return groups;
}
```

### 2.3 그룹 표시 UI
```
┌──────────────────────────────────────────────────────┐
│ 🚫 NVDA 외 3개 종목에서 5건의 주문이 차단됨           │
│    [상세보기 ▼]                              [X]    │
├──────────────────────────────────────────────────────┤
│ ▼ 세부 내용:                                         │
│   • NVDA: trading 전략에서 2건 차단                  │
│   • AAPL: dividend 전략에서 1건 차단                 │
│   • TSLA: aggressive 전략에서 1건 차단               │
│   • MSFT: trading 전략에서 1건 차단                  │
└──────────────────────────────────────────────────────┘
```

---

## 3. 알림 지속 시간 및 제거 전략

### 3.1 자동 제거 (Auto-Dismiss)
| Level | Duration | Rationale |
|-------|----------|-----------|
| Critical | 30초 | 중요한 정보, 사용자가 인지할 시간 필요 |
| Warning | 15초 | 중간 우선순위, 빠른 인지 |
| Info | 10초 | 덜 중요, 빠르게 사라짐 |

**구현**:
```typescript
useEffect(() => {
  const timeout = setTimeout(() => {
    dismissAlert(alert.id);
  }, getAutoDismissTime(alert.severity));
  
  return () => clearTimeout(timeout);
}, [alert]);

function getAutoDismissTime(severity: 'critical' | 'warning' | 'info'): number {
  switch (severity) {
    case 'critical': return 30000;
    case 'warning': return 15000;
    case 'info': return 10000;
  }
}
```

### 3.2 수동 제거
- **개별 제거**: 알림 우측 `[X]` 버튼
- **전체 제거**: 배너 하단 "모두 지우기" 버튼

### 3.3 영구 제거 (Persistent Dismissal)
**선택적 기능**:
- "이 알림 다시 보지 않기" 체크박스
- LocalStorage에 저장: `dismissed_alerts: string[]` (alert ID 목록)
- 서버 재시작 시에도 유지

---

## 4. 시각적 디자인 가이드라인

### 4.1 색상 시스템
```css
/* Critical (Red) */
.alert-critical {
  background: linear-gradient(90deg, #FEE2E2, #FECACA);
  border-left: 4px solid #DC2626;
  color: #7F1D1D;
}

/* Warning (Yellow) */
.alert-warning {
  background: linear-gradient(90deg, #FEF3C7, #FDE68A);
  border-left: 4px solid #F59E0B;
  color: #78350F;
}

/* Info (Blue) */
.alert-info {
  background: linear-gradient(90deg, #DBEAFE, #BFDBFE);
  border-left: 4px solid #3B82F6;
  color: #1E3A8A;
}
```

### 4.2 애니메이션
```css
/* Slide-in from top */
@keyframes slideInDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.alert-enter {
  animation: slideInDown 0.3s ease-out;
}

/* Slide-out to top */
@keyframes slideOutUp {
  from {
    transform: translateY(0);
    opacity: 1;
  }
  to {
    transform: translateY(-100%);
    opacity: 0;
  }
}

.alert-exit {
  animation: slideOutUp 0.2s ease-in;
}
```

### 4.3 Progress Bar (Auto-Dismiss Indicator)
```
┌──────────────────────────────────────────────┐
│ 🚫 NVDA 주문이 차단됨                         │
│ ──────────────────────────────────────────── │
│ ████████████░░░░░░░░░░  (12s remaining)     │
└──────────────────────────────────────────────┘
```

---

## 5. 알림 메시지 템플릿

### 5.1 Critical (차단됨)
```
🚫 {ticker} 주문이 차단됨: {owning_strategy} 전략이 소유 중 (우선순위 {priority})
🚫 {ticker} 매도 불가: 포지션이 {locked_until}까지 잠금 상태
🚫 {count}건의 주문이 차단됨: 충돌 감지 (상세보기)
```

### 5.2 Warning (소유권 이전)
```
⚠️ {ticker} 소유권 이전: {from_strategy} → {to_strategy}
⚠️ {ticker} 우선순위 오버라이드: {new_strategy}가 소유권 획득
⚠️ {count}건의 소유권이 이전됨 (상세보기)
```

### 5.3 Info (전략 상태 변경)
```
ℹ️ {strategy_name} 전략이 활성화됨
ℹ️ {strategy_name} 전략이 비활성화됨
ℹ️ {count}개 전략의 상태가 변경됨 (상세보기)
```

---

## 6. 상호작용 패턴

### 6.1 확장/축소 (Expand/Collapse)
```
Collapsed (기본):
┌────────────────────────────────────┐
│ 🚫 3건의 충돌 감지  [상세보기 ▼] │
└────────────────────────────────────┘

Expanded:
┌────────────────────────────────────┐
│ 🚫 3건의 충돌 감지  [접기 ▲]     │
├────────────────────────────────────┤
│ • NVDA: trading 차단               │
│ • AAPL: dividend 차단              │
│ • TSLA: aggressive 차단            │
└────────────────────────────────────┘
```

### 6.2 클릭 동작
- **알림 클릭**: 관련 페이지로 이동
  - Conflict → `/dashboard?filter=conflicts`
  - Ownership Transfer → `/dashboard?ticker={ticker}`
- **"상세보기" 버튼**: 알림 확장
- **"X" 버튼**: 알림 제거

---

## 7. 알림 저장소 (Store)

### 7.1 Zustand Store 구조
```typescript
interface AlertStore {
  alerts: OrderConflict[];
  addAlert: (alert: OrderConflict) => void;
  removeAlert: (id: string) => void;
  clearAll: () => void;
  dismissedIds: Set<string>; // 영구 제거된 알림
}

const useAlertStore = create<AlertStore>((set) => ({
  alerts: [],
  dismissedIds: new Set(),
  
  addAlert: (alert) => set((state) => {
    // 중복 방지
    if (state.dismissedIds.has(alert.id)) return state;
    
    // 우선순위 정렬
    const newAlerts = [...state.alerts, alert].sort((a, b) => {
      const severityOrder = { critical: 0, warning: 1, info: 2 };
      return severityOrder[a.severity] - severityOrder[b.severity];
    });
    
    return { alerts: newAlerts };
  }),
  
  removeAlert: (id) => set((state) => ({
    alerts: state.alerts.filter(a => a.id !== id)
  })),
  
  clearAll: () => set({ alerts: [] })
}));
```

---

## 8. WebSocket 통합

### 8.1 이벤트 → 알림 매핑
| WebSocket Event | Alert Severity | Alert Type |
|-----------------|----------------|------------|
| `ORDER_BLOCKED_BY_CONFLICT` | Critical | position_conflict |
| `PRIORITY_OVERRIDE` | Warning | priority_override |
| `OWNERSHIP_TRANSFERRED` | Warning | ownership_transferred |
| `STRATEGY_ACTIVATED` | Info | strategy_status |
| `STRATEGY_DEACTIVATED` | Info | strategy_status |

### 8.2 구현 예시
```typescript
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8001/api/conflicts/ws');
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    const alert: OrderConflict = {
      id: `${data.type}_${Date.now()}`,
      severity: mapSeverity(data.type),
      type: data.type,
      ticker: data.ticker,
      message: formatMessage(data),
      timestamp: new Date().toISOString()
    };
    
    addAlert(alert);
  };
  
  return () => ws.close();
}, []);
```

---

## 9. 접근성 (A11y)

### 9.1 Screen Reader 지원
```tsx
<div role="alert" aria-live="assertive" aria-atomic="true">
  <span className="sr-only">
    {severity === 'critical' ? 'Critical Alert:' : 
     severity === 'warning' ? 'Warning:' : 'Information:'}
  </span>
  {message}
</div>
```

### 9.2 키보드 네비게이션
- `Escape`: 알림 닫기
- `Enter`: 알림 상세 보기 (확장/축소)
- `Delete`: 알림 제거

---

## 10. 성능 최적화

### 10.1 알림 제한
- **최대 동시 표시**: 5개
- **최대 저장**: 최근 50개 (메모리 누수 방지)
- **그룹화**: 5초 윈도우 내 동일 ticker

### 10.2 Debouncing
```typescript
// 짧은 시간 내 중복 알림 방지
const debouncedAddAlert = useMemo(
  () => debounce((alert: OrderConflict) => {
    addAlert(alert);
  }, 500),
  []
);
```

---

## 11. 테스트 시나리오

### 11.1 Manual Test Cases
1. **Critical 알림**: 주문 차단 시뮬레이션 → 빨간색 배너, 30초 후 자동 제거
2. **Warning 알림**: 소유권 이전 → 노란색 배너, 15초 후 자동 제거
3. **그룹화**: 5초 내 NVDA 5건 차단 → "NVDA 외 X건" 표시
4. **수동 제거**: [X] 클릭 → 즉시 제거
5. **전체 제거**: "모두 지우기" → 모든 알림 제거

### 11.2 Integration Test
```typescript
describe('ConflictAlertBanner', () => {
  it('should group alerts by ticker', () => {
    const alerts = [
      { ticker: 'NVDA', ... },
      { ticker: 'NVDA', ... },
      { ticker: 'AAPL', ... }
    ];
    
    const grouped = groupAlerts(alerts);
    expect(grouped[0].count).toBe(2);
    expect(grouped[0].ticker).toBe('NVDA');
  });
  
  it('should auto-dismiss after timeout', async () => {
    render(<ConflictAlertBanner />);
    addAlert({ severity: 'info', ... });
    
    await waitFor(() => {
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    }, { timeout: 11000 });
  });
});
```

---

## 12. 다음 단계 (이미 구현 완료 ✅)

Claude Code가 이미 구현 완료:
- ✅ `ConflictAlertBanner.tsx`
- ✅ WebSocket 연결 (`ws://localhost:8001/api/conflicts/ws`)
- ✅ 자동 제거 (10초)
- ✅ 수동 제거 (X 버튼, 모두 지우기)

**향후 개선 사항** (v2):
- [ ] 알림 그룹화 (5초 윈도우)
- [ ] Progress Bar (Auto-Dismiss Indicator)
- [ ] "다시 보지 않기" 영구 제거
- [ ] 알림 히스토리 (최근 50개 보관)
