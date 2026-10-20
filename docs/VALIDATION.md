# 통합 검증 기록 — 2026-10-18

> 최신 결과: Windows Docker Desktop 격리 렌더와 실제 API를 사용한 Flow Map v2 영상 2편을 생성·검증·연결했다. [실측 비용·시간·수동 보완 내역](experiments/flowmap-v2/README.md). 아래 초기 키 미설정 기록은 이전 시점의 검증 이력이다.

## 확인한 결과

| 검사                         | 결과                                                                                                                                                                                                                         |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 제공 MP4 probe               | H.264 / AAC, 1080×1920, **83.600초**                                                                                                                                                                                         |
| 제공 영상과 논문 매핑        | arXiv **2610.20674**, On the Stability and Convergence of Flow Map Training                                                                                                                                                  |
| 브라우저 실영상              | metadata 로드, 재생 시간 증가, 원 논문 제목 확인                                                                                                                                                                             |
| 논문 수집                    | 총 21편, 모든 metadata/첫 페이지 존재                                                                                                                                                                                        |
| 새 ingest                    | v1 고정, LaTeX+페이지별 PDF, Table 1 / (5) / C.1 포함                                                                                                                                                                        |
| golden 계약                  | 8 scenes / 28 facts, storyboard 게이트 통과                                                                                                                                                                                  |
| backend 자동 테스트          | 10개 통과: 인증, 비밀 값 비노출, 리소스 차단, atomic claim, cancel/retry, skipped validation 공개 금지, timestamp-source, quotes, golden schema, unsafe ids, model allowlist, OpenAI payload/usage, failed-validation resume |
| frontend 데이터 테스트       | 3개 통과                                                                                                                                                                                                                     |
| Playwright                   | 4개 통과: paper flow, mobile, demo feedback persistence, real playback & server prerequisites                                                                                                                                |
| TypeScript / Vite production | 통과                                                                                                                                                                                                                         |
| 비밀정보                     | backend/.env와 models/data는 gitignore, owner token이 dist JS에 없음을 확인                                                                                                                                                  |

## M0 실제 재생성

`backend/tools/run_golden.sh`로 변경하지 않은 원본 golden scenes와 대본에서 시작해 TTS → ASR → preview → final → composition → deterministic validation까지 한 번 실행했다. 기존 제공 MP4를 복사한 결과가 아니라 새 음성/새 렌더다.

- 결과: **84.333초**, **1080×1920**, H.264/AAC.
- 최종 장면 8개, 각 장면 `overrun_sec=0.0`.
- 대본의 길이 예측 84.4초.
- narration 97.8초, preview 53.8초, final 80.7초, compose 21.2초. 단계 합 약 **253.5초 (4분 14초)**. 설치/모델 다운로드 시간 제외.
- 실제 파일: `backend/data/golden-regression-01/out/short.mp4` (git 제외).
- 로그: 현재 환경 `/tmp/ss-golden-regression.log`.
- 영속 기록: [deterministic validation](validation/golden-validation.json), [scene render reports](validation/golden-render-report.json).
- `tools/verify_golden.py`에서 80–88초, 1080×1920, 8장면, overrun <0.3, 결정론 검사 통과를 assert한다.

레퍼런스의 keyless golden 동작을 유지하기 위해 trusted golden 모드에서는 `visual_review_executed`와 `claims_judged`가 skip 메모와 함께 통과로 기록된다. **이는 LLM 검증 통과가 아니다.** 서비스의 publish API는 skip 메모가 있는 보고서를 거절한다. API job은 trusted golden 모드를 사용할 수 없다.

## 미실행 / 후속 검증

- **M1:** 실제 GPT/Claude key가 없어 understand/storyboard 실호출, 3개 preset 비교, 실제 LLM token/cost 미측정. provider adapter는 fake response 단위 테스트만 수행.
- **M2:** 원문과 source.quote exact matching 실행 가능. 정교한 수식·표 semantic parser, 길이가 큰 논문의 chunked extraction은 미구현. source 구조는 raw LaTeX와 페이지 텍스트를 보존.
- **M3:** 새 visual_code, 실제 vision review/judge 및 자동 코드 수정 루프 미실행. 제공된 golden code만 실행.
- **M4:** API/큐/worker 코드·상태·프론트 연결 구현. 키와 Docker가 없어 웹 요청부터 LLM 생성→격리 렌더→publish 전체 E2E는 미실행.
- **M5:** P0 UI 및 모델 선택, 키/renderer 미준비 차단 확인. 다른 설정의 실제 영상 2개 생성은 미실행.
- **M6:** 게시 결과 timestamp→line→fact 신고 API 구현 및 테스트. 제공 MP4에는 첨부 timeline이 없어 이 파일의 근거 시간표는 연결하지 않음. 신고 UI·preset fork·다중 사용자 기능은 후속 작업.
- **Docker:** CLI/daemon 없음. 새 renderer Dockerfile의 build/run은 미검증. keyless regression은 byte-identical golden scenes만 허용하는 local 경로로 실행.

## 원본 대비 필수 보완 사항

- OpenAI Responses provider 추가, Claude timeout/retry·truncation 확인.
- source ingest, model/revision별 공유 사실 캐시와 원문 quote gate 추가.
- generated Python의 keyless/networkless Docker 실행 경계 추가.
- 비용을 모르는 경우 무료로 표시하지 않음. UI에는 토큰 사용량과 가격표 미설정을 표시.
- 검증 JSON이 이미 있는 job을 재시작해도 실패를 `published`로 바꾸지 않음.
- judge 응답의 line coverage 및 schema 확인, API 공개 시 skipped check 거절.
- path로 쓰이는 line ID 제한, 중복 scene ID 거절.
- 모든 정상 생성은 `needs_review`로 보관 후 explicit publish.

이 보완으로 stage 순서·render layout·golden scene 자체를 바꾸지 않았다.

## Reference v2 integration (2026-10-18)

- Backend tests: 20 passed, including cache-boundary preservation, v2 motion validation, persistent uncertain-cost reservations, and bridge exclusion of env files.
- Browser tests: 7 passed; inline flip preserves the other 20 papers. Grid/viewport checks passed at 320, 390, 768, 1440 px. Mobile grid was additionally rechecked after narrowing tile minimum width.
- V2 golden regression: unchanged reference scene code, reused previously validated narration, new layout checks + preview/final render + composition + validation. Preview 56.1 sec, final 92.9 sec, composition 23.7 sec. M0 checks pass; no paid API calls. Evidence under `docs/validation/v2/`.
- Windows bridge and live API v2 comparison subsequently completed; see the actual-run section and linked evidence below.

## 실제 v2 실행 완료

- GPT 편집 보완본 77.600초 / Claude 검토본 80.033초. 모두 1080×1920, 30fps, H.264/AAC.
- Windows renderer Docker image build와 networkless render 실제 실행 확인. 생성된 Python을 개발 컨테이너에서 실행하지 않았다.
- LLM 대본/코드/vision QA/judge 실제 호출 및 수정 루프 실행. 공통 facts는 ZIP 결과를 재사용하고 원문 대조 후 누락 근거를 보충했으며, 이해/사실 추출 단계를 새로 유료 실행한 실험은 아니다.
- GPT 결과는 수동 편집과 독립적인 Sonnet 화면 재검토를 포함한다. 원본 품질과 동등함을 검증한 결과나 무개입 모델 벤치마크가 아니다.

- 최종 데이터 테스트 3개, backend 테스트 20개, production build 통과. 브라우저 시나리오 8개 통과(새 계정명과 기존 baseline 계정명의 부분 일치 때문에 Drifting locator를 논문 카드로 한정한 뒤 해당 시나리오 재실행). 새 GPT/Claude 영상 모두 재생 시간이 실제로 증가하는지 확인했다.

## 2026-10-20 Email Digest Preview

- Legacy Git tag and local bundle verified at commit `7708aaf` before changes.
- `npm test`: 3 passed. Production build passed.
- Existing browser regression suite: 8 passed; new digest interaction test passed. Responsive digest test caught a 320px sender-date overflow, fixed by accounting for the left margin; both digest tests then passed at 320/390/768/1440px.
- Checked screenshots at 390px and 1440px. Beige/cream/orange email styling remains scoped to digest components.
- Served built assets beneath `/paper_reels/`: direct `#/digest-preview` entry, reload, 4 cards and actual video metadata loading succeeded without browser page errors.
- No emails sent; no subscriptions changed; no model/API generation calls made. Recommended scores and totals are illustrative; papers use existing source-backed catalogue metadata.
- Initial browser test attempt had connection-refused errors because the dev server was stopped; restarted Vite at 0.0.0.0:5173 before the successful checks above.

## Demo style redesign

- Backup: `.cache/backups/before-demo-styles-20261020-155804.tar.gz` includes tracked and non-ignored untracked project files before this edit (including earlier uncommitted UI changes).
- All five real video manifest entries compared equal to the pre-edit snapshot; SHA-256 of all five MP4 and five thumbnails unchanged.
- Desktop and 390px MeanFlow cards visually inspected: style badges, unique hooks, conceptual artwork and descriptive labels readable.
- `npm test`: 3 passed. Production build passed. Existing browser regression suite also checks original/sample playback and digest interactions.

## Fixed Explore workspace

- Unit checks (3) and production build passed; prior 12 browser tests passed.
- New wheel-isolation test passed: panel scroll changes scrollTop without changing the video, panel-bottom wheel does not leak, outside wheel changes the video and resets panel scroll, video stays in place.
- 320/390/768/1440px viewport bounds checked; desktop and fresh mobile screenshots inspected. After mobile text adjustment, mobile and wheel-isolation tests passed again.

## Release: consumer discovery and digest

Explore video margins increased to 36px per side on desktop and 20px on mobile. Real video entries and all ten associated media files still match the pre-redesign snapshot. Pre-push credential-pattern scan found no matches in tracked/non-ignored project files; env/runtime/backups remain ignored.

## Unified Explore media frame

Removed Explore tabs at all widths; paper-feed tabs remain. Actual MP4 and demo art share a container-sized 9:16 frame and common caption placement. A missing explicit width on the flex main initially caused size-contained video columns to collapse to zero; assigning main width:100% fixes this. Regression coverage checks positive frame dimensions and identical x/y/width/height before/after real→demo→loaded-real transitions at 390/768/1440/1920/2560px. Original media and metadata remain unchanged.

## Explore TL;DR and paper Q&A

- All 21 source-backed papers have a concise AI-authored TL;DR and explicitly static, abstract-grounded example question/answer with original source links.
- `npm test`: 4 passed; `npm run build`: passed; `npm run test:e2e`: 15 passed.
- Browser checks cover requested panel order, abstract modal, original PDF URL, style badges, question persistence across perspectives/reload, isolation between papers and independent per-short evaluations.
- Custom questions display a pending/unconnected notice; no live LLM responses or public sharing are claimed. No API calls or costs incurred.
- Desktop screenshot inspected; responsive and wide-screen frame regression tests passed. All original real-media entries and ten assets unchanged.

## English discussion and body-grounded insights

- Rechecked all 21 TL;DRs and seeded answers against the original cached PDFs' supporting body sections; recorded section/page references and PDF hashes in paperInsights.json. See PAPER_INSIGHTS_REVIEW.md for scope and important corrections.
- Removed verbose prototype/source captions; conversation shows a seeded Researcher handle, Q. prefix and AI answer. Legacy test questions are cleared on Explore entry, while new questions persist in v2 storage.
- Genre badges use explanation style rather than model names; added discussion/perspectives divider and rating-note spacing.
- `npm test`: 4 passed. Production build passed. `npm run test:e2e`: 16 passed, including migration, English text, genre labels and wide/mobile frame checks.
- Desktop conversation screenshot reviewed. Original five video records and all ten video/thumbnail assets still match the protected snapshot.
