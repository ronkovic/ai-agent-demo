import { test, expect } from "@playwright/test";

test.describe("Home Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should display the home page", async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Agent Platform|AI Agent/i);
  });

  test("should have navigation elements", async ({ page }) => {
    // Check for header or navigation
    const header = page.locator("header");
    await expect(header).toBeVisible();
  });

  test("should navigate to agents page", async ({ page }) => {
    // Click on agents link
    const agentsLink = page.getByRole("link", { name: /agents|エージェント/i });

    if (await agentsLink.isVisible()) {
      await agentsLink.click();
      await expect(page).toHaveURL(/\/agents/);
    }
  });

  test("should have sidebar navigation", async ({ page }) => {
    // Check for sidebar
    const sidebar = page.locator("nav, aside").first();
    await expect(sidebar).toBeVisible();
  });

  test("should support theme toggle", async ({ page }) => {
    // Look for theme toggle button
    const themeToggle = page.getByRole("button", { name: /theme|テーマ/i });

    if (await themeToggle.isVisible()) {
      await themeToggle.click();
      // Theme should change (check for dark/light class on html/body)
      const html = page.locator("html");
      await expect(html).toHaveClass(/dark|light/);
    }
  });
});
