import { expect, test } from "./fixtures";

test.describe("Public Agents", () => {
  // Fixtures already set up the mocks for /api/agents/public and /api/agents/public/search

  test("should navigate to explore page from sidebar", async ({ page }) => {
    await page.goto("/agents");
    await page.waitForLoadState("networkidle");

    // Click on public agents link in sidebar
    const publicAgentsLink = page.getByRole("button", { name: /公開エージェント/i });
    await publicAgentsLink.click();

    // Verify we're on the explore page
    await expect(page).toHaveURL("/agents/explore");
    await expect(page.getByText(/公開エージェントを探す/i)).toBeVisible();
  });

  test("should display public agents list", async ({ page }) => {
    await page.goto("/agents/explore");
    await page.waitForLoadState("networkidle");

    // Verify the page title
    await expect(page.getByText(/公開エージェントを探す/i)).toBeVisible();

    // Verify public agents are displayed
    await expect(page.getByText("Public Helper Agent")).toBeVisible();
    await expect(page.getByText("Public Translator")).toBeVisible();
  });

  test("should search public agents", async ({ page }) => {
    await page.goto("/agents/explore");
    await page.waitForLoadState("networkidle");

    // Enter search query
    const searchInput = page.getByPlaceholder(/エージェントを検索/i);
    await searchInput.fill("Translator");

    // Wait for search results
    await page.waitForTimeout(500);

    // Verify only matching agent is shown
    await expect(page.getByText("Public Translator")).toBeVisible();
  });

  test("should show empty state when no results", async ({ page }) => {
    await page.goto("/agents/explore");
    await page.waitForLoadState("networkidle");

    // Override mock for empty search results
    await page.route("**/api/agents/public/search*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    });

    // Search for non-existent agent
    const searchInput = page.getByPlaceholder(/エージェントを検索/i);
    await searchInput.fill("NonExistentAgent");

    // Wait for search results
    await page.waitForTimeout(500);

    // Verify empty state message
    await expect(page.getByText(/公開エージェントが見つかりません/i)).toBeVisible();
    await expect(page.getByText(/別のキーワードで検索/i)).toBeVisible();
  });

  test("should show public toggle in agent form", async ({ page }) => {
    await page.goto("/agents/new");
    await page.waitForLoadState("networkidle");

    // Verify public toggle is visible
    await expect(page.getByText(/公開設定/i)).toBeVisible();
    await expect(
      page.getByText(/他のユーザーがこのエージェントをワークフローで利用できます/i)
    ).toBeVisible();

    // Verify checkbox exists
    const publicCheckbox = page.locator("#is_public");
    await expect(publicCheckbox).toBeVisible();
  });

  test("should create public agent", async ({ page }) => {
    // Fixtures already handle POST /api/agents with is_public support
    await page.goto("/agents/new");
    await page.waitForLoadState("networkidle");

    // Fill in agent form
    await page.getByLabel(/名前/i).fill("My Public Agent");
    await page.getByLabel(/システムプロンプト/i).fill("You are a helpful assistant.");

    // Enable public toggle
    const publicCheckbox = page.locator("#is_public");
    await publicCheckbox.check();

    // Submit form
    await page.getByRole("button", { name: /エージェントを保存/i }).click();

    // Wait for redirect (should navigate away from /new)
    await page.waitForLoadState("networkidle");
  });

  test("should display provider badge on public agent card", async ({ page }) => {
    await page.goto("/agents/explore");
    await page.waitForLoadState("networkidle");

    // Verify provider badges
    await expect(page.getByText("Claude")).toBeVisible();
    await expect(page.getByText("OpenAI")).toBeVisible();
  });
});
