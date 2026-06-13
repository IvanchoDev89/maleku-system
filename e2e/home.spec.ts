import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test('should load the home page', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/Costa Rica Travel/)
  })

  test('should show navigation', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('nav')).toBeVisible()
  })

  test('should navigate to hotels page', async ({ page }) => {
    await page.goto('/')
    const hotelsLink = page.locator('a').filter({ hasText: /Hoteles/i }).first()
    if (await hotelsLink.isVisible()) {
      await hotelsLink.click()
      await expect(page).toHaveURL(/\/hoteles/)
    }
  })
})

test.describe('Search', () => {
  test('should have a search input', async ({ page }) => {
    await page.goto('/search')
    await expect(page.locator('input[type="search"], input[name="q"]').first()).toBeVisible()
  })
})
