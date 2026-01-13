/**
 * Authentication Helper Functions
 * Phase 5, T5.6: E2E Tests
 */

import { Page } from '@playwright/test';

export async function loginAsUser(page: Page, username: string, password: string = 'password123') {
  await page.goto('/login');
  await page.fill('[name="username"]', username);
  await page.fill('[name="password"]', password);
  await page.click('button[type="submit"]');

  // Wait for navigation to complete
  await page.waitForURL('**/strategies', { timeout: 10000 });
}

export async function logout(page: Page) {
  // Assuming there's a logout button in the header
  await page.click('[data-testid="logout-button"]');
  await page.waitForURL('**/login');
}
