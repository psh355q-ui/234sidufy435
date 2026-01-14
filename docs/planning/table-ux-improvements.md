# Position Ownership Table UX Improvements (T5.4)

**작성일**: 2026-01-13  
**담당**: Gemini (설계), Claude Code (구현)

---

## 1. 정렬 기능 (Sortable Columns)

### 1.1 정렬 가능한 컬럼
| Column | Sort Key | Default | Notes |
|--------|----------|---------|-------|
| Ticker | `ticker` (asc/desc) | ❌ | 알파벳순 정렬 |
| Strategy | `strategy.priority` (desc) | ❌ | 우선순위 높은 순 권장 |
| Lock Status | `locked_until` (asc/desc) | ✅ DESC | 최근 잠금 우선 |
| Created | `created_at` (desc) | ✅ DEFAULT | 최신 소유권 우선 |

### 1.2 UI 디자인
```
┌─────────────────────────────────────────────────────────┐
│ Ticker ▲  Strategy ▼  Type  Lock Status ⇅  Actions     │
│ ─────────────────────────────────────────────────────── │
│ AAPL      dividend    pri   🔒 Jan 20     [View][...] │
│ NVDA      long_term   pri   -              [View][...] │
└─────────────────────────────────────────────────────────┘
```

**정렬 인디케이터**:
- **▲**: Ascending (현재 정렬 중)
- **▼**: Descending (현재 정렬 중)
- **⇅**: Sortable (정렬 가능하지만 비활성)

**상호작용**:
- Click: Toggle `ASC ↔ DESC`
- Shift+Click: Multi-column sort (보조 정렬 키 추가)
  - 예: Strategy DESC → Ticker ASC (같은 전략 내 알파벳 순)

### 1.3 구현 가이드
```typescript
// TanStack Table 사용 예시
const columns = [
  {
    accessorKey: 'ticker',
    header: ({ column }) => (
      <SortableHeader column={column}>Ticker</SortableHeader>
    ),
    enableSorting: true,
  },
  {
    accessorKey: 'strategy.priority',
    header: 'Strategy',
    cell: ({ row }) => row.original.strategy.name,
    enableSorting: true,
    sortDescFirst: true, // 우선순위는 높은 순이 기본
  },
  {
    accessorKey: 'locked_until',
    header: 'Lock Status',
    enableSorting: true,
    sortingFn: (rowA, rowB) => {
      // null은 항상 맨 뒤로
      const a = rowA.original.locked_until;
      const b = rowB.original.locked_until;
      if (!a && !b) return 0;
      if (!a) return 1;
      if (!b) return -1;
      return new Date(a).getTime() - new Date(b).getTime();
    },
  },
];
```

---

## 2. 필터 기능

### 2.1 필터 컨트롤 UI
```
┌──────────────────────────────────────────────────────────┐
│ Filters:  [Strategy: All ▼]  [Lock Status: All ▼]  [X] │
│ ──────────────────────────────────────────────────────── │
│ Showing 15 of 42 ownerships                              │
└──────────────────────────────────────────────────────────┘
```

### 2.2 필터 옵션

#### A. 전략별 필터 (Strategy Filter)
- **Type**: Multi-select Dropdown
- **Options**:
  - `All` (default)
  - `long_term` (📈)
  - `dividend` (💰)
  - `trading` (⚡)
  - `aggressive` (🔥)
- **Behavior**: OR 조건 (여러 전략 선택 가능)

#### B. 잠금 상태별 필터 (Lock Status Filter)
- **Type**: Radio Group or Toggle Buttons
- **Options**:
  - `All` (default)
  - `🔒 Locked` - `locked_until != null AND locked_until > now()`
  - `🔓 Unlocked` - `locked_until == null OR locked_until <= now()`
- **Behavior**: Exclusive (하나만 선택)

### 2.3 고급 필터 (Optional)
- **Ticker Search**: Autocomplete input (예: "NV" → NVDA, NVAX)
- **Date Range**: Lock expiry between X and Y
- **Ownership Type**: primary vs shared

### 2.4 필터 상태 표시
```
┌──────────────────────────────────────────────────────────┐
│ Active Filters: [long_term ✕] [Locked ✕]      Clear All │
└──────────────────────────────────────────────────────────┘
```

**UX 개선**:
- 활성 필터를 Chip/Badge로 표시
- 각 Chip에 `✕` 버튼 → 개별 제거
- `Clear All` 버튼 → 모든 필터 초기화

### 2.5 URL Query Params 동기화
```
/dashboard?strategy=long_term,dividend&lock_status=locked&page=2
```
**이점**:
- 북마크 가능
- 뒤로가기/앞으로가기 동작
- 공유 가능한 필터 상태

---

## 3. 색상 코딩 (Color Coding)

### 3.1 잠금 상태 색상
| Status | Color | Tailwind Class | Icon | Usage |
|--------|-------|----------------|------|-------|
| **Locked** | 🔴 Red | `bg-red-50 border-red-300 text-red-700` | 🔒 | Row background (subtle), Icon (bold) |
| **Unlocked** | 🟢 Green | `bg-green-50 border-green-300 text-green-700` | 🔓 | Row background (subtle), Icon (bold) |
| **Expiring Soon** | 🟡 Yellow | `bg-yellow-50 border-yellow-300 text-yellow-700` | ⏱️ | locked_until < 24h |

### 3.2 전략별 색상 (Strategy Badges)
| Strategy | Color | Tailwind Class |
|----------|-------|----------------|
| long_term | Blue | `bg-blue-100 text-blue-800` |
| dividend | Purple | `bg-purple-100 text-purple-800` |
| trading | Orange | `bg-orange-100 text-orange-800` |
| aggressive | Red | `bg-red-100 text-red-800` |

### 3.3 적용 예시
```tsx
// Row 배경 색상
<tr className={cn(
  "hover:bg-gray-50",
  isLocked && "bg-red-50 border-l-4 border-l-red-500",
  !isLocked && "bg-green-50 border-l-4 border-l-green-500"
)}>
  
  {/* Lock Status Cell */}
  <td className="px-4 py-2">
    {isLocked ? (
      <div className="flex items-center gap-2 text-red-700">
        <Lock size={16} />
        <span className="text-sm">{formatDate(locked_until)}</span>
      </div>
    ) : (
      <div className="flex items-center gap-2 text-green-700">
        <Unlock size={16} />
        <span className="text-sm">Unlocked</span>
      </div>
    )}
  </td>
  
  {/* Strategy Badge */}
  <td>
    <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-medium">
      📈 {strategy.name}
    </span>
  </td>
</tr>
```

### 3.4 접근성 고려 (A11y)
- **색맹 대응**: 색상 + 아이콘 조합 사용 (색상만 의존 ❌)
- **대비율**: WCAG AA 준수 (4.5:1 최소)
- **Screen Reader**: 
  - `aria-label="Locked until January 20, 3:45 PM"`
  - `<VisuallyHidden>Status: Locked</VisuallyHidden>`

---

## 4. 상호작용 패턴

### 4.1 Hover States
```
Default:       bg-white
Hover:         bg-gray-50
Active (Click): bg-gray-100
```

### 4.2 선택 기능 (Optional)
- **Checkbox**: 행 선택 → 일괄 작업 (Bulk Release, Bulk Transfer)
- **Shift+Click**: 범위 선택 (Row 5 → Shift+Click Row 10 = 5~10 선택)

### 4.3 컨텍스트 메뉴 (Right-Click)
```
┌─────────────────┐
│ View Details    │
│ Release         │
│ Transfer to...  │
│ ──────────────  │
│ Copy Ticker     │
└─────────────────┘
```

---

## 5. 반응형 디자인

### 5.1 Desktop (>1024px)
- 모든 컬럼 표시
- Sticky header (스크롤 시 헤더 고정)

### 5.2 Tablet (768px - 1024px)
- `Type` 컬럼 숨김 (Badge로 통합)
- Actions를 Dropdown으로 축소

### 5.3 Mobile (<768px)
- **Card View**로 전환 (테이블 → 카드 리스트)
```
┌──────────────────────────┐
│ NVDA                     │
│ 📈 long_term (Priority 100) │
│ 🔓 Unlocked              │
│ [View] [Release]         │
└──────────────────────────┘
```

---

## 6. 성능 최적화

### 6.1 Virtual Scrolling
- 100+ rows 시 `react-window` 적용
- 가시 영역만 렌더링 (성능 10배 개선)

### 6.2 Pagination 전략
- **Client-side**: 데이터 < 500개
- **Server-side**: 데이터 > 500개 (현재 API 지원됨)

---

## 7. 에러 상태 & 빈 상태

### 7.1 Empty State (No Ownerships)
```
┌─────────────────────────────────┐
│         📭                      │
│   No Position Ownerships        │
│                                 │
│   Create your first ownership   │
│   by executing a trade.         │
│                                 │
│   [Learn More]                  │
└─────────────────────────────────┘
```

### 7.2 Filter No Results
```
┌─────────────────────────────────┐
│         🔍                      │
│   No Results Found              │
│                                 │
│   Try adjusting your filters    │
│   [Clear Filters]               │
└─────────────────────────────────┘
```

---

## 8. 구현 체크리스트

### Must-Have (MVP)
- [x] Sortable: ticker, locked_until
- [x] Filter: Strategy dropdown
- [x] Color: Locked (red) vs Unlocked (green)
- [x] Pagination (server-side)

### Nice-to-Have (v2)
- [ ] Multi-column sort (Shift+Click)
- [ ] Lock Status filter (toggle)
- [ ] Ticker autocomplete search
- [ ] Bulk selection + actions
- [ ] Virtual scrolling (>100 rows)
- [ ] Export to CSV

---

## 9. 다음 단계 (Claude Code)

1. **TanStack Table 설정**: `@tanstack/react-table` 설치
2. **컴포넌트 구현**: `PositionOwnershipTable.tsx`
3. **필터 상태 관리**: URL Query Params (`useSearchParams`)
4. **색상 시스템**: Tailwind 클래스 통일
5. **Storybook**: Interactive Component Demo
