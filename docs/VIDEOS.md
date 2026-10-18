# 기존 샘플 영상 연결

1. MP4를 `public/videos/meanflow-intuition.mp4`에 넣는다. H.264 video + AAC audio가 브라우저 호환성이 좋다.
2. `src/data/shorts.json`에 다음 항목을 추가한다. 여러 creator/설명 버전을 같은 `paperId`에 연결할 수 있다.

```json
[
  {
    "id": "meanflow-intuition-01",
    "paperId": "2505.13447",
    "creator": "your-handle",
    "title": "MeanFlow, visually explained",
    "style": "Visual intuition",
    "duration": 60,
    "videoUrl": "videos/meanflow-intuition.mp4",
    "thumbnailUrl": null
  }
]
```

3. 저장하면 Paper Shorts에 카드가 나타나고 Explore에서 실제 영상을 재생한다. 썸네일이 없으면 임시 타일이 표시된다.
4. 원하면 `public/thumbnails/...jpg`를 추가하고 `thumbnailUrl`을 `thumbnails/...jpg`로 지정한다.

`videoUrl`과 `thumbnailUrl`은 `https://...` 외부 URL도 지원한다. GitHub 프로젝트 Pages 하위 경로를 고려해 로컬 asset은 `public/`을 제외한 상대 경로를 쓴다. GitHub의 blob 보기 URL 대신 실제 MP4 응답을 제공하는 URL을 쓴다. 대용량 영상은 object storage에 두고 manifest만 커밋하는 편이 적합하다. 여러 영상의 id는 고유해야 하며 paperId는 papers.json에 존재해야 한다.

현재 manifest에는 `demo: true`, `videoUrl: null`인 가상 사용자 샘플 12개가 있다. 실제 영상을 연결할 때 항목을 추가하거나 샘플의 URL·creator를 교체하고 `demo`를 제거한다. `scripts/create_demo_shorts.py`는 실제 영상 항목을 보존하고 demo 항목만 재생성한다. 데모 generation은 localStorage에 영상 없는 preview만 만든다. 실제 MP4를 생성하거나 자동 업로드하지 않는다.

실제 연결된 샘플: `reference/flowmap_reel.mp4` → `public/videos/flowmap_reel.mp4`, 논문 `2610.20674`, 길이 83.6초. 썸네일은 18초의 실제 영상 프레임이다. 원본의 claims timeline은 첨부되지 않아 임의로 생성하지 않았다.

추가 실제 영상 (2026-10-18): Drifting 원문 `2602.04770v2`에 GPT‑5.4 mini / Claude Sonnet 5.5 baseline 2편을 연결했다. 각각 `public/videos/drifting-openai-baseline.mp4` (51.636초), `drifting-anthropic-baseline.mp4` (67.003초). 사용량·시간·근거 및 고정 템플릿 렌더러 한계는 [비교 보고서](experiments/drifting-baseline/README.md)에 있다.

Flow Map v2 실제 API 영상 2편을 같은 `2610.20674`에 추가했다: `flowmap-v2-openai.mp4` 77.600초(GPT-5.4 · Edited v2), `flowmap-v2-anthropic.mp4` 80.033초(Claude Opus 5.5). 각 썸네일은 실제 출력 프레임이며 원본 샘플과 함께 재생된다. [검증·비용·수동 보완 기록](experiments/flowmap-v2/README.md).
