# E2E Tests - Multi-Strategy Orchestration

Phase 5, T5.6: End-to-End Testing with Playwright

## 📋 Overview

This directory contains Playwright E2E tests for the Multi-Strategy Orchestration Dashboard.

**Design**: Gemini
**Implementation**: Claude Code
**Testing Framework**: Playwright

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
cd frontend
npm install

# Install Playwright browsers
npx playwright install --with-deps
```

### Running Tests

```bash
# Run all tests (headless)
npm run test:e2e

# Run with UI mode (debugging)
npm run test:e2e:ui

# Run with debug mode (step-through)
npm run test:e2e:debug

# View HTML report
npm run test:e2e:report
```

### Running Specific Tests

```bash
# Run specific test file
npx playwright test multi-strategy.spec.ts

# Run specific test by name
npx playwright test -g "should allow order when no conflict exists"

# Run in specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## 📁 Test Structure

```
e2e/
├── multi-strategy.spec.ts    # Main test scenarios
├── helpers/
│   ├── auth.ts                # Authentication helpers
│   └── api.ts                 # API interaction helpers
└── README.md                  # This file
```

## 🧪 Test Scenarios

### User Flow Scenarios

1. **Scenario 1: Normal Flow**
   - No conflicts
   - Order creation succeeds
   - Ownership table updates

2. **Scenario 2: Conflict Detection**
   - Ownership exists
   - Lower priority order blocked
   - Conflict alert displayed

3. **Scenario 3: Priority Override**
   - Higher priority takes ownership
   - Ownership transferred
   - Warning alert shown

### Edge Cases

1. **Slow Network** - 3-second API delay
2. **API Failure** - Error handling
3. **WebSocket Disconnect** - Connection status
4. **Mobile Responsive** - Layout adaptation
5. **Accessibility** - A11y compliance

## 🔧 Configuration

Configuration is in `playwright.config.ts`:

- **Timeout**: 30 seconds per test
- **Retries**: 2 on CI, 0 locally
- **Browsers**: Chromium, Firefox, WebKit
- **Mobile**: Pixel 5, iPhone 12
- **Video**: Recorded on failure
- **Screenshots**: On failure only

## 📊 Test Reports

After running tests:

```bash
# View HTML report
npm run test:e2e:report
```

Reports are saved in:
- `playwright-report/` - HTML report
- `test-results/` - Videos, screenshots, traces

## 🔄 CI/CD Integration

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

Workflow file: `.github/workflows/e2e-tests.yml`

## 🐛 Debugging

### UI Mode (Recommended)

```bash
npm run test:e2e:ui
```

Features:
- Watch mode
- Time travel debugging
- Step through tests
- Network inspector

### Debug Mode

```bash
npm run test:e2e:debug
```

Opens Playwright Inspector for step-by-step execution.

### Headed Mode

```bash
npx playwright test --headed
```

Run tests in browser you can see.

### VSCode Extension

Install "Playwright Test for VSCode" extension for:
- Run/debug tests from editor
- Set breakpoints
- View test results

## 📝 Writing Tests

### Basic Structure

```typescript
import { test, expect } from '@playwright/test';

test('my test', async ({ page }) => {
  await page.goto('/strategies');
  await expect(page.locator('h1')).toBeVisible();
});
```

### Using Helpers

```typescript
import { loginAsUser } from './helpers/auth';

test('authenticated test', async ({ page }) => {
  await loginAsUser(page, 'test_user');
  // ... test logic
});
```

### API Mocking

```typescript
test('mock API', async ({ page, context }) => {
  await context.route('**/api/strategies**', async (route) => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify([...])
    });
  });
});
```

## 🎯 Best Practices

1. **Use data-testid** for reliable selectors
2. **Wait for elements** instead of fixed timeouts
3. **Cleanup test data** after each test
4. **Mock external APIs** when needed
5. **Use Page Object Model** for complex pages

## 📚 Resources

- [Playwright Documentation](https://playwright.dev)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-playwright)
- [Gemini E2E Scenarios](../../docs/planning/e2e-scenarios.md)

## 🤝 Contributing

1. Write tests following existing patterns
2. Add data-testid attributes to components
3. Update this README with new scenarios
4. Ensure tests pass locally before committing

## 📞 Support

For issues or questions:
- Check Playwright docs first
- Review existing test patterns
- Ask in team chat

---

**Created**: 2026-01-13
**Designed by**: Gemini
**Implemented by**: Claude Code
**Phase**: 5, T5.6
