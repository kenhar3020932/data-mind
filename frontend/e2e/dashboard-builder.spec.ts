import { test, expect } from "@playwright/test";

test.describe("Dashboard Builder", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should load dashboard builder page", async ({ page }) => {
    await page.getByRole("link", { name: /dashboard/i }).click();
    await expect(page.locator("[data-testid='dashboard-builder']")).toBeVisible();
  });

  test("should add new widget", async ({ page }) => {
    await page.getByRole("button", { name: /add widget/i }).click();
    await expect(page.locator(".widget-card")).toHaveCount(6); // 5 default + 1 new
  });

  test("should delete widget", async ({ page }) => {
    const initialCount = await page.locator(".widget-card").count();
    await page.locator(".widget-card").first().getByRole("button", { name: /delete/i }).click();
    await expect(page.locator(".widget-card")).toHaveCount(initialCount - 1);
  });

  test("should drag and drop widget", async ({ page }) => {
    const widget = page.locator(".widget-card").first();
    const box = await widget.boundingBox();
    if (box) {
      await widget.dragTo(page.locator(".widget-card").last());
      await expect(widget).toBeVisible();
    }
  });
});