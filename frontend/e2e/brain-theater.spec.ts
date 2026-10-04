import { test, expect } from "@playwright/test";

test.describe("Brain Theater", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should load brain theater", async ({ page }) => {
    await expect(page.locator("[data-testid='brain-theater']")).toBeVisible();
  });

  test("should accept task input", async ({ page }) => {
    const input = page.locator("[data-testid='task-input']");
    await input.fill("Analyze sales trends for Q4");
    await expect(input).toHaveValue("Analyze sales trends for Q4");
  });

  test("should show execution events", async ({ page }) => {
    await page.locator("[data-testid='task-input']").fill(
      "Show me the top 10 customers by revenue"
    );
    await page.getByRole("button", { name: /execute/i }).click();
    await expect(page.locator("[data-testid='event-stream']")).toBeVisible();
  });

  test("should display agent progress", async ({ page }) => {
    await page.getByRole("button", { name: /execute/i }).click();
    await expect(page.locator("[data-testid='agent-status']")).toBeVisible();
  });

  test("should show confidence scores", async ({ page }) => {
    await page.getByRole("button", { name: /execute/i }).click();
    await expect(page.locator("[data-testid='confidence-score']")).toBeVisible();
  });
});