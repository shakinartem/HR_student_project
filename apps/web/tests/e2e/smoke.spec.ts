import { expect, test } from "@playwright/test";

const vacancyTitles = [
  "Waiter evening shift",
  "Barista trainee",
  "Weekend promoter",
  "Evening courier",
] as const;

function routeValue(url: string) {
  return new URL(url).searchParams.get("route") ?? "";
}

async function openVacancyFromFeed(page: import("@playwright/test").Page, title: string) {
  await page.getByRole("button", { name: new RegExp(title, "i") }).click();
  await expect
    .poll(() => routeValue(page.url()), {
      message: `Expected ${title} to open in vacancy detail`,
    })
    .toContain("/vacancies/");
}

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button", { name: /Waiter evening shift/i })).toBeVisible();
});

test("app loads and guest feed renders seeded vacancies", async ({ page }) => {
  await expect(page.getByRole("button", { name: /Waiter evening shift/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Barista trainee/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Weekend promoter/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Evening courier/i })).toBeVisible();
});

test("guest can open vacancy details without exposing HR contacts", async ({ page }) => {
  await openVacancyFromFeed(page, vacancyTitles[0]);

  await expect(page.getByRole("button", { name: /откликнуться/i })).toBeVisible();
  await expect(page.locator("body")).not.toContainText("Hidden HR Contact");
  await expect(page.locator("body")).not.toContainText("+79990002222");
  await expect(page.locator("body")).not.toContainText("@example.com");
});

test("guest reaches paywall on the fourth unique vacancy preview", async ({ page }) => {
  for (const title of vacancyTitles.slice(0, 3)) {
    await openVacancyFromFeed(page, title);
    await page.goBack();
    await expect(page.getByRole("button", { name: /Waiter evening shift/i })).toBeVisible();
  }

  await page.getByRole("button", { name: new RegExp(vacancyTitles[3], "i") }).click();

  await expect
    .poll(() => routeValue(page.url()), {
      message: "Expected guest paywall route after fourth preview",
    })
    .toBe("/paywall?reason=guest-limit");
  await expect(page.getByRole("button", { name: /открыть профиль/i })).toBeVisible();
});

test("guest apply action routes to paywall", async ({ page }) => {
  await openVacancyFromFeed(page, vacancyTitles[0]);
  await page.getByRole("button", { name: /откликнуться/i }).click();

  await expect
    .poll(() => routeValue(page.url()), {
      message: "Expected guest apply to redirect to paywall",
    })
    .toBe("/paywall?reason=guest-apply");
  await expect(page.getByRole("button", { name: /открыть профиль/i })).toBeVisible();
});

test("guest cannot open hr route and gets a safe fallback", async ({ page }) => {
  await page.goto("/?route=/hr");

  await expect(page.getByRole("button", { name: /Waiter evening shift/i })).toBeVisible();
  await expect(page.getByText("HR dashboard")).toHaveCount(0);
});

test("guest cannot open admin route and sees access denied", async ({ page }) => {
  await page.goto("/?route=/admin");

  await expect(page.getByText("Access denied")).toBeVisible();
  await expect(page.getByRole("button", { name: /back to feed/i })).toBeVisible();
});
