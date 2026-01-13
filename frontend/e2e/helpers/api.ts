/**
 * API Helper Functions
 * Phase 5, T5.6: E2E Tests
 */

import { Page, APIRequestContext } from '@playwright/test';

const API_BASE = 'http://localhost:8001/api';

export interface CreateOrderParams {
  strategy: string;
  ticker: string;
  action: 'buy' | 'sell';
  quantity: number;
}

export async function createOrder(page: Page, params: CreateOrderParams) {
  await page.goto('/orders/new');
  await page.selectOption('[name="strategy"]', params.strategy);
  await page.fill('[name="ticker"]', params.ticker);
  await page.selectOption('[name="action"]', params.action);
  await page.fill('[name="quantity"]', params.quantity.toString());
  await page.click('button[type="submit"]');
}

export async function setupOwnership(
  request: APIRequestContext,
  params: { ticker: string; strategy: string }
) {
  await request.post(`${API_BASE}/ownership`, {
    data: {
      ticker: params.ticker,
      strategy_id: params.strategy,
      ownership_type: 'primary'
    }
  });
}

export async function setupStrategies(request: APIRequestContext) {
  const strategies = [
    {
      id: 'test-long',
      name: 'long_term',
      display_name: '장기 투자',
      persona_type: 'long_term',
      priority: 100,
      time_horizon: 'long',
      is_active: true
    },
    {
      id: 'test-div',
      name: 'dividend',
      display_name: '배당 투자',
      persona_type: 'dividend',
      priority: 90,
      time_horizon: 'medium',
      is_active: true
    },
    {
      id: 'test-trade',
      name: 'trading',
      display_name: '단기 트레이딩',
      persona_type: 'trading',
      priority: 50,
      time_horizon: 'short',
      is_active: true
    },
    {
      id: 'test-aggr',
      name: 'aggressive',
      display_name: '공격적 투자',
      persona_type: 'aggressive',
      priority: 30,
      time_horizon: 'short',
      is_active: true
    }
  ];

  for (const strategy of strategies) {
    await request.post(`${API_BASE}/strategies`, { data: strategy });
  }
}

export async function cleanupTestData(request: APIRequestContext) {
  // Delete test ownerships
  await request.delete(`${API_BASE}/ownership/test-cleanup`);

  // Delete test orders
  await request.delete(`${API_BASE}/orders/test-cleanup`);

  // Delete test strategies
  await request.delete(`${API_BASE}/strategies/test-cleanup`);
}
