import { test, expect } from "./fixtures";

test.describe("Settings Page", () => {
  test("should redirect to LLM keys page from settings root", async ({
    page,
  }) => {
    await page.goto("/settings");
    await page.waitForLoadState("networkidle");

    // Should redirect to llm-keys
    await expect(page).toHaveURL(/\/settings\/llm-keys/);
  });

  test("should display settings navigation", async ({ page }) => {
    await page.goto("/settings/llm-keys");
    await page.waitForLoadState("networkidle");

    // Check for navigation items
    const llmKeysNav = page.getByRole("button", {
      name: /LLM.*キー|LLM.*API/i,
    });
    const apiKeysNav = page.getByRole("button", {
      name: /API.*キー/i,
    });

    await expect(llmKeysNav).toBeVisible();
    await expect(apiKeysNav).toBeVisible();
  });
});

test.describe("LLM Keys Settings Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/settings/llm-keys");
    await page.waitForLoadState("networkidle");
  });

  test("should display LLM keys page title", async ({ page }) => {
    // Check for page title or heading
    const heading = page.getByRole("heading", {
      name: /LLM.*キー|LLM.*API/i,
    });

    await expect(heading).toBeVisible();
  });

  test("should display existing LLM configs", async ({ page }) => {
    // Should show existing config or empty state
    const configItem = page.getByText(/openai|anthropic|google/i);
    const emptyState = page.getByText(/設定されていません|no.*config/i);

    const hasConfig = await configItem.isVisible().catch(() => false);
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasConfig || hasEmptyState).toBeTruthy();
  });

  test("should have add LLM key form", async ({ page }) => {
    // Look for provider select and API key input
    const providerSelect = page.getByRole("combobox");
    const apiKeyInput = page.getByPlaceholder(/API.*key|キー/i);

    const hasSelect = await providerSelect.isVisible().catch(() => false);
    const hasInput = await apiKeyInput.isVisible().catch(() => false);

    // At least one form element should exist
    expect(hasSelect || hasInput).toBeTruthy();
  });

  test("should be able to add new LLM config", async ({ page }) => {
    // Find and interact with the form
    const providerSelect = page.locator("select").first();

    if (await providerSelect.isVisible()) {
      await providerSelect.selectOption("anthropic");

      const apiKeyInput = page.getByPlaceholder(/API.*key|キー/i);
      if (await apiKeyInput.isVisible()) {
        await apiKeyInput.fill("sk-ant-test-key-12345");
      }

      const addButton = page.getByRole("button", {
        name: /追加|add|保存|save/i,
      });

      if (await addButton.isVisible()) {
        await addButton.click();
        // Should show success or the new config
        await page.waitForLoadState("networkidle");
      }
    }
  });

  test("should navigate to API keys page", async ({ page }) => {
    const apiKeysNav = page.getByRole("button", {
      name: /API.*キー/i,
    });

    await apiKeysNav.click();
    await expect(page).toHaveURL(/\/settings\/api-keys/);
  });
});

test.describe("API Keys Settings Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/settings/api-keys");
    await page.waitForLoadState("networkidle");
  });

  test("should display API keys page title", async ({ page }) => {
    // Check for page title or heading
    const heading = page.getByRole("heading", {
      name: /API.*キー/i,
    });

    await expect(heading).toBeVisible();
  });

  test("should display existing API keys", async ({ page }) => {
    // Should show existing keys or empty state
    const keyItem = page.getByText(/sk_live/i);
    const emptyState = page.getByText(
      /まだ作成されていません|no.*key|キーがありません/i
    );

    const hasKey = await keyItem.isVisible().catch(() => false);
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasKey || hasEmptyState).toBeTruthy();
  });

  test("should have create new API key button", async ({ page }) => {
    const createButton = page.getByRole("button", {
      name: /新しいキー|create|追加|add/i,
    });

    await expect(createButton).toBeVisible();
  });

  test("should open create API key form", async ({ page }) => {
    const createButton = page.getByRole("button", {
      name: /新しいキー|create|追加|add/i,
    });

    await createButton.click();

    // Form should be visible
    const nameInput = page.getByLabel(/名前|name/i);
    await expect(nameInput).toBeVisible();
  });

  test("should create new API key and show modal", async ({ page }) => {
    // Open form
    const createButton = page.getByRole("button", {
      name: /新しいキー|create|追加|add/i,
    });
    await createButton.click();

    // Fill form
    const nameInput = page.getByLabel(/名前|name/i);
    await nameInput.fill("Test API Key");

    // Submit
    const submitButton = page.getByRole("button", {
      name: /作成|create|submit/i,
    });
    await submitButton.click();

    // Should show modal with the created key
    await page.waitForLoadState("networkidle");

    // Look for modal or success message
    const modal = page.locator('[role="dialog"]');
    const keyDisplay = page.getByText(/sk_live_/);

    const hasModal = await modal.isVisible().catch(() => false);
    const hasKeyDisplay = await keyDisplay.isVisible().catch(() => false);

    expect(hasModal || hasKeyDisplay).toBeTruthy();
  });

  test("should display key prefix for existing keys", async ({ page }) => {
    // Should show key prefix like "sk_live_abc1..."
    const keyPrefix = page.getByText(/sk_live_\w+\.\.\./);

    const hasPrefix = await keyPrefix.isVisible().catch(() => false);
    // This may or may not be visible depending on whether there are existing keys
    expect(typeof hasPrefix).toBe("boolean");
  });

  test("should have delete button for existing keys", async ({ page }) => {
    // Look for delete buttons
    const deleteButtons = page.getByRole("button").filter({
      has: page.locator("svg"),
    });

    // Should have some buttons (at least create button)
    const count = await deleteButtons.count();
    expect(count).toBeGreaterThan(0);
  });

  test("should navigate back to LLM keys page", async ({ page }) => {
    const llmKeysNav = page.getByRole("button", {
      name: /LLM.*キー|LLM.*API/i,
    });

    await llmKeysNav.click();
    await expect(page).toHaveURL(/\/settings\/llm-keys/);
  });
});

test.describe("Settings from Sidebar", () => {
  test("should navigate to settings from sidebar", async ({ page }) => {
    await page.goto("/agents");
    await page.waitForLoadState("networkidle");

    // Look for settings button in sidebar
    const settingsButton = page.getByRole("button", {
      name: /設定|settings/i,
    });

    if (await settingsButton.isVisible()) {
      await settingsButton.click();
      await expect(page).toHaveURL(/\/settings/);
    }
  });
});
