---
description: TSX/React 컴포넌트에 표준 주석 추가
---

# TSX 파일 문서화 워크플로우

이 워크플로우는 TypeScript React (TSX) 컴포넌트에 표준 주석을 추가하는 방법을 설명합니다.

## 🎯 목적

- TSX 컴포넌트의 데이터 흐름 명확화
- API 엔드포인트와 Props 관계 문서화
- 컴포넌트 재사용성 향상
- AI 도구(Cursor, Claude Code)의 코드 이해도 향상

## 📋 단계별 가이드

### 1. 파일 타입 확인

먼저 문서화할 TSX 파일의 타입을 확인:

- **페이지 컴포넌트** (`pages/`): Dashboard.tsx, Portfolio.tsx 등
- **공통 컴포넌트** (`components/common/`): Card.tsx, Button.tsx 등
- **레이아웃 컴포넌트** (`components/Layout/`): Layout.tsx, Header.tsx 등
- **기능 컴포넌트** (`components/Feature/`): DividendCalendar.tsx 등

### 2. 템플릿 선택

파일 타입에 맞는 템플릿 사용:

**기본 템플릿**:
```typescript
/**
 * ComponentName.tsx - [한 줄 설명]
 * 
 * 📊 Data Sources:
 *   - API: GET /api/endpoint (설명)
 *   - Props: 부모 컴포넌트에서 전달
 *   - State: 로컬 상태 관리
 * 
 * 🔗 Dependencies:
 *   - react-query: 데이터 페칭
 *   - lucide-react: 아이콘
 * 
 * 📤 Components Used:
 *   - Card, Button, LoadingSpinner
 * 
 * 🔄 Used By:
 *   - pages/Dashboard.tsx
 * 
 * 📝 Notes:
 *   - 특이사항
 */
```

### 3. Data Sources 작성

컴포넌트가 사용하는 모든 데이터 소스 나열:

```typescript
📊 Data Sources:
  - API: GET /api/portfolio (포트폴리오 조회)
  - API: GET /api/dividend/calendar (배당 캘린더)
  - Props: selectedDate (Date) - 부모에서 전달받는 선택된 날짜
  - State: activeTab (string) - 현재 활성 탭
  - Context: AuthContext - 사용자 인증 정보
```

### 4. Dependencies 나열

사용하는 외부 라이브러리:

```typescript
🔗 Dependencies:
  - @tanstack/react-query: useQuery, useMutation
  - lucide-react: Calendar, TrendingUp 아이콘
  - recharts: LineChart, BarChart
  - date-fns: format, addDays
```

### 5. Components Used 작성

이 컴포넌트에서 사용하는 하위 컴포넌트:

```typescript
📤 Components Used:
  - Card (common): 카드 래퍼
  - LoadingSpinner (common): 로딩 표시
  - DividendItem: 개별 배당 항목
```

### 6. Used By 파악

// turbo
이 컴포넌트를 사용하는 부모 컴포넌트 찾기:

```bash
# VSCode에서 "Find All References" 사용
# 또는 grep으로 검색
grep -r "import.*ComponentName" frontend/src
```

```typescript
🔄 Used By:
  - pages/DividendDashboard.tsx (tab: calendar)
  - pages/Portfolio.tsx (section: upcoming)
```

### 7. Notes 추가

특이사항, 성능 최적화, 알려진 이슈:

```typescript
📝 Notes:
  - 30초마다 자동 새로고침 (refetchInterval)
  - Redis 캐싱으로 성능 최적화
  - 모바일 반응형: 카드 레이아웃 변경
  - TODO: 무한 스크롤 추가 필요
```

## 📝 예시

### 공통 컴포넌트 (Card.tsx)

```typescript
/**
 * Card.tsx - 재사용 가능한 카드 컴포넌트
 * 
 * 📊 Data Sources:
 *   - Props: title, children, padding, className
 * 
 * 🔗 Dependencies:
 *   - react: HTMLAttributes
 *   - Tailwind CSS: 스타일링
 * 
 * 📤 Props:
 *   - title?: string - 카드 제목
 *   - children: ReactNode - 카드 내용
 *   - padding?: boolean (default: true)
 * 
 * 🔄 Used By:
 *   - 거의 모든 페이지와 컴포넌트
 * 
 * 📝 Notes:
 *   - 가장 많이 사용되는 공통 컴포넌트
 *   - bg-white, rounded-lg, shadow-md
 */
```

### 페이지 컴포넌트 (DividendDashboard.tsx)

```typescript
/**
 * DividendDashboard.tsx - 배당 대시보드 페이지
 * 
 * 📊 Data Sources:
 *   - API: GET /api/portfolio (배당 포함 포트폴리오)
 *   - API: GET /api/dividend/calendar (배당 캘린더)
 *   - State: activeTab, portfolio, loading
 * 
 * 🔗 Dependencies:
 *   - @tanstack/react-query: useQuery
 *   - lucide-react: DollarSign, Calendar 아이콘
 * 
 * 📤 Components Used:
 *   - Card, LoadingSpinner
 *   - DividendSummaryCards, DividendCalendar
 *   - CompoundSimulator, RiskScoreTable
 * 
 * 🔄 Used By:
 *   - App.tsx (route: /dividend)
 * 
 * 📝 Notes:
 *   - 6개 탭 (보유종목, 캘린더, DRIP, 리스크, 예수금, 귀족주)
 *   - portfolioIncome 계산: sum(dividend * quantity)
 */
```

## ✅ 체크리스트

문서화 완료 전 확인사항:

- [ ] 파일 타입 확인 (페이지/공통/기능)
- [ ] 모든 API 엔드포인트 나열
- [ ] Props 타입 명시
- [ ] 사용하는 라이브러리 나열
- [ ] 하위 컴포넌트 목록 작성
- [ ] 부모 컴포넌트 파악 (Used By)
- [ ] 특이사항, 성능 최적화 포인트 기록

## 🎯 우선순위

1. **공통 컴포넌트** (components/common/): 가장 많이 사용됨
2. **레이아웃** (components/Layout/): 전체 앱 구조
3. **주요 페이지** (pages/): 사용자 진입점
4. **기능 컴포넌트**: 필요할 때마다

---

**참조**: `.agent/coding_standards.md` - TSX 문서화 섹션
