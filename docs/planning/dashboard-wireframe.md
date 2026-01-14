# Multi-Strategy Dashboard UI Wireframe (T5.3)

**작성일**: 2026-01-13  
**담당**: Gemini (설계), Claude Code (구현)

---

## 1. 레이아웃 구조 (3단 구성)

### 1.1 전체 구조 (Desktop)
```
┌────────────────────────────────────────────────────────────────────┐
│ Header: Multi-Strategy Orchestrator                    [User] [⚙️] │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │  🚨 Conflict Alert Banner (Collapsible)                      │ │
│ │  ⚠️ 2 conflicts detected: NVDA blocked (trading), ...       │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌─────── Strategy Cards (Grid: 4 columns) ──────────────────────┐ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │ │
│ │ │ 📈 Long  │ │ 💰 Div   │ │ ⚡ Trade │ │ 🔥 Aggr  │         │ │
│ │ │ Priority │ │ Priority │ │ Priority │ │ Priority │         │ │
│ │ │   100    │ │    90    │ │    50    │ │    30    │         │ │
│ │ │──────────│ │──────────│ │──────────│ │──────────│         │ │
│ │ │ Active   │ │ Active   │ │ Inactive │ │ Active   │         │ │
│ │ │ 5 Pos    │ │ 3 Pos    │ │ 0 Pos    │ │ 2 Pos    │         │ │
│ │ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌─────── Position Ownership Table ──────────────────────────────┐ │
│ │ Ticker  Strategy    Type     Locked Until    Actions          │ │
│ │ ──────────────────────────────────────────────────────────── │ │
│ │ NVDA    long_term   primary  -               [View] [Release]│ │
│ │ AAPL    dividend    primary  2026-01-20      🔒 [View]       │ │
│ │ TSLA    aggressive  primary  -               [View] [Release]│ │
│ │                                                                │ │
│ │                                    [Prev] Page 1/3 [Next]     │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 1.2 반응형 구조 (Mobile)
```
┌──────────────────────┐
│ Multi-Strategy [☰]  │
├──────────────────────┤
│ 🚨 2 Conflicts       │
├──────────────────────┤
│ ┌──────────────────┐ │
│ │ 📈 Long (100)    │ │
│ │ Active, 5 Pos    │ │
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │ 💰 Div (90)      │ │
│ │ Active, 3 Pos    │ │
│ └──────────────────┘ │
│ ...                  │
├──────────────────────┤
│ [Positions Table ▼]  │
│ Swipeable horizontal │
└──────────────────────┘
```

---

## 2. 컴포넌트 계층 구조

```
StrategyDashboard (Page Component)
├─ ConflictAlertBanner
│  ├─ AlertItem (repeatable)
│  └─ DismissButton
│
├─ StrategyCardGrid
│  └─ StrategyCard (4x)
│     ├─ StrategyHeader (Persona Icon, Name, Priority)
│     ├─ StrategyStats (Active, Position Count)
│     └─ QuickActions (Activate/Deactivate Toggle)
│
└─ PositionOwnershipTable
   ├─ TableHeader (Sortable Columns)
   ├─ TableRow (repeatable)
   │  ├─ TickerCell (Link to Position Detail)
   │  ├─ StrategyCell (Colored Badge)
   │  ├─ TypeCell (primary/shared)
   │  ├─ LockStatusCell (🔒 Icon + Date)
   │  └─ ActionsCell (View/Release/Transfer Buttons)
   └─ Pagination (Page 1/N, Prev/Next)
```

---

## 3. 상태 관리 전략

### 3.1 추천: **React Query** (with Zustand 보조)

**React Query 사용 이유**:
1. **Server State 관리**: 전략, 소유권 데이터는 서버 상태이므로 React Query의 캐싱, refetching, invalidation이 적합
2. **자동 Re-fetch**: `refetchInterval: 3000` 설정으로 실시간성 확보
3. **Optimistic Updates**: 전략 활성화/비활성화 시 즉각 UI 반영 후 서버 동기화

**Zustand 사용 범위** (보조):
1. **UI State**: Alert 배너 접힘/펼침 상태
2. **Filter State**: 테이블 필터 (ticker, strategy) - URL Query Params와 동기화 권장

### 3.2 데이터 플로우
```
[API] ─────> [React Query Cache] ─────> [Component]
                    ▲                         │
                    │ refetch(3s)             │ mutation
                    └─────────────────────────┘
                    
[WebSocket] ─────> [Event Handler] ─────> queryClient.invalidateQueries()
```

---

## 4. 실시간 업데이트 전략

### 4.1 추천: **Hybrid (Polling + WebSocket)**

#### A. Polling (Primary)
- **전략 목록**: `refetchInterval: 30000` (30초) - 변화가 드뭄
- **소유권 목록**: `refetchInterval: 3000` (3초) - API 캐시와 조화

#### B. WebSocket (Event-Driven)
WebSocket으로 다음 이벤트 수신 시 즉시 query invalidate:
1. `OWNERSHIP_TRANSFERRED` → `invalidateQueries(['ownerships'])`
2. `CONFLICT_DETECTED` → Alert 배너 업데이트
3. `ORDER_BLOCKED_BY_CONFLICT` → Alert 배너에 추가

**구현 예시**:
```typescript
// React Query 설정
const { data: strategies } = useQuery({
  queryKey: ['strategies'],
  queryFn: fetchStrategies,
  refetchInterval: 30000
});

const { data: ownerships } = useQuery({
  queryKey: ['ownerships', filters],
  queryFn: () => fetchOwnerships(filters),
  refetchInterval: 3000
});

// WebSocket 리스너
useEffect(() => {
  const ws = connectWebSocket();
  
  ws.on('OWNERSHIP_TRANSFERRED', (event) => {
    queryClient.invalidateQueries(['ownerships']);
    showToast(`${event.ticker} transferred to ${event.to_strategy}`);
  });
  
  ws.on('CONFLICT_DETECTED', (event) => {
    // Zustand store에 alert 추가
    addConflictAlert(event);
  });
  
  return () => ws.close();
}, []);
```

---

## 5. 컴포넌트 상세 설계

### 5.1 StrategyCard
**Props**:
- `strategy: StrategyResponse`

**UI 요소**:
- Persona Icon (long_term=📈, dividend=💰, trading=⚡, aggressive=🔥)
- Priority Badge (color-coded: >80=green, 50-80=yellow, <50=orange)
- Active Toggle (Switch 컴포넌트)
- Position Count (Clickable → Filter positions by strategy)

**Interaction**:
- Click Card → Navigate to `/strategies/{id}`
- Toggle Active → `useMutation` (POST /strategies/{id}/activate)

### 5.2 PositionOwnershipTable
**Props**:
- `filters: { ticker?, strategy_id? }`
- `page: number`

**Features**:
- Sortable Columns (default: `created_at DESC`)
- Lock Status: 🔒 icon + formatted date (e.g., "Jan 20, 3:45 PM")
- Color-coded Strategy Badges (각 전략마다 고유 색상)
- Actions:
  - **View**: Modal → Position Detail
  - **Release**: Confirm → DELETE /ownership/{id}
  - **Transfer**: Modal → Select target strategy → POST /ownership/transfer

### 5.3 ConflictAlertBanner
**Props**:
- `conflicts: ConflictEvent[]` (from Zustand or React Query)

**UI**:
- Collapsible (클릭 시 펼침/접힘)
- Severity Color: `ERROR` (red), `WARNING` (yellow)
- Each Alert Item:
  - Icon (⚠️ or 🚫)
  - Message: `"{ticker} blocked by {strategy}: {reasoning}"`
  - Timestamp: "2 mins ago"
  - Dismiss Button (X)

---

## 6. 기술 스택 추천

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| State Management | React Query + Zustand | Server state (RQ) + UI state (Zustand) |
| Styling | Tailwind CSS | 프로젝트 기존 스타일 일관성 |
| Icons | Lucide React | 경량 + Tree-shakeable |
| Tables | TanStack Table | 정렬, 필터, 페이지네이션 내장 |
| WebSocket | Socket.io-client | Event-based updates |
| Routing | React Router v6 | 기존 프로젝트 의존성 |

---

## 7. 파일 구조 (제안)

```
frontend/src/
├── pages/
│   └── StrategyDashboard.tsx         # Main page
├── components/
│   ├── strategy/
│   │   ├── StrategyCard.tsx
│   │   └── StrategyCardGrid.tsx
│   ├── ownership/
│   │   ├── PositionOwnershipTable.tsx
│   │   └── OwnershipActions.tsx
│   └── alerts/
│       ├── ConflictAlertBanner.tsx
│       └── AlertItem.tsx
├── hooks/
│   ├── useStrategies.ts              # React Query hook
│   ├── useOwnerships.ts
│   └── useConflictAlerts.ts
├── stores/
│   └── alertStore.ts                 # Zustand
└── services/
    └── websocket.ts                  # WebSocket connection
```

---

## 8. 접근성 (A11y) 고려사항

1. **Keyboard Navigation**: 모든 Interactive 요소 Tab 지원
2. **Screen Reader**: 
   - Lock Icon: `aria-label="Locked until Jan 20"`
   - Priority Badge: `aria-label="Priority 100, Highest"`
3. **Color Contrast**: WCAG AA 준수 (배지, 버튼)
4. **Focus Indicators**: 키보드 포커스 시 outline 명확

---

## 9. 성능 최적화

1. **Virtual Scrolling**: 소유권 테이블이 100+ 항목 시 `react-window` 적용
2. **Memoization**: 
   - Strategy Cards: `React.memo` + `useMemo` (persona icon 계산)
   - Table Rows: `React.memo` (props 변경 시만 re-render)
3. **Code Splitting**: `React.lazy(() => import('./StrategyDashboard'))`

---

## 10. 다음 단계 (Claude Code)

1. **구현 순서**:
   1. `StrategyCard` + `StrategyCardGrid` (T5.3)
   2. `PositionOwnershipTable` (T5.4)
   3. `ConflictAlertBanner` (T5.5)
   4. WebSocket 통합
2. **Mock Data**: 초기 구현 시 `/api/v1/strategies`, `/api/v1/positions/ownership` mock 응답 사용
3. **Storybook**: 각 컴포넌트별 스토리 작성 (권장)
