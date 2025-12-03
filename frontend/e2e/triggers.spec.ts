import { expect, test } from "./fixtures";

const TEST_WORKFLOW_ID = "66666666-6666-6666-6666-666666666666";

test.describe("Trigger Settings UI", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to workflow edit page
    await page.goto(`/workflows/${TEST_WORKFLOW_ID}`);
    // Wait for the page to load
    await page.waitForLoadState("networkidle");
  });

  test("should open trigger panel when clicking trigger button", async ({ page }) => {
    // Find and click the trigger button (CalendarClock icon)
    const triggerButton = page.getByRole("button", { name: /トリガー設定/i });
    await triggerButton.click();

    // Verify trigger panel is visible
    await expect(page.getByText("トリガー設定")).toBeVisible();
    await expect(page.getByText("スケジュール")).toBeVisible();
    await expect(page.getByText("Webhook")).toBeVisible();
  });

  test("should display existing schedule triggers", async ({ page }) => {
    // Open trigger panel
    const triggerButton = page.getByRole("button", { name: /トリガー設定/i });
    await triggerButton.click();

    // Verify schedule trigger is displayed
    await expect(page.getByText("0 9 * * *")).toBeVisible();
  });

  test("should create a new schedule trigger", async ({ page }) => {
    // Open trigger panel
    const triggerButton = page.getByRole("button", { name: /トリガー設定/i });
    await triggerButton.click();

    // Click add button
    await page.getByRole("button", { name: /スケジュールトリガーを追加/i }).click();

    // Select a preset
    await page.getByRole("combobox").click();
    await page.getByRole("option", { name: /毎日 12:00/i }).click();

    // Submit the form
    await page.getByRole("button", { name: /追加/i }).click();

    // Verify the new trigger is displayed
    await expect(page.getByText("0 12 * * *")).toBeVisible();
  });

  test("should toggle schedule trigger", async ({ page }) => {
    // Open trigger panel
    const triggerButton = page.getByRole("button", { name: /トリガー設定/i });
    await triggerButton.click();

    // Wait for schedule triggers to load
    await expect(page.getByText("0 9 * * *")).toBeVisible();

    // Find and click the toggle switch
    const toggleSwitch = page.getByRole("switch").first();
    const isChecked = await toggleSwitch.isChecked();
    await toggleSwitch.click();

    // Verify the state changed
    await expect(toggleSwitch).toHaveAttribute(
      "data-state",
      isChecked ? "unchecked" : "checked"
    );
  });

  test("should switch to webhook tab and display triggers", async ({ page }) => {
    // Open trigger panel
    const triggerButton = page.getByRole("button", { name: /トリガー設定/i });
    await triggerButton.click();

    // Click webhook tab
    await page.getByRole("tab", { name: /Webhook/i }).click();

    // Verify webhook trigger is displayed
    await expect(page.getByText("test-webhook")).toBeVisible();
    await expect(page.getByText(/Webhook URL/i)).toBeVisible();
  });

  test("should create a new webhook trigger", async ({ page }) => {
    // Open trigger panel
    const triggerButton = page.getByRole("button", { name: /トリガー設定/i });
    await triggerButton.click();

    // Click webhook tab
    await page.getByRole("tab", { name: /Webhook/i }).click();

    // Click add button
    await page.getByRole("button", { name: /Webhookトリガーを追加/i }).click();

    // Enter webhook path
    await page.getByLabel(/Webhookパス/i).fill("my-new-webhook");

    // Submit the form
    await page.getByRole("button", { name: /作成/i }).click();

    // Verify the success message and new trigger details
    await expect(page.getByText(/Webhookトリガーを作成しました/i)).toBeVisible();
    await expect(page.getByText(/my-new-webhook/i)).toBeVisible();
    await expect(page.getByText(/シークレットキー/i)).toBeVisible();
  });

  test("should regenerate webhook secret", async ({ page }) => {
    // Open trigger panel
    const triggerButton = page.getByRole("button", { name: /トリガー設定/i });
    await triggerButton.click();

    // Click webhook tab
    await page.getByRole("tab", { name: /Webhook/i }).click();

    // Wait for webhooks to load
    await expect(page.getByText("test-webhook")).toBeVisible();

    // Handle confirmation dialog
    page.on("dialog", async (dialog) => {
      await dialog.accept();
    });

    // Click regenerate button
    await page.getByRole("button", { name: /再生成/i }).click();

    // Verify new secret is shown (the secret should now be visible)
    await expect(page.locator("code").filter({ hasText: /secret_/ })).toBeVisible();
  });

  test("should delete schedule trigger", async ({ page }) => {
    // Open trigger panel
    const triggerButton = page.getByRole("button", { name: /トリガー設定/i });
    await triggerButton.click();

    // Wait for schedule triggers to load
    await expect(page.getByText("0 9 * * *")).toBeVisible();

    // Handle confirmation dialog
    page.on("dialog", async (dialog) => {
      await dialog.accept();
    });

    // Find and click delete button (Trash2 icon)
    // Try by button with Trash icon
    const trashButton = page.getByRole("button").filter({ has: page.locator("svg") }).last();
    await trashButton.click();

    // Give time for the deletion to process
    await page.waitForTimeout(500);
  });

  test("should close trigger panel when clicking button again", async ({ page }) => {
    // Open trigger panel
    const triggerButton = page.getByRole("button", { name: /トリガー設定/i });
    await triggerButton.click();

    // Verify panel is visible
    await expect(page.getByText("トリガー設定")).toBeVisible();

    // Close panel
    await triggerButton.click();

    // Verify panel is hidden (check for the Card title specifically in the sidebar area)
    const triggerPanel = page.locator(".border-l").getByText("トリガー設定");
    await expect(triggerPanel).not.toBeVisible();
  });
});
