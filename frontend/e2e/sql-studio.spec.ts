import { test, expect } from "@playwright/test";

test.describe("SQL Studio", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/sql-studio");
  });

  test("should load SQL editor", async ({ page }) => {
    await expect(page.locator("[data-testid='sql-editor']")).toBeVisible();
  });

  test("should accept SQL input", async ({ page }) => {
    const editor = page.locator("[data-testid='sql-editor'] textarea");
    await editor.fill("SELECT * FROM users LIMIT 10");
    await expect(editor).toHaveValue("SELECT * FROM users LIMIT 10");
  });

  test("should execute query", async ({ page }) => {
    await page.locator("[data-testid='sql-editor'] textarea").fill(
      "SELECT 1 AS test"
    );
    await page.getByRole("button", { name: /execute/i }).click();
    await expect(page.locator("[data-testid='query-results']")).toBeVisible();
  });

  test("should show validation feedback", async ({ page }) => {
    await page.locator("[data-testid='sql-editor'] textarea").fill(
      "DROP TABLE users"
    );
    await page.getByRole("button", { name: /execute/i }).click();
    await expect(page.locator("[data-testid='validation-error']")).toBeVisible();
  });
});