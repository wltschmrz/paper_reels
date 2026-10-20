import { test, expect } from "@playwright/test";
import shorts from "../src/data/shorts.json" with { type: "json" };
test("research discovery, persistence, evaluation and collections", async ({
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
    .locator("nav")
    .getByRole("button", { name: "Explore NEW" })
    .click();
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
    .getByRole("button", { name: "Your interests", exact: true })
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
  await expect(page.locator(".short-tile")).toHaveCount(shorts.length - 2);
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

test("real sample playback without consumer generation controls", async ({
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
  await expect(
    page.getByRole("button", { name: /Generate Short|Create your version/i }),
  ).toHaveCount(0);
});

test("Drifting baselines hidden and missing explanation styles have placeholders", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .locator("nav")
    .getByRole("button", { name: "Paper Shorts", exact: true })
    .click();
  const drifting = page.locator('[data-paper-id="2602.04770"]');
  await expect(drifting.locator(".short-tile")).toHaveCount(3);
  await expect(drifting).not.toContainText("@you_openai");
  await expect(drifting).not.toContainText("@you_anthropic");
  const empty = page
    .locator(".paper-card")
    .filter({ has: page.locator(".shorts-pending") })
    .filter({ hasNot: page.locator(".short-tile") })
    .first();
  await expect(empty.locator(".shorts-pending")).toHaveCount(3);
  await expect(empty.locator(".shorts-pending strong")).toHaveText([
    "Intuition",
    "Geometry",
    "Mathematics",
  ]);
  const partial = page.locator('[data-paper-id="2512.02012"]');
  await expect(partial.locator(".shorts-row > *")).toHaveCount(3);
  await expect(partial.locator(".shorts-row > *").nth(0)).toHaveClass(
    "shorts-pending",
  );
  await expect(
    partial.locator(".shorts-row > *").nth(1).locator(".cover-lens"),
  ).toHaveText("Geometry");
  await expect(
    partial.locator(".shorts-row > *").nth(2).locator(".cover-lens"),
  ).toHaveText("Mathematics");
  await expect(partial.locator(".shorts-pending strong")).toHaveText([
    "Intuition",
  ]);
  const flow = page.locator('[data-paper-id="2610.20674"] .short-tile').first();
  await expect
    .poll(async () => (await flow.boundingBox())!.width)
    .toBeCloseTo(190, 0);
  const before = await flow.boundingBox();
  await page
    .locator(".topic-filters")
    .getByRole("button", { name: "Flow Map Theory", exact: true })
    .click();
  await expect(page.locator(".paper-card")).toHaveCount(1);
  await expect
    .poll(async () => (await flow.boundingBox())!.width)
    .toBeCloseTo(before!.width, 0);
  await page
    .locator(".topic-filters")
    .getByRole("button", { name: "All topics", exact: true })
    .click();
  await expect
    .poll(async () => (await flow.boundingBox())!.width)
    .toBeCloseTo(before!.width, 0);
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
  await expect(card).toContainText("@pixel_sparrow_29");
  await expect(page.locator("video")).toHaveCount(0);
  await card
    .getByRole("button", {
      name: "Generative Modeling via Drifting 초록 보기",
      exact: true,
    })
    .click();
  await expect(card.locator(".abstract")).toBeVisible();
});

test("shorts grid fits viewport without consumer creation tiles", async ({
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
    await expect(row.locator(".create-tile")).toHaveCount(0);
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

test("email digest: footer, history, playback, preferences and honest empty states", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .locator(".app-footer")
    .getByRole("link", { name: "Email Digest Preview", exact: true })
    .click();
  await expect(page).toHaveURL(/#\/digest-preview$/);
  await expect(
    page.getByRole("heading", { name: "Email Digest Preview", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".digest-paper")).toHaveCount(4);
  await expect(page.locator(".digest-score")).toHaveText([
    "96",
    "93",
    "88",
    "87",
  ]);
  await page.reload();
  await expect(page.locator(".digest-paper")).toHaveCount(4);
  await page
    .getByRole("button", { name: "Play the Digest", exact: true })
    .click();
  const video = page.locator(".digest-player video");
  await expect(video).toHaveAttribute("src", /flowmap_reel.mp4/);
  await video.evaluate((v: HTMLVideoElement) => {
    v.dispatchEvent(new Event("ended"));
  });
  await expect(page.getByRole("status")).toHaveText(
    "You've reached the end of this selection.",
  );
  await expect(page.getByRole("button", { name: "Next video" })).toBeDisabled();
  await page.getByRole("button", { name: "닫기", exact: true }).click();
  await page
    .locator(".digest-paper")
    .first()
    .getByRole("button", { name: "Watch Shorts" })
    .click();
  await expect(page.locator(".digest-player")).toContainText("1 / 3");
  await page.keyboard.press("Escape");
  await page
    .locator(".digest-paper")
    .nth(2)
    .getByRole("button", { name: "Watch Shorts" })
    .click();
  await expect(page.getByRole("dialog")).toContainText("No playable short");
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Manage Preferences" }).click();
  await expect(page.getByRole("dialog")).toContainText(
    "Your research interests",
  );
  await page.keyboard.press("Escape");
  await page
    .getByRole("button", { name: "View Full Digest", exact: true })
    .click();
  await expect(page.locator(".paper-card")).toHaveCount(21);
  await page.goBack();
  await expect(page.locator(".digest-paper")).toHaveCount(4);
  await page.goBack();
  await expect(page.locator(".paper-card")).toHaveCount(21);
});

test("email digest: responsive direct entry and valid original-paper links", async ({
  page,
}) => {
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/#/digest-preview");
    await expect(page.locator(".digest-paper")).toHaveCount(4);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    const links = await page
      .locator(".digest-paper-actions a")
      .evaluateAll((els) => els.map((a) => (a as HTMLAnchorElement).href));
    expect(links.every((url) => /^https:\/\/arxiv.org\/abs\//.test(url))).toBe(
      true,
    );
    await page.screenshot({
      path: `test-results/digest-${width}.png`,
      fullPage: true,
    });
  }
});

test("consumer UI has no creation entry points and empty papers show availability", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("button", {
      name: /Generate Short|Creator Studio|Create your|생성 작업/,
    }),
  ).toHaveCount(0);
  await page.locator(".paper-title").first().click();
  await expect(
    page.getByRole("dialog").getByRole("button", { name: "Generate Short" }),
  ).toHaveCount(0);
  await page.keyboard.press("Escape");
  await page
    .locator("nav")
    .getByRole("button", { name: "Paper Shorts", exact: true })
    .click();
  await expect(page.locator(".shorts-pending").first()).toBeVisible();
  await expect(page.locator(".create-tile")).toHaveCount(0);
});

test("both paper views flip independently and navigation restores default faces", async ({
  page,
}) => {
  await page.goto("/");
  const first = page.locator('[data-paper-id="2505.13447"]');
  const second = page.locator('[data-paper-id="2610.20674"]');
  const nav = page.locator("nav");
  await first.getByRole("button", { name: /쇼츠 버전 보기/ }).click();
  await expect(first).toHaveAttribute("data-mode", "shorts");
  await nav.getByRole("button", { name: "Paper Feed", exact: true }).click();
  await expect(page.locator('.paper-card[data-mode="shorts"]')).toHaveCount(0);
  await nav.getByRole("button", { name: "Paper Shorts", exact: true }).click();
  await first.getByRole("button", { name: /초록 보기/ }).click();
  await expect(first).toHaveAttribute("data-mode", "papers");
  await expect(second).toHaveAttribute("data-mode", "shorts");
  await first.getByRole("button", { name: /쇼츠 버전 보기/ }).click();
  await expect(first).toHaveAttribute("data-mode", "shorts");
  await first.getByRole("button", { name: /초록 보기/ }).click();
  await first.locator(".paper-title").click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "쇼츠 버전 보기", exact: true })
    .click();
  await expect(first).toHaveAttribute("data-mode", "shorts");
  await first.getByRole("button", { name: /초록 보기/ }).click();
  await page
    .locator(".feed-tabs")
    .getByRole("button", { name: "Paper Shorts", exact: true })
    .click();
  await expect(page.locator('.paper-card[data-mode="papers"]')).toHaveCount(0);
  await nav.getByRole("button", { name: "Paper Feed", exact: true }).click();
  await expect(page.locator('.paper-card[data-mode="shorts"]')).toHaveCount(0);
  await first.getByRole("button", { name: /쇼츠 버전 보기/ }).click();
  await page
    .locator(".feed-tabs")
    .getByRole("button", { name: /^Papers/ })
    .click();
  await expect(page.locator('.paper-card[data-mode="shorts"]')).toHaveCount(0);
});

test("Explore tabs and independent panel scrolling keep playback in the viewport", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  await page
    .locator(".feed-tabs")
    .getByRole("button", { name: "Explore", exact: true })
    .click();
  const info = page.getByRole("complementary", { name: "Behind the short" });
  const reel = page.locator(".reel-shell");
  const pagination = page.locator(".reel-pagination > small");
  await expect(pagination).toHaveText("1 / 15");
  const before = await reel.boundingBox();
  await info.hover();
  await page.mouse.wheel(0, 650);
  await expect
    .poll(() => info.evaluate((el) => el.scrollTop))
    .toBeGreaterThan(0);
  await expect(pagination).toHaveText("1 / 15");
  expect((await reel.boundingBox())!.y).toBeCloseTo(before!.y, 0);
  await info.evaluate((el) => {
    el.scrollTop = el.scrollHeight;
  });
  await page.mouse.wheel(0, 650);
  await expect(pagination).toHaveText("1 / 15");
  expect(await page.evaluate(() => window.scrollY)).toBe(0);
  await reel.hover();
  await page.mouse.wheel(0, 500);
  await expect(pagination).toHaveText("2 / 15");
  await expect.poll(() => info.evaluate((el) => el.scrollTop)).toBe(0);
  expect((await reel.boundingBox())!.y).toBeCloseTo(before!.y, 0);
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await expect
      .poll(() =>
        page.evaluate(
          () =>
            document.documentElement.scrollWidth <= innerWidth &&
            document.documentElement.scrollHeight <= innerHeight + 1,
        ),
      )
      .toBe(true);
    if (width <= 760) {
      await expect(page.locator(".explore-tabs")).toBeHidden();
      await expect(
        page.getByRole("button", { name: "메뉴 열기" }),
      ).toBeVisible();
    } else {
      await expect(page.locator(".explore-tabs")).toBeVisible();
    }
    const bounds = await reel.boundingBox();
    expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(900);
    await page.screenshot({ path: `test-results/fixed-explore-${width}.png` });
  }
  await page
    .locator(".explore-tabs")
    .getByRole("button", { name: "Paper Shorts", exact: true })
    .click();
  await expect(page.locator(".paper-card")).toHaveCount(21);
  await expect(page.locator(".explore-workspace")).toHaveCount(0);
});
