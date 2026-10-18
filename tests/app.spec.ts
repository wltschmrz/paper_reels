import { test, expect } from "@playwright/test";
import shorts from "../src/data/shorts.json" with { type: "json" };
test("research discovery, persistence, simulation, evaluation and collections", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto("/");
  await expect(page.locator(".paper-card")).toHaveCount(21);
  await expect(page.locator(".paper-preview img").first()).toBeVisible();
  await page.screenshot({ path: "test-results/desktop.png", fullPage: false });
  await page.getByLabel("논문 검색", { exact: true }).fill("mean");
  const count = await page.locator(".paper-card").count();
  expect(count).toBeGreaterThan(0);
  await page
    .locator("nav")
    .getByRole("button", { name: "Paper Shorts", exact: true })
    .click();
  await expect(page.locator(".paper-card")).toHaveCount(count);
  await expect(page.getByLabel("논문 검색", { exact: true })).toHaveValue(
    "mean",
  );
  await page
    .locator("nav")
    .getByRole("button", { name: "Paper Feed", exact: true })
    .click();
  await page.getByLabel("검색어 지우기").click();
  await page
    .locator(".paper-card")
    .first()
    .getByRole("button", { name: "북마크", exact: true })
    .click();
  await page.reload();
  await expect(
    page
      .locator(".paper-card")
      .first()
      .getByRole("button", { name: "북마크 해제" }),
  ).toHaveAttribute("aria-pressed", "true");
  await page
    .locator(".paper-card")
    .first()
    .getByRole("button", { name: "컬렉션에 저장" })
    .click();
  await page.getByRole("button", { name: "Reading list", exact: true }).click();
  await page.getByRole("button", { name: "닫기" }).click();
  await page
    .locator("nav")
    .getByRole("button", { name: "Collections", exact: true })
    .click();
  await page.getByRole("button", { name: "Reading list 1 papers" }).click();
  await expect(page.locator(".paper-card")).toHaveCount(1);
  await page
    .locator("nav")
    .getByRole("button", { name: "Paper Feed", exact: true })
    .click();
  await page.locator(".paper-title").first().click();
  await expect(page.getByRole("dialog")).toContainText("Abstract");
  await page.keyboard.press("Escape");
  await page
    .locator(".paper-card")
    .first()
    .getByRole("button", { name: "Generate Short" })
    .click();
  await page.getByLabel("Preset name").fill("Test intuition");
  await page.getByRole("button", { name: "Save preset", exact: true }).click();
  await page.getByRole("button", { name: "Start demo generation" }).click();
  await expect(page.getByRole("dialog")).toContainText("DEMO IN PROGRESS");
  await expect(
    page.getByRole("button", { name: "View demo preview" }),
  ).toBeVisible({ timeout: 30000 });
  await page.getByRole("button", { name: "View demo preview" }).click();
  await expect(page.locator(".reel-placeholder")).toContainText(
    "DEMO PREVIEW · NO VIDEO",
  );
  await page.getByRole("button", { name: "Follow", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Following", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "0 comments" }).click();
  await page
    .getByLabel("Comment", { exact: true })
    .fill("00:15 — 원문 식과 비교해 보기");
  await page.getByRole("button", { name: "Post comment" }).click();
  await expect(page.locator(".comment-box")).toContainText(
    "00:15 — 원문 식과 비교해 보기",
  );
  await page.screenshot({ path: "test-results/explore.png" });
  await page
    .locator("nav")
    .getByRole("button", { name: "Paper Feed", exact: true })
    .click();
  await page
    .locator(".paper-card")
    .first()
    .getByRole("button", { name: "Generate Short" })
    .click();
  await page.getByRole("button", { name: "Start demo generation" }).click();
  await page.getByRole("button", { name: "Cancel job" }).click();
  await expect(page.getByRole("dialog")).toContainText("CANCELLED");
  expect(errors).toEqual([]);
});
test("mobile layout, sample explore, filtering and modal usability", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({ path: "test-results/mobile.png", fullPage: false });
  await page.getByRole("button", { name: "메뉴 열기" }).click();
  await page
    .locator("nav")
    .getByRole("button", { name: "Explore NEW" })
    .click();
  await expect(page.locator("video")).toBeVisible();
  await expect(page.locator(".comment-box")).toBeVisible();
  await page
    .getByRole("button", { name: "Create your version", exact: true })
    .click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByRole("button", { name: "닫기" }).click();
  await page.getByRole("button", { name: "메뉴 열기" }).click();
  await page
    .locator("nav")
    .getByRole("button", { name: "Paper Feed", exact: true })
    .click();
  await page
    .locator(".topic-filters")
    .getByRole("button", { name: "Drifting", exact: true })
    .click();
  await expect(page.locator(".paper-card")).toHaveCount(7);
  await page.locator(".paper-title").first().click();
  await expect(page.locator(".detail-preview")).toBeVisible();
  await page.keyboard.press("Escape");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
});

test("seeded thumbnail opens discussion and persists independent feedback", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .locator("nav")
    .getByRole("button", { name: "Paper Shorts", exact: true })
    .click();
  await expect(page.locator(".short-tile")).toHaveCount(shorts.length);
  await page.screenshot({ path: "test-results/sample-shorts.png" });
  await page
    .locator(".short-tile")
    .filter({ hasText: "@mint_tensor_42" })
    .click();
  await expect(page.locator(".reel-demo-thumbnail")).toBeVisible();
  await expect(page.locator("video")).toHaveCount(0);
  await expect(page.locator(".reel-caption")).toContainText(
    "@mint_tensor_42 · 가상 사용자",
  );
  await page.getByRole("button", { name: "Short 좋아요", exact: true }).click();
  await page
    .getByRole("button", { name: "Good visualization", exact: true })
    .click();
  await page
    .getByLabel("Comment", { exact: true })
    .fill("썸네일의 흐름 그림이 궁금해요.");
  await page.getByRole("button", { name: "Post comment", exact: true }).click();
  await page.getByRole("button", { name: "다음 Short" }).click();
  await expect(page.locator(".comment-box")).not.toContainText(
    "썸네일의 흐름 그림이 궁금해요.",
  );
  await page.getByRole("button", { name: "이전 Short" }).click();
  await expect(page.locator(".comment-box")).toContainText(
    "썸네일의 흐름 그림이 궁금해요.",
  );
  await expect(
    page.getByRole("button", { name: "Good visualization", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await page.reload();
  await page
    .locator("nav")
    .getByRole("button", { name: "Explore NEW" })
    .click();
  await page.getByRole("button", { name: "다음 Short" }).click();
  await expect(page.locator(".comment-box")).toContainText(
    "썸네일의 흐름 그림이 궁금해요.",
  );
  await expect(
    page.getByRole("button", { name: "Short 좋아요", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await page.screenshot({
    path: "test-results/sample-discussion.png",
    fullPage: true,
  });
});

test("real sample playback and server generation prerequisites", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .locator("nav")
    .getByRole("button", { name: "Paper Shorts", exact: true })
    .click();
  await page.locator(".short-tile").first().click();
  const video = page.locator("video");
  await expect(video).toBeVisible();
  await expect
    .poll(() => video.evaluate((v: HTMLVideoElement) => v.readyState))
    .toBeGreaterThanOrEqual(1);
  const duration = await video.evaluate((v: HTMLVideoElement) => v.duration);
  expect(duration).toBeCloseTo(83.6, 0);
  await video.evaluate((v: HTMLVideoElement) => {
    v.muted = true;
    return v.play();
  });
  await expect
    .poll(() => video.evaluate((v: HTMLVideoElement) => v.currentTime))
    .toBeGreaterThan(0.1);
  await video.evaluate((v: HTMLVideoElement) => v.pause());
  await expect(page.locator(".reel-caption")).toContainText(
    "On the Stability and Convergence of Flow Map Training",
  );
  await page
    .getByRole("button", { name: "Create your version", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Real generation · my API keys" })
    .click();
  await expect(
    page.getByRole("button", { name: "Generate with my API keys" }),
  ).toBeDisabled();
  await expect(page.getByLabel("Math depth (0–3)")).toBeVisible();
  await page.screenshot({ path: "test-results/backend-studio.png" });
});

test("both budgeted Drifting baselines play under their source paper", async ({
  page,
}) => {
  for (const [creator, seconds] of [
    ["you_openai", 51.636],
    ["you_anthropic", 67.003],
  ] as const) {
    await page.goto("/");
    await page
      .locator("nav")
      .getByRole("button", { name: "Paper Shorts", exact: true })
      .click();
    await page
      .locator('[data-paper-id="2602.04770"] .short-tile')
      .filter({ hasText: `@${creator}` })
      .click();
    const video = page.locator("video");
    await expect
      .poll(() => video.evaluate((v: HTMLVideoElement) => v.readyState))
      .toBeGreaterThanOrEqual(1);
    expect(
      await video.evaluate((v: HTMLVideoElement) => v.duration),
    ).toBeCloseTo(seconds, 0);
    await video.evaluate((v: HTMLVideoElement) => {
      v.muted = true;
      return v.play();
    });
    await expect
      .poll(() => video.evaluate((v: HTMLVideoElement) => v.currentTime))
      .toBeGreaterThan(0.1);
    await expect(page.locator(".reel-caption")).toContainText(
      "Generative Modeling via Drifting",
    );
    await page.screenshot({ path: `test-results/drifting-${creator}.png` });
  }
});

test("paper flips inline without hiding other papers and restores abstract", async ({
  page,
}) => {
  await page.goto("/");
  const card = page.locator('[data-paper-id="2602.04770"]');
  const other = page.locator('[data-paper-id="2610.20674"]');
  await card
    .getByRole("button", {
      name: "Generative Modeling via Drifting 쇼츠 버전 보기",
      exact: true,
    })
    .click();
  await expect(page.locator(".paper-card")).toHaveCount(21);
  await expect(card).toHaveAttribute("data-mode", "shorts");
  await expect(other).toHaveAttribute("data-mode", "papers");
  await expect(card).toContainText("@you_openai");
  await expect(page.locator("video")).toHaveCount(0);
  await card
    .getByRole("button", {
      name: "Generative Modeling via Drifting 초록 보기",
      exact: true,
    })
    .click();
  await expect(card.locator(".abstract")).toBeVisible();
});

test("shorts grid fits viewport and omits creation tile when row is full", async ({
  page,
}) => {
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/");
    const card = page.locator('[data-paper-id="2602.04770"]');
    await card
      .getByRole("button", {
        name: "Generative Modeling via Drifting 쇼츠 버전 보기",
        exact: true,
      })
      .click();
    const row = card.locator(".shorts-row");
    await expect(row).toBeVisible();
    await expect
      .poll(async () =>
        page.evaluate(() => document.documentElement.scrollWidth),
      )
      .toBeLessThanOrEqual(width);
    const columns = await row.evaluate(
      (el) => getComputedStyle(el).gridTemplateColumns.split(" ").length,
    );
    const count = await row.locator(".short-tile").count();
    await expect(row.locator(".create-tile")).toHaveCount(
      count % columns === 0 ? 0 : 1,
    );
    await card.scrollIntoViewIfNeeded();
    await page.screenshot({ path: `test-results/inline-${width}.png` });
  }
});

test("both Flow Map v2 videos play alongside the original paper", async ({
  page,
}) => {
  for (const provider of ["openai", "anthropic"]) {
    const short = shorts.find((s) => s.id === `flowmap-v2-${provider}`);
    expect(short).toBeDefined();
    await page.goto("/");
    const card = page.locator('[data-paper-id="2610.20674"]');
    await card.getByRole("button", { name: /쇼츠 버전 보기/ }).click();
    await expect(page.locator(".paper-card")).toHaveCount(21);
    await card
      .locator(".short-tile")
      .filter({ hasText: `@you_${provider}_v2` })
      .click();
    const video = page.locator("video");
    await expect
      .poll(() => video.evaluate((v: HTMLVideoElement) => v.readyState))
      .toBeGreaterThanOrEqual(1);
    expect(
      await video.evaluate((v: HTMLVideoElement) => v.duration),
    ).toBeCloseTo(short!.duration, 0);
    await video.evaluate((v: HTMLVideoElement) => {
      v.muted = true;
      return v.play();
    });
    await expect
      .poll(() => video.evaluate((v: HTMLVideoElement) => v.currentTime))
      .toBeGreaterThan(0.1);
    await video.evaluate((v: HTMLVideoElement) => v.pause());
    await expect(page.locator(".reel-caption")).toContainText(
      "On the Stability and Convergence of Flow Map Training",
    );
  }
});
