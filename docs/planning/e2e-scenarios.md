# E2E Test Scenarios (T5.6)

**작성일**: 2026-01-13  
**담당**: Gemini (설계), Claude Code (구현)  
**도구**: Playwright

---

## 1. 사용자 플로우 시나리오

### Scenario 1: 정상 플로우 - 충돌 없는 주문
```typescript
test('should allow order when no conflict exists', async ({ page }) => {
  // 1. 로그인
  await page.goto('http://localhost:3002/login');
  await page.fill('[name="username"]', 'test_user');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // 2. 전략 대시보드 접속
  await page.waitForURL('**/strategies');
  await expect(page.locator('h1')).toContainText('Multi-Strategy Dashboard');
  
  // 3. 전략 확인 (long_term이 활성화됨)
  const longTermCard = page.locator('[data-testid="strategy-card-long_term"]');
  await expect(longTermCard).toBeVisible();
  await expect(longTermCard.locator('[data-testid="status"]')).toContainText('Active');
  
  // 4. 주문 생성 (MSFT - 소유권 없음)
  await page.goto('http://localhost:3002/orders/new');
  await page.selectOption('[name="strategy"]', 'long_term');
  await page.fill('[name="ticker"]', 'MSFT');
  await page.selectOption('[name="action"]', 'buy');
  await page.fill('[name="quantity"]', '10');
  await page.click('button[type="submit"]');
  
  // 5. 성공 확인
  await expect(page.locator('.toast-success')).toContainText('Order created successfully');
  
  // 6. 소유권 테이블 확인
  await page.goto('http://localhost:3002/strategies');
  const ownershipTable = page.locator('[data-testid="ownership-table"]');
  await expect(ownershipTable.locator('tr:has-text("MSFT")')).toBeVisible();
});
```

---

### Scenario 2: 충돌 감지 및 차단
```typescript
test('should block order due to conflict', async ({ page }) => {
  // Setup: NVDA는 long_term(priority=100)이 소유 중
  await setupOwnership({ ticker: 'NVDA', strategy: 'long_term' });
  
  // 1. 로그인
  await loginAsUser(page, 'test_user');
  
  // 2. 전략 대시보드 접속
  await page.goto('http://localhost:3002/strategies');
  
  // 3. 소유권 확인
  const ownershipRow = page.locator('tr:has-text("NVDA")');
  await expect(ownershipRow.locator('td:nth-child(2)')).toContainText('long_term');
  
  // 4. 단기 전략(trading, priority=50)으로 NVDA 매도 시도
  await page.goto('http://localhost:3002/orders/new');
  await page.selectOption('[name="strategy"]', 'trading');
  await page.fill('[name="ticker"]', 'NVDA');
  await page.selectOption('[name="action"]', 'sell');
  await page.fill('[name="quantity"]', '5');
  await page.click('button[type="submit"]');
  
  // 5. 충돌 경고 확인 (WebSocket Alert)
  const alertBanner = page.locator('[data-testid="conflict-alert-banner"]');
  await expect(alertBanner).toBeVisible({ timeout: 5000 });
  await expect(alertBanner).toContainText('NVDA');
  await expect(alertBanner).toContainText('blocked');
  
  // 6. 주문 차단 확인
  await expect(page.locator('.toast-error')).toContainText('Order blocked');
  
  // 7. 주문 테이블에서 REJECTED 상태 확인
  await page.goto('http://localhost:3002/orders');
  const orderRow = page.locator('tr').filter({ hasText: 'NVDA' }).first();
  await expect(orderRow.locator('td:has-text("REJECTED")')).toBeVisible();
});
```

---

### Scenario 3: 우선순위 오버라이드 (Priority Override)
```typescript
test('should transfer ownership on priority override', async ({ page }) => {
  // Setup: AAPL은 trading(priority=50)이 소유 중
  await setupOwnership({ ticker: 'AAPL', strategy: 'trading' });
  
  await loginAsUser(page, 'test_user');
  
  // 1. long_term(priority=100)으로 AAPL 매수 시도
  await page.goto('http://localhost:3002/orders/new');
  await page.selectOption('[name="strategy"]', 'long_term');
  await page.fill('[name="ticker"]', 'AAPL');
  await page.selectOption('[name="action"]', 'buy');
  await page.fill('[name="quantity"]', '10');
  await page.click('button[type="submit"]');
  
  // 2. 소유권 이전 경고 (Warning)
  const alertBanner = page.locator('[data-testid="conflict-alert-banner"]');
  await expect(alertBanner).toBeVisible({ timeout: 5000 });
  await expect(alertBanner).toContainText('Ownership transferred');
  await expect(alertBanner).toHaveClass(/alert-warning/);
  
  // 3. 주문 성공 확인
  await expect(page.locator('.toast-success')).toContainText('Order created');
  
  // 4. 소유권 테이블에서 변경 확인
  await page.goto('http://localhost:3002/strategies');
  const ownershipRow = page.locator('tr:has-text("AAPL")');
  await expect(ownershipRow.locator('td').filter({ hasText: 'long_term' })).toBeVisible();
});
```

---

## 2. Edge Case 시나리오

### Edge Case 1: 네트워크 지연 (Slow Network)
```typescript
test('should handle slow API response gracefully', async ({ page, context }) => {
  // API 응답 지연 시뮬레이션 (3초)
  await context.route('**/api/v1/positions/ownership**', async (route) => {
    await new Promise(resolve => setTimeout(resolve, 3000));
    await route.continue();
  });
  
  await loginAsUser(page, 'test_user');
  await page.goto('http://localhost:3002/strategies');
  
  // 1. 로딩 인디케이터 확인
  await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();
  
  // 2. 3초 후 데이터 표시
  await expect(page.locator('[data-testid="ownership-table"]')).toBeVisible({ timeout: 5000 });
  
  // 3. 로딩 인디케이터 사라짐
  await expect(page.locator('[data-testid="loading-spinner"]')).not.toBeVisible();
});
```

---

### Edge Case 2: API 타임아웃 (Timeout)
```typescript
test('should show error on API timeout', async ({ page, context }) => {
  // API 타임아웃 시뮬레이션 (30초 대기 → 실패)
  await context.route('**/api/v1/strategies**', async (route) => {
    await new Promise(resolve => setTimeout(resolve, 30000));
    await route.abort('timedout');
  });
  
  await loginAsUser(page, 'test_user');
  await page.goto('http://localhost:3002/strategies');
  
  // 1. 에러 메시지 표시
  await expect(page.locator('[data-testid="error-message"]')).toBeVisible({ timeout: 35000 });
  await expect(page.locator('[data-testid="error-message"]')).toContainText('Failed to load strategies');
  
  // 2. 재시도 버튼 확인
  await expect(page.locator('button:has-text("Retry")')).toBeVisible();
});
```

---

### Edge Case 3: WebSocket 연결 끊김
```typescript
test('should reconnect WebSocket on disconnect', async ({ page }) => {
  await loginAsUser(page, 'test_user');
  await page.goto('http://localhost:3002/strategies');
  
  // 1. WebSocket 연결 확인 (연결 상태 인디케이터)
  await expect(page.locator('[data-testid="ws-status"]')).toContainText('Connected');
  
  // 2. WebSocket 연결 강제 종료
  await page.evaluate(() => {
    // @ts-ignore
    window.__wsConnection?.close();
  });
  
  // 3. 재연결 시도 표시
  await expect(page.locator('[data-testid="ws-status"]')).toContainText('Reconnecting...', { timeout: 2000 });
  
  // 4. 재연결 성공 (5초 이내)
  await expect(page.locator('[data-testid="ws-status"]')).toContainText('Connected', { timeout: 7000 });
});
```

---

### Edge Case 4: 동시 주문 생성 (Race Condition)
```typescript
test('should handle concurrent order creation correctly', async ({ browser }) => {
  // 2개의 병렬 세션 생성
  const context1 = await browser.newContext();
  const context2 = await browser.newContext();
  
  const page1 = await context1.newPage();
  const page2 = await context2.newPage();
  
  await loginAsUser(page1, 'user1');
  await loginAsUser(page2, 'user2');
  
  // 동시에 같은 종목(TSLA) 주문 생성
  await Promise.all([
    createOrder(page1, { strategy: 'long_term', ticker: 'TSLA', action: 'buy', quantity: 10 }),
    createOrder(page2, { strategy: 'trading', ticker: 'TSLA', action: 'buy', quantity: 5 })
  ]);
  
  // 1. 하나는 성공, 하나는 차단되어야 함
  const page1Success = await page1.locator('.toast-success').isVisible();
  const page2Success = await page2.locator('.toast-success').isVisible();
  
  expect(page1Success || page2Success).toBeTruthy();
  expect(page1Success && page2Success).toBeFalsy(); // 둘 다 성공하면 안됨
  
  // 2. 소유권은 하나만 존재
  await page1.goto('http://localhost:3002/strategies');
  const tslaRows = page1.locator('tr:has-text("TSLA")');
  await expect(tslaRows).toHaveCount(1);
});
```

---

## 3. 테스트 데이터 Setup

### Fixtures
```typescript
// tests/fixtures/multi-strategy.ts
export async function setupStrategies(db) {
  await db.exec(`
    INSERT INTO strategies (id, name, display_name, persona_type, priority, time_horizon, is_active)
    VALUES 
      ('test-long', 'long_term', '장기 투자', 'long_term', 100, 'long', true),
      ('test-div', 'dividend', '배당 투자', 'dividend', 90, 'medium', true),
      ('test-trade', 'trading', '단기 트레이딩', 'trading', 50, 'short', true),
      ('test-aggr', 'aggressive', '공격적 투자', 'aggressive', 30, 'short', true);
  `);
}

export async function setupOwnership(db, { ticker, strategy }) {
  await db.exec(`
    INSERT INTO position_ownership (id, strategy_id, ticker, ownership_type, created_at)
    VALUES ('${uuid()}', '${strategy}', '${ticker}', 'primary', NOW());
  `);
}

export async function cleanupTestData(db) {
  await db.exec(`
    DELETE FROM position_ownership WHERE id LIKE 'test-%';
    DELETE FROM orders WHERE id LIKE 'test-%';
    DELETE FROM conflict_logs WHERE id LIKE 'test-%';
    DELETE FROM strategies WHERE id LIKE 'test-%';
  `);
}
```

---

## 4. Assertion 체크리스트

### UI Assertions
- [ ] 전략 카드 표시 (4개)
- [ ] 각 전략의 Active 상태 토글
- [ ] 소유권 테이블 로딩 및 페이지네이션
- [ ] 충돌 알림 배너 표시 (색상, 아이콘, 메시지)
- [ ] 알림 자동 제거 (10초)
- [ ] 수동 제거 (X 버튼)

### API Assertions
- [ ] GET /api/v1/strategies → 200 OK
- [ ] GET /api/v1/positions/ownership → 200 OK (페이지네이션)
- [ ] POST /api/v1/orders → 201 Created (성공 케이스)
- [ ] POST /api/v1/orders → 409 Conflict (충돌 케이스)
- [ ] WebSocket /api/conflicts/ws → 연결됨

### Database Assertions
```typescript
test('should persist ownership in database', async ({ page }) => {
  // ... 주문 생성

  // DB 상태 확인
  const ownership = await db.query(`
    SELECT * FROM position_ownership 
    WHERE ticker = 'NVDA' AND strategy_id = 'long_term'
  `);
  
  expect(ownership.rows).toHaveLength(1);
  expect(ownership.rows[0].ownership_type).toBe('primary');
});
```

---

## 5. 성능 테스트 시나리오

### Scenario: 대량 소유권 조회
```typescript
test('should load 100+ ownerships with pagination', async ({ page }) => {
  // Setup: 150개 소유권 생성
  await setupBulkOwnerships(db, 150);
  
  await loginAsUser(page, 'test_user');
  await page.goto('http://localhost:3002/strategies');
  
  // 1. 첫 페이지 (20개) 로딩 시간 측정
  const startTime = Date.now();
  await expect(page.locator('tr[data-testid^="ownership-row-"]')).toHaveCount(20);
  const loadTime = Date.now() - startTime;
  
  expect(loadTime).toBeLessThan(2000); // 2초 이내
  
  // 2. 페이지네이션 확인
  await expect(page.locator('[data-testid="pagination"]')).toContainText('Page 1 of 8');
  
  // 3. 다음 페이지 이동
  await page.click('[data-testid="next-page"]');
  await expect(page.locator('[data-testid="pagination"]')).toContainText('Page 2 of 8');
});
```

---

## 6. 접근성 (A11y) 테스트

```typescript
import { injectAxe, checkA11y } from 'axe-playwright';

test('should have no accessibility violations', async ({ page }) => {
  await loginAsUser(page, 'test_user');
  await page.goto('http://localhost:3002/strategies');
  
  await injectAxe(page);
  await checkA11y(page, null, {
    detailedReport: true,
    detailedReportOptions: {
      html: true
    }
  });
});
```

---

## 7. 모바일 반응형 테스트

```typescript
test.use({ viewport: { width: 375, height: 667 } }); // iPhone SE

test('should display mobile layout correctly', async ({ page }) => {
  await loginAsUser(page, 'test_user');
  await page.goto('http://localhost:3002/strategies');
  
  // 1. 전략 카드: Grid → Stack
  const cardGrid = page.locator('[data-testid="strategy-card-grid"]');
  await expect(cardGrid).toHaveCSS('flex-direction', 'column');
  
  // 2. 테이블 → Card View
  const ownershipCards = page.locator('[data-testid^="ownership-card-"]');
  await expect(ownershipCards.first()).toBeVisible();
  
  // 3. 테이블은 숨김
  await expect(page.locator('[data-testid="ownership-table"]')).not.toBeVisible();
});
```

---

## 8. 실행 방법

### Setup
```bash
# Playwright 설치
npm install -D @playwright/test

# 테스트 실행
npx playwright test

# UI 모드 (디버깅)
npx playwright test --ui

# 특정 브라우저
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### CI/CD 통합
```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npx playwright test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 9. 다음 단계 (Claude Code)

1. **테스트 파일 생성**: `e2e/multi-strategy.spec.ts`
2. **Fixture 구현**: DB setup/teardown
3. **Helper 함수**: `loginAsUser`, `setupOwnership`
4. **CI/CD 통합**: GitHub Actions
5. **리포트**: HTML 리포트 생성 및 저장
