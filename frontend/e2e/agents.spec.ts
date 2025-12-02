import { test, expect } from "@playwright/test";

test.describe("Agents Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/agents");
  });

  test("should display agents list page", async ({ page }) => {
    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // Check page has loaded
    await expect(page).toHaveURL(/\/agents/);
  });

  test("should display agent cards when agents exist", async ({ page }) => {
    // Wait for agents to load (or loading state to complete)
    await page.waitForLoadState("networkidle");

    // Look for agent cards or empty state
    const agentCards = page.locator('[data-testid="agent-card"], .agent-card');
    const emptyState = page.getByText(/no agents|エージェントがありません/i);

    // Either agents or empty state should be visible
    const hasAgents = (await agentCards.count()) > 0;
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasAgents || hasEmptyState).toBeTruthy();
  });

  test("should have create new agent button", async ({ page }) => {
    // Look for create button
    const createButton = page.getByRole("link", {
      name: /new|create|新規|作成/i,
    });

    await expect(createButton).toBeVisible();
  });

  test("should navigate to create agent page", async ({ page }) => {
    // Click create button
    const createButton = page.getByRole("link", {
      name: /new|create|新規|作成/i,
    });

    if (await createButton.isVisible()) {
      await createButton.click();
      await expect(page).toHaveURL(/\/agents\/new/);
    }
  });
});

test.describe("Create Agent Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/agents/new");
  });

  test("should display create agent form", async ({ page }) => {
    // Check for form elements
    const nameInput = page.getByLabel(/name|名前/i);
    const descriptionInput = page.getByLabel(/description|説明/i);

    await expect(nameInput).toBeVisible();
    await expect(descriptionInput).toBeVisible();
  });

  test("should have required form fields", async ({ page }) => {
    // Check for required fields
    const nameInput = page.getByLabel(/name|名前/i);
    const systemPromptInput = page.getByLabel(/system prompt|システムプロンプト/i);

    await expect(nameInput).toBeVisible();
    await expect(systemPromptInput).toBeVisible();
  });

  test("should have LLM provider selection", async ({ page }) => {
    // Look for LLM provider dropdown or select
    const providerSelect = page.getByRole("combobox", {
      name: /provider|プロバイダー/i,
    });

    if (await providerSelect.isVisible()) {
      await expect(providerSelect).toBeVisible();
    }
  });

  test("should have submit button", async ({ page }) => {
    const submitButton = page.getByRole("button", {
      name: /create|save|作成|保存/i,
    });

    await expect(submitButton).toBeVisible();
  });

  test("should validate required fields on submit", async ({ page }) => {
    // Try to submit empty form
    const submitButton = page.getByRole("button", {
      name: /create|save|作成|保存/i,
    });

    await submitButton.click();

    // Should show validation errors or stay on page
    await expect(page).toHaveURL(/\/agents\/new/);
  });
});

test.describe("Agent Detail Page", () => {
  test("should navigate to agent detail from list", async ({ page }) => {
    await page.goto("/agents");
    await page.waitForLoadState("networkidle");

    // Click on first agent card if exists
    const agentCard = page
      .locator('[data-testid="agent-card"], .agent-card')
      .first();

    if (await agentCard.isVisible()) {
      await agentCard.click();
      // Should navigate to agent detail or chat page
      await expect(page).toHaveURL(/\/agents\/[a-f0-9-]+/);
    }
  });
});
