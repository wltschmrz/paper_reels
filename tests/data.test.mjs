import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
const papers = JSON.parse(
  readFileSync(new URL("../src/data/papers.json", import.meta.url)),
);
const shorts = JSON.parse(
  readFileSync(new URL("../src/data/shorts.json", import.meta.url)),
);
test("21 real papers with unique IDs, provenance, abstracts and local PDF previews", () => {
  assert.equal(papers.length, 21);
  assert.equal(new Set(papers.map((p) => p.id)).size, 21);
  for (const p of papers) {
    assert.match(p.id, /^\d{4}\.\d{4,5}$/);
    assert.ok(p.title.length > 10);
    assert.ok(p.abstract.length > 100);
    assert.ok(p.authors.length);
    assert.match(p.date, /^\d{4}-\d{2}-\d{2}$/);
    assert.equal(p.url, `https://arxiv.org/abs/${p.id}`);
    assert.equal(p.pdfUrl, `https://arxiv.org/pdf/${p.id}`);
    assert.ok(p.fetchedAt);
    assert.ok(p.preview);
    const image = readFileSync(
      new URL(`../public/${p.preview}`, import.meta.url),
    );
    assert.equal(image.subarray(1, 4).toString(), "PNG");
    assert.ok(image.length > 10000);
  }
});
test("video manifest references valid papers and playable asset paths", () => {
  assert.equal(new Set(shorts.map((s) => s.id)).size, shorts.length);
  for (const s of shorts) {
    assert.ok(papers.some((p) => p.id === s.paperId));
    assert.ok(s.creator && s.title);
    assert.ok(s.duration > 0);
    for (const path of [s.videoUrl, s.thumbnailUrl].filter(Boolean)) {
      assert.ok(
        /^https:\/\//.test(path) ||
          existsSync(new URL(`../public/${path}`, import.meta.url)),
      );
    }
  }
});

test("real Flow Map video is attached only to its original paper", () => {
  const s = shorts.find((s) => s.id === "flowmap-reference");
  assert.equal(s.paperId, "2610.20674");
  assert.equal(s.demo, false);
  assert.equal(s.duration, 83.6);
  assert.ok(s.videoUrl.endsWith("flowmap_reel.mp4"));
});
