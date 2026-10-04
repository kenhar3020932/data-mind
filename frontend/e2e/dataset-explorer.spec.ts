import { test, expect } from "@playwright/test";

test.describe("Dataset Explorer", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/datasets");
  });

  test("should load dataset list", async ({ page }) => {
    await expect(page.locator("[data-testid='dataset-list']")).toBeVisible();
  });

  test("should search datasets", async ({ page }) => {
    const searchInput = page.locator("[data-testid='search-input']");
    await searchInput.fill("sales");
    await expect(searchInput).toHaveValue("sales");
  });

  test("should filter by status", async ({ page }) => {
    const filterBtn = page.locator("[data-testid='filter-status']");
    await filterBtn.click();
    await expect(page.locator("[data-testid='filter-dropdown']")).toBeVisible();
  });

  test("should navigate to dataset details", async ({ page }) => {
    const firstDataset = page.locator("[data-testid='dataset-card']").first();
    await firstDataset.click();
    await expect(page).toHaveURL(/\/datasets\/[\w-]+/);
  });
});