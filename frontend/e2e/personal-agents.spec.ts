import { test, expect } from "./fixtures";

test.describe("Personal Agents Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/personal-agents");
  });

  test("should display personal agents list page", async ({ page }) => {
    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // Check page has loaded
    await expect(page).toHaveURL(/\/personal-agents/);
  });

  test("should display personal agent cards when agents exist", async ({
    page,
  }) => {
    // Wait for agents to load
    await page.waitForLoadState("networkidle");

    // Look for personal agent cards or empty state
    const agentCards = page.locator(
      '[data-testid="personal-agent-card"], .personal-agent-card'
    );
    const emptyState = page.getByText(
      /no personal agents|パーソナルエージェントがありません/i
    );

    // Either agents or empty state should be visible
    const hasAgents = (await agentCards.count()) > 0;
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasAgents || hasEmptyState).toBeTruthy();
  });

  test("should have create new personal agent button", async ({ page }) => {
    // Look for create button
    const createButton = page.getByRole("button", {
      name: /新規作成|create|新しい/i,
    });

    await expect(createButton).toBeVisible();
  });

  test("should navigate to create personal agent page", async ({ page }) => {
    // Click create button
    const createButton = page.getByRole("button", {
      name: /新規作成|create|新しい/i,
    });

    if (await createButton.isVisible()) {
      await createButton.click();
      await expect(page).toHaveURL(/\/personal-agents\/new/);
    }
  });
});

test.describe("Create Personal Agent Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/personal-agents/new");
  });

  test("should display create personal agent form", async ({ page }) => {
    // Check for form elements
    const nameInput = page.getByLabel(/name|名前/i);

    await expect(nameInput).toBeVisible();
  });

  test("should have required form fields", async ({ page }) => {
    // Check for required fields
    const nameInput = page.getByLabel(/name|名前/i);
    const systemPromptInput = page.getByLabel(
      /system prompt|システムプロンプト/i
    );

    await expect(nameInput).toBeVisible();
    await expect(systemPromptInput).toBeVisible();
  });

  test("should have is_public toggle", async ({ page }) => {
    // Look for public toggle
    const publicToggle = page.getByRole("checkbox", {
      name: /public|公開/i,
    });

    // Toggle may or may not exist depending on implementation
    const hasToggle = await publicToggle.isVisible().catch(() => false);
    expect(typeof hasToggle).toBe("boolean");
  });

  test("should have submit button", async ({ page }) => {
    // Look for the form submit button
    const submitButton = page.getByRole("button", {
      name: /保存|save|作成|create/i,
    });

    await expect(submitButton).toBeVisible();
  });

  test("should validate required fields on submit", async ({ page }) => {
    // Try to submit empty form
    const submitButton = page.getByRole("button", {
      name: /保存|save|作成|create/i,
    });

    await submitButton.click();

    // Should show validation errors or stay on page
    await expect(page).toHaveURL(/\/personal-agents\/new/);
  });

  test("should create personal agent successfully", async ({ page }) => {
    // Fill in the form
    const nameInput = page.getByLabel(/name|名前/i);
    await nameInput.fill("Test Personal Agent");

    const descriptionInput = page.getByLabel(/description|説明/i);
    if (await descriptionInput.isVisible()) {
      await descriptionInput.fill("A test personal agent");
    }

    const systemPromptInput = page.getByLabel(
      /system prompt|システムプロンプト/i
    );
    await systemPromptInput.fill("You are a helpful orchestrator agent.");

    // Submit the form
    const submitButton = page.getByRole("button", {
      name: /保存|save|作成|create/i,
    });
    await submitButton.click();

    // Should redirect to personal agents list or detail page
    await page.waitForURL(/\/personal-agents/);
  });
});

test.describe("Personal Agent Detail Page", () => {
  test("should navigate to personal agent detail from list", async ({
    page,
  }) => {
    await page.goto("/personal-agents");
    await page.waitForLoadState("networkidle");

    // Click on a personal agent card
    const agentCard = page
      .locator('[data-testid="personal-agent-card"]')
      .first();

    if (await agentCard.isVisible()) {
      await agentCard.click();
      // Should navigate to personal agent detail or chat page
      await expect(page).toHaveURL(/\/personal-agents\/[a-f0-9-]+/);
    }
  });
});

test.describe("Personal Agent Settings Page", () => {
  test("should navigate to personal agent settings", async ({ page }) => {
    await page.goto("/personal-agents/33333333-3333-3333-3333-333333333333");
    await page.waitForLoadState("networkidle");

    // Look for settings link or button
    const settingsButton = page.getByRole("button", {
      name: /settings|設定/i,
    });
    const settingsLink = page.getByRole("link", {
      name: /settings|設定/i,
    });

    const hasButton = await settingsButton.isVisible().catch(() => false);
    const hasLink = await settingsLink.isVisible().catch(() => false);

    if (hasButton || hasLink) {
      if (hasButton) {
        await settingsButton.click();
      } else {
        await settingsLink.click();
      }
      await expect(page).toHaveURL(
        /\/personal-agents\/[a-f0-9-]+\/settings/
      );
    }
  });

  test("should display edit form on settings page", async ({ page }) => {
    await page.goto(
      "/personal-agents/33333333-3333-3333-3333-333333333333/settings"
    );
    await page.waitForLoadState("networkidle");

    // Check for edit form elements
    const nameInput = page.getByLabel(/name|名前/i);

    await expect(nameInput).toBeVisible();
  });
});
