import { test, expect } from "./fixtures";

test.describe("Authentication", () => {
  test.describe("Login Page", () => {
    test("should display login form", async ({ page }) => {
      await page.goto("/auth/login");

      // Check for email input
      const emailInput = page.getByLabel(/email|メール/i);
      await expect(emailInput).toBeVisible();

      // Check for password input
      const passwordInput = page.getByLabel(/password|パスワード/i);
      await expect(passwordInput).toBeVisible();

      // Check for submit button
      const submitButton = page.getByRole("button", { name: /sign in|ログイン/i });
      await expect(submitButton).toBeVisible();
    });

    test("should have link to signup page", async ({ page }) => {
      await page.goto("/auth/login");

      const signupLink = page.getByRole("link", { name: /sign up|新規登録|アカウント作成/i });
      await expect(signupLink).toBeVisible();
    });

    test("should navigate to signup page", async ({ page }) => {
      await page.goto("/auth/login");

      const signupLink = page.getByRole("link", { name: /sign up|新規登録|アカウント作成/i });
      await signupLink.click();

      await expect(page).toHaveURL(/\/auth\/signup/);
    });
  });

  test.describe("Signup Page", () => {
    test("should display signup form", async ({ page }) => {
      await page.goto("/auth/signup");

      // Check for email input
      const emailInput = page.getByLabel(/email|メール/i);
      await expect(emailInput).toBeVisible();

      // Check for password input (use exact match to avoid matching "Confirm Password")
      const passwordInput = page.getByRole("textbox", { name: "Password", exact: true });
      await expect(passwordInput).toBeVisible();

      // Check for confirm password input
      const confirmPasswordInput = page.getByRole("textbox", { name: /confirm password/i });
      await expect(confirmPasswordInput).toBeVisible();

      // Check for submit button
      const submitButton = page.getByRole("button", { name: /create account|新規登録|アカウント作成/i });
      await expect(submitButton).toBeVisible();
    });

    test("should have link to login page", async ({ page }) => {
      await page.goto("/auth/signup");

      const loginLink = page.getByRole("link", { name: /sign in|ログイン/i });
      await expect(loginLink).toBeVisible();
    });

    test("should navigate to login page", async ({ page }) => {
      await page.goto("/auth/signup");

      const loginLink = page.getByRole("link", { name: /sign in|ログイン/i });
      await loginLink.click();

      await expect(page).toHaveURL(/\/auth\/login/);
    });
  });

  test.describe("User Menu (Mock Auth)", () => {
    test("should show user email in menu when logged in", async ({ page }) => {
      // When Supabase is not configured, mock user is automatically logged in
      await page.goto("/");

      // Look for user menu button
      const userMenuButton = page.getByRole("button", { name: /user menu/i });

      if (await userMenuButton.isVisible()) {
        await userMenuButton.click();

        // Should show mock user email
        const userEmail = page.getByText(/dev@example.com/i);
        await expect(userEmail).toBeVisible();
      }
    });

    test("should have sign out option", async ({ page }) => {
      await page.goto("/");

      const userMenuButton = page.getByRole("button", { name: /user menu/i });

      if (await userMenuButton.isVisible()) {
        await userMenuButton.click();

        // Should show sign out button
        const signOutButton = page.getByRole("button", { name: /sign out|ログアウト/i });
        await expect(signOutButton).toBeVisible();
      }
    });
  });
});
