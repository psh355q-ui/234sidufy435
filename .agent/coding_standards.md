# AI Trading System - Coding Standards

## 📋 목적
AI 에이전트의 효율적인 코드 분석을 위해 모든 코드 파일에 명확한 메타데이터와 주석을 포함합니다.

## 🔧 Python 파일 표준

### 1. 파일 헤더 주석 (필수)
모든 `.py` 파일 상단에 다음 정보를 포함해야 합니다:

```python
"""
[파일명] - [간단한 설명]

📊 Data Sources:
    - KIS API: 포트폴리오 데이터, 잔고 조회
    - Yahoo Finance: 배당 정보, 섹터 정보
    - PostgreSQL: [테이블명] - [용도]

🔗 External Dependencies:
    - yfinance: 주식 데이터 조회
    - requests: HTTP 통신
    - pandas: 데이터 처리

📤 API Endpoints (if applicable):
    - GET /api/portfolio: 포트폴리오 조회
    - POST /api/rebalance: 리밸런싱 실행

🔄 Called By:
    - frontend/src/pages/Portfolio.tsx
    - backend/services/portfolio_scheduler.py

📝 Notes:
    - 특이사항이나 중요한 비즈니스 로직 설명
"""
```

### 2. 함수/클래스 Docstring
모든 public 함수와 클래스에 다음을 포함:

```python
def get_portfolio_data(account_no: str) -> Dict:
    """
    포트폴리오 데이터 조회
    
    Data Source: KIS API → /account/balance
    Fallback: Yahoo Finance (배당 정보)
    
    Args:
        account_no: 계좌번호 (예: "12345678-01")
        
    Returns:
        Dict: {
            "total_value": float,
            "positions": List[Dict],
            "cash": float
        }
        
    Raises:
        HTTPException: KIS API 인증 실패 시
    """
```

### 3. 중요 변수 주석

```python
# Data Source: KIS API response.body.output1
positions = balance.get("positions", [])

# Calculated from: current_price - avg_price
profit_loss = pos.get("profit_loss", 0)

# External API: Yahoo Finance ticker.info['sector']
sector = yf.get_stock_sector(symbol)
```

---

## 📱 TypeScript/React (TSX) 파일 표준

### TSX 표준 템플릿

```typescript
/**
 * ComponentName.tsx - [한 줄 설명]
 * 
 * 📊 Data Sources:
 *   - API: GET /api/endpoint (설명)
 *   - Props: ParentComponent에서 전달받는 데이터
 *   - State: useState로 관리하는 로컬 상태
 *   - Context: useContext로 가져오는 전역 상태
 * 
 * 🔗 Dependencies:
 *   - react-query: 서버 상태 관리
 *   - lucide-react: 아이콘 라이브러리
 *   - recharts: 차트 라이브러리
 *   - @tanstack/react-query: 데이터 페칭
 * 
 * 📤 Components Used:
 *   - Card, Button, LoadingSpinner (공통 컴포넌트)
 *   - SpecificComponent (기능별 컴포넌트)
 * 
 * 🔄 Used By:
 *   - pages/Dashboard.tsx
 *   - pages/Portfolio.tsx
 *   - components/ParentComponent.tsx
 * 
 * 📝 Notes:
 *   - 특이사항, 주의사항
 *   - 성능 최적화 포인트
 *   - 알려진 이슈
 */
```

### TSX 파일별 가이드

#### 1. 페이지 컴포넌트 (pages/)

```typescript
/**
 * Dashboard.tsx - 대시보드 메인 페이지
 * 
 * 📊 Data Sources:
 *   - API: GET /api/portfolio (포트폴리오 데이터)
 *   - API: GET /api/signals (트레이딩 시그널)
 *   - State: activeTab, filters
 * 
 * 🔗 Dependencies:
 *   - react-query: useQuery
 *   - recharts: LineChart, BarChart
 * 
 * 📤 Components Used:
 *   - Card, PortfolioSummary, SignalsList
 * 
 * 🔄 Used By:
 *   - App.tsx (route: /dashboard)
 * 
 * 📝 Notes:
 *   - 30초마다 자동 새로고침
 *   - 모바일 반응형 레이아웃
 */
```

#### 2. 공통 컴포넌트 (components/common/)

```typescript
/**
 * Card.tsx - 재사용 가능한 카드 컴포넌트
 * 
 * 📊 Data Sources:
 *   - Props: title, children, className
 * 
 * 🔗 Dependencies:
 *   - Tailwind CSS
 * 
 * 📤 Props:
 *   - title?: string
 *   - children: ReactNode
 *   - padding?: boolean
 * 
 * 🔄 Used By:
 *   - 거의 모든 페이지와 컴포넌트
 * 
 * 📝 Notes:
 *   - 가장 많이 사용되는 공통 컴포넌트
 */
```

#### 3. 기능 컴포넌트 (components/Feature/)

```typescript
/**
 * DividendCalendar.tsx - 배당 캘린더
 * 
 * 📊 Data Sources:
 *   - API: GET /api/dividend/calendar
 *   - Props: selectedDate
 * 
 * 🔗 Dependencies:
 *   - react-query
 *   - date-fns: 날짜 포맷팅
 * 
 * 📤 Components Used:
 *   - Card, Calendar, DividendItem
 * 
 * 🔄 Used By:
 *   - pages/DividendDashboard.tsx
 * 
 * 📝 Notes:
 *   - 월별/주별 뷰 전환 가능
 */
```

### TSX 문서화 체크리스트

- [ ] **Data Sources**: API 엔드포인트, Props, State 명시
- [ ] **Dependencies**: 사용하는 라이브러리 나열
- [ ] **Components Used**: import한 컴포넌트 목록
- [ ] **Used By**: 이 컴포넌트를 사용하는 부모 컴포넌트
- [ ] **Notes**: 특이사항, 성능 최적화, 알려진 이슈

### TSX 우선순위

1. **공통 컴포넌트** (components/common/): Card, Button, LoadingSpinner
2. **레이아웃 컴포넌트** (components/Layout/): Layout, Header, Sidebar
3. **주요 페이지** (pages/): Dashboard, Portfolio, DividendDashboard
4. **기능별 컴포넌트**: 필요할 때마다

---

## 🚀 자동화 도구

### 주석 검증 스크립트
```bash
# 주석이 없는 파일 찾기
python scripts/check_docstrings.py

# 자동 주석 템플릿 생성
python scripts/generate_docstring_template.py <filename>
```

## ✅ 체크리스트

코드 커밋 전:
- [ ] 파일 헤더에 Data Sources 명시
- [ ] External Dependencies 문서화
- [ ] Public 함수에 docstring 작성
- [ ] API 호출하는 곳에 endpoint 주석
- [ ] 복잡한 로직에 설명 주석

## 📌 예시: 좋은 주석 vs 나쁜 주석

### ❌ 나쁜 예
```python
# Get portfolio
def get_portfolio():
    data = api.call()
    return data
```

### ✅ 좋은 예
```python
"""
포트폴리오 조회
Data Source: KIS API /account/balance (TTTS3012R)
"""
def get_portfolio(account_no: str) -> PortfolioResponse:
    # KIS API 호출: 해외주식 잔고 조회
    balance = kis.overseas_stock.get_balance(account_no, "NASD")
    
    # Response format: {positions: [...], cash: float}
    return balance
```

## 성공적인 AI 분석을 위한 핵심 원칙

1. **데이터 소스를 명확히** - 어디서 데이터가 오는지
2. **의존성을 나열** - 어떤 라이브러리/모듈을 사용하는지
3. **사용 관계를 표시** - 이 파일을 누가 사용하는지
4. **간결하게 작성** - 핵심만, 불필요한 설명 제거

---

## 🔄 Workflows

- `/add-docstrings` - Python 파일에 표준 주석 추가 (.agent/workflows/add-docstrings.md)
- `/add-tsx-docs` - TSX 파일에 표준 주석 추가 (.agent/workflows/add-tsx-docs.md)

## 🔄 업데이트 이력
- 2025-12-25: TSX 문서화 표준 추가
- 2025-12-25: 초안 작성 - 데이터 소스 명시 표준 정의
