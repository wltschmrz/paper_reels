# ScholarShorts — 프로젝트 기준 문서

> One Paper, Multiple Perspectives. 하나의 논문, 여러 설명 방식.
>
> 2026-10-18 사용자 브레인스토밍 및 제공한 「PROJECT CONCEPT & MVP DEVELOPMENT PLAN · 2026.10」를 정리한 장기 참조 문서. 원문의 반복 설명과 붙여넣기된 Mermaid CSS는 제외했으며, 제품 의도·주요 요구사항·후속 계획을 보존했다. 원문 전체의 verbatim 보관본은 아니다.

## 1. 요청 배경과 개발 원칙

새 GitHub 레포 `wltschmrz/paper_reels`에서 대학원 수업 / CHI 스타일 HCI 프로젝트용 MVP와 웹 프로토타입을 만든다. 현재 개발 환경은 Windows 호스트 안 Docker Linux 컨테이너다. 사용자가 웹의 변화를 실시간 확인하고 피드백할 수 있어야 한다. 이 문서를 루트에 보존해 후속 개발에서도 처음 의도를 유지한다.

- Scholar Inbox 형태의 논문 탐색과 사용자별 AI Shorts 제작을 결합한다.
- 실제 MeanFlow / Drifting 계열 및 관련 기초 연구 약 20편을 직접 수집한다. 제목, 저자, 초록, 날짜, 첫 페이지 PDF 이미지, 원문 링크를 포함한다.
- 썸네일은 임시 또는 공란, 영상은 공란으로 둔다. 사용자의 기존 샘플 MP4는 나중에 레포 파일 또는 외부 URL로 연결한다.
- 초기 인터랙티브 데모와 실제 AI 생성 기능을 명확하게 구분한다. 가짜 영상을 실제 결과로 표시하지 않는다.
- GitHub Pages에서는 정적 프론트엔드를 제공하고, 추후 Python API와 worker는 별도로 연결한다.
- 현재 프로토타입은 실제 비용 청구·사용자 인증·서버 저장 없이 브라우저 상태로 동작한다.

## 2. 문제와 핵심 가치

연구자는 매일 공개되는 많은 논문을 제한된 시간에 탐색한다. 제목, abstract, figure preview 중심 피드는 유용하지만 텍스트 이해 부담이 남는다. 제목을 보고 관심은 생겨도 초록 전체를 읽지 않는 경우가 있다. 원문을 읽기 전에 짧은 시각적 설명으로 핵심을 파악하고 더 읽을 가치가 있는 논문을 찾도록 한다.

핵심은 paper-to-video 자동화 자체보다 **사용자가 논문을 이해하는 방식을 만들고 공유하며 자신에게 맞는 설명을 발견하는 구조**다.

- Paper-centric multi-video: `Paper 1:N Short`. 한 논문 아래 다양한 창작자의 여러 영상.
- Creator-centric personalization: 설명 스타일과 모델 구성을 선택하고 creator를 follow.
- Community-based quality selection: 이해도, 정확성, 시각화, 오류·한계 누락을 평가.
- Dual discovery: paper-first 또는 video-first로 시작해 원문으로 연결.
- 모든 사용자는 viewer이면서 AI-assisted creator가 될 수 있다.
- 좋은 프롬프트·프리셋을 가진 creator의 설명을 반복 소비하고 구독할 수 있다.

관련 맥락: Scholar Inbox의 개인화 피드·평가·하이라이트·프리뷰·컬렉션·semantic search. 사용자 제공 계획은 PaperTok을 CHI 2026 선행연구로 언급한다. **PaperTok의 서지·기여·발표 정보는 proposal 작성 전에 원문을 별도로 검증해야 한다.** 현재 문서는 사용자 연구 방향을 기록하며 확인되지 않은 선행연구 사실을 확정하지 않는다.

## 3. 세 가지 주 화면

### Paper Feed — traditional / text-first

논문 제목, 저자, 공개일, venue(확인된 경우), 주제, 초록, 실제 첫 페이지 이미지. 관심/비관심, 북마크, 컬렉션, 원문/PDF, Generate Short, 연결된 실제 영상 수를 제공한다. Shorts가 전혀 없는 cold start에서도 논문 탐색은 가능해야 한다.

### Paper Shorts — paper-centric

**Paper Feed와 동일한 논문 목록·검색·주제 필터·정렬 상태를 공유한다.** 논문 제목과 topic 아래 여러 creator의 썸네일·설명 스타일·길이·평가를 보여준다. 영상이 없는 논문에는 첫 설명 만들기 empty state를 표시한다. 논문 하나가 여러 Shorts를 포함하는 정보 구조를 유지한다.

설명 예시: Mathematical Intuition / Quick Research Summary / Beginner-Friendly Explanation / Critical Review. 한 논문을 여러 관점으로 비교·선택할 수 있어야 한다.

### Explore — shorts-centric

한 번에 하나의 vertical Short. 스와이프·스크롤·방향키·명시적 이전/다음 버튼. 실제 URL을 연결하면 HTML video로 재생한다. 좋아요/싫어요, 북마크, 댓글, creator follow, 원문·초록·PDF, 같은 논문의 다른 설명으로 이동한다. 장기적으로 관심 topic 및 follow 신호로 개인화한다. 초기에는 공란 상태와 데모 프리뷰를 정직하게 표현한다.

## 4. 주요 사용자 흐름

1. Discover → Generate → Publish: 논문 선택 → 스타일·preset·모델 설정 → job 제출 → background generation → validation → 게시 → 논문/탐색 피드 반영.
2. Watch → Evaluate → Discover: 영상 → 논문 상세 → 다른 설명 비교 → 평가/토론 → 원문 또는 collection.
3. Find Creator → Follow → Personalize: 선호하는 creator 발견 → 프로필과 기존 콘텐츠 → follow → 우선 추천.

첫 vertical slice: Paper Feed → Generate Short 설정 → progress → Paper Shorts의 새 preview → Explore → 평가/원문. 데모에서는 약 20초 simulation 뒤 **영상 없는 데모 preview**만 추가한다. 실제 MP4 생성을 가장하지 않는다.

## 5. AI Generation Studio

### 설명 선호

- 대상: Beginner / Graduate Student / Expert.
- 접근: Intuition / Mathematical / Implementation / Critical Review.
- 구성: Problem → Method → Results → Limitations.
- 초점: Theory / Equations / Experiments / Visual intuition.
- 언어: Korean / English.
- 길이: 기본 60초, 30–90초. 초기 구두 설명 중 10분 언급은 이후 상세 계획의 기본 60초를 따른다.
- speaking pace / visual density.
- 자연어 지시: 수식의 의미를 충분히 설명하기, 기존 연구와 차이 강조하기, 복잡한 수식은 오래 보여주기 등.
- 참고 설명 방식: 3Blue1Brown, 한국 AI 설명 채널 인커밋처럼 시각적 수학·통계·AI 설명. 공식 협업이나 동일 스타일 재현을 주장하지 않는다.
- 개인 preset 저장: Mathematical Deep Dive / Fast Abstract / Critical Reviewer 등. 장기적으로 공개/비공개.

### 모델 및 툴

Paper Understanding LLM → Script / Storyboard LLM → Coding LLM / Manim / LaTeX → TTS (gTTS 등) → Manim rendering → FFmpeg composition → thumbnail / captions → validation.

대본과 animation code를 다른 모델로 완전히 분리하면 정합성이 깨질 수 있으므로 공유된 storyboard/scene schema와 컨텍스트를 유지한다. 사용자는 단계별 모델 구성과 비용을 확인하도록 한다. MVP는 기본 pipeline을 먼저 검증하고 임의 모델 builder는 나중에 만든다. 프론트엔드 데모에서는 실제 모델 공급자/API를 확정하지 않은 설정 예시만 사용한다.

## 6. 실제 비동기 파이프라인 계획

입력: PDF/arXiv ID + 사용자 선호 + model configuration.

1. Paper Understanding: 제목·초록·본문·수식·그림 추출. Problem, Method, Contributions, Results, Limitations 구조화. 주요 주장에 원문 section/page 기록.
2. Script & Storyboard: opening hook, narration, scene별 duration, 수학 시각화. 1분 영상은 예시로 15fps에서 약 900 프레임이나 실제 fps/timing은 음성에 맞춰 결정한다.
3. Animation Code: Manim/Python/LaTeX, diagram/graph/geometric animation. 렌더 실패 시 제한된 재시도.
4. Voice & Rendering: TTS, audio/scene timing 정렬, Manim 이미지/영상, FFmpeg MP4, 자막, 썸네일.
5. Validation & Publication: 원문과 주요 claim·수치·수식 대조, unsupported claim 검토, transcript/source 저장. 성공한 asset만 paper/creator와 연결. validation 결과 및 publication status에 따라 게시.

사용자가 실험한 Claude Max 기반 생성은 약 30분 소요. 동기 HTTP 요청에 묶지 않고 별도 worker와 영속 job queue로 분리한다. API 키는 서버에만 둔다. 사용자 입력과 생성 코드는 sandbox worker에서 실행해야 한다. timeout/retry/cancel/idempotency와 실패 기록이 필요하다.

## 7. 커뮤니티, 추천, 비용

Short feedback: Easy to Understand / Accurate Explanation / Good Visualization / Misleading or Incorrect / Missing Important Limitations. 일반 좋아요·싫어요와 분리할 수 있다. 댓글은 장기적으로 timestamp/원문 section 연결.

Creator: published Shorts, presets, followers/following, explanation quality, research interests. 프로필을 통해 설명 스타일을 알 수 있어야 한다.

초기 추천은 관심 topic, follow creator, quality, relevance, recency의 간단한 규칙. 장기적으로 시청 완료·북마크·원문 방문. watch time만 최적화하지 않고 정확성과 topic diversity를 고려한다. 현재 데모의 For you는 관심 topic만 반영하며 실제 학습 추천이 아니다.

시청/기존 영상 탐색 무료, 생성 요청자가 usage-based credits 부담을 고려. 실제 API 및 rendering usage 기록과 estimated cost breakdown. MVP는 결제·정산 제외. 화면 비용은 **예시 demo credits**이며 실제 요금 아님.

## 8. 설계 원칙

Accessibility: 처음 접하는 사용자도 접근 가능. Personalization: 배경과 취향 반영. Creator Agency: 설명과 모델 구성에 사용자 통제. Scientific Fidelity: 재미가 정확성을 훼손하지 않음. Traceability: 원문 주장 추적. Community Intelligence: 좋은 설명을 평가와 상호작용으로 발견.

## 9. 아키텍처와 데이터

현재: React + TypeScript + Vite, 독립 CSS, 로컬 JSON metadata / assets, localStorage. Tailwind는 필수 요구가 아닌 추천 stack으로 보고 CSS 토큰 기반으로 구현했다. 추후 Supabase Auth/Postgres/Storage, FastAPI, Python worker, queue, Manim/LaTeX/TTS/FFmpeg 연결.

| Entity        | 주요 필드                                                                                     |
| ------------- | --------------------------------------------------------------------------------------------- |
| Paper         | id, title, authors, abstract, date, topics, arxiv_id, pdf_url, preview, provenance            |
| User          | id, handle, interests, following                                                              |
| Preset        | id, creator_id, style_prompt, model_config, audience, language, duration                      |
| Short         | id, paper_id, creator_id, preset_id, video_url, thumbnail_url, transcript, publication_status |
| GenerationJob | id, paper_id, user_id, preset_snapshot, status, progress, cost, error                         |
| Interaction   | user_id, paper_id/short_id, reaction, bookmark                                                |
| Collection    | id, user_id, name; CollectionPaper join                                                       |
| Comment       | user_id, short_id, timestamp, source_section, content                                         |

핵심 relation: Paper 1:N Short; User 1:N Short. 데모는 인증 없는 local user다. 실제 서비스 전환 시 server-side auth와 row-level permissions가 필요하다.

## 10. 단계와 후속 작업

### P0: interactive demo — 10/23 proposal

실제 논문 약 20편(제공 계획의 5–10편에서 이번 직접 요청에 따라 확장), 세 화면, 설정 modal, 생성 simulation, 샘플 영상 등록 구조, 지속되는 local state, 반응형 UI, Windows Docker preview, GitHub Pages workflow.

현재 실제 영상 파일은 비어 있으며, 후속 요청으로 가상 사용자 및 썸네일이 있는 데모 Shorts를 추가했다. 최종 발표에는 기존 샘플 5–8편을 연결할 수 있다.

### P1: working generation — 10월 말–11월

기존 Claude pipeline을 받아 1편의 Generate → job → LLM/Manim/TTS → MP4 storage → validation → feed 실제 동작을 완성한다. preset 2–3개, 인증과 영속 DB, 실제 API usage, retry/cancel.

### P2: community / HCI evaluation — 11–12월

creator profile, server-backed follow/reaction/comment/bookmark, 규칙 기반 추천, user study. 현재 로컬 반응은 실제 community가 아니다.

초기 scope 제외: production payment, 대규모 추천, 자유로운 pipeline builder, 전체 arXiv 지속 수집, 실시간 render preview.

## 11. HCI research framing

RQ1: Short-form AI explanation이 abstract-first 탐색과 비교해 discovery efficiency와 comprehension에 어떤 영향을 주는가?
RQ2: 동일 논문의 여러 personalized explanations가 단일 설명보다 perceived usefulness와 understanding을 높이는가?
RQ3: creator identity, 설명 style, community feedback이 content selection과 trust에 어떻게 영향을 주는가?

수업에서는 RQ1과 RQ2를 우선한다. 8–12명 within-subject design으로 Abstract-first / Single AI Short / Multi-Short Choice 조건을 비교한다. 비교 가능한 논문과 난이도를 선정하고 연구 배경을 기록한다. 논문 순서와 조건 순서를 counterbalance한다. task time, comprehension score, confidence, perceived cognitive load, 원문 클릭 의향을 측정한다. 단순한 재미보다 설명을 선택하는 권한이 이해와 탐색을 개선하는지 평가한다. 연구 시행 시 동의 및 데이터 보관 범위는 소속 기관 지침에 맞춰 결정한다.

## 12. 일정 (사용자 제공)

| 일정              | 결과물                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------- |
| 10/18–10/20       | concept, UI, related work, wireframe                                                        |
| 10/21–10/22       | React demo, sample Shorts 연결                                                              |
| 10/23             | Midterm Proposal: users, problem, related work, design goals, sketches, model choice, study |
| 10월 말–11월 중순 | backend generation integration                                                              |
| 11월 중순–12월 초 | community + study                                                                           |
| 12/16             | 10분 발표 + interactive demo                                                                |
| 12/23             | 최대 6쪽 CVPR format report, repository, 30초–2분 video figure                              |

10/23은 명확한 연구 framing과 설득력 있는 high-fidelity prototype을 목표로 한다.

## 13. 후속 개발 체크

기능 추가 전 이 문서와 `docs/ARCHITECTURE.md`를 읽는다. 세 화면의 구별, paper-centric relation, shared filtering, 빈 영상과 실영상 구별을 유지한다. 새 결정은 해당 절에 기록한다. 연구 주장은 원전을 확인하고 생성 요약과 원문 abstract를 구별한다. 소스 URL과 수집 날짜를 보존한다.

## UI 피드백 반영

- 논문 정보의 가독성을 우선해 Paper Feed / Paper Shorts 상단 소개 문구와 홍보 배너를 제거한다. 페이지 진입 시 검색·필터·논문 목록을 바로 보여준다.
- Your interests는 페이지 본문에서 제거하고 상단 오른쪽 Y 버튼을 대체한다. 관심 분야 설정 기능은 유지한다.

- 추가 요청: 가상 사용자 8명의 샘플 Shorts 12개를 7편의 논문에 연결한다. 직접 만든 SVG 썸네일을 제공하되 videoUrl은 null로 유지하고 DEMO 표시를 한다. 클릭 시 평가와 항상 열린 댓글 입력창을 제공한다. 평가는 실제 콘텐츠 품질 집계가 아닌 브라우저 데모 상태다.

- 썸네일 디자인 피드백: 도서 표지 느낌 대신 9:16 릴스형 고대비 컬러·대형 한국어 후킹 제목을 사용한다. 제목·계정명은 썸네일 박스 안에 통합한다. 일부는 3Blue1Brown을 참고한 어두운 배경의 수식·곡선·벡터 시각화를 사용하며 공식 채널/실제 제작자 콘텐츠로 표시하지 않는다.

## 실제 파이프라인 통합 (2026-10-18)

- `reference/PIPELINE.md`, `scholarshorts-pipeline.zip`, `flowmap_reel.mp4`를 사용자 제공 원본으로 보존한다. ZIP은 `backend/`로 옮겨 구현 기반으로 사용한다.
- 실제 샘플의 논문은 arXiv:2610.20674, On the Stability and Convergence of Flow Map Training. 기존 MeanFlow 논문에 잘못 붙이지 않는다. 논문은 총 21편이다.
- 실파일 검사: 83.6초, 1080×1920, H.264/AAC. 정적 영상/썸네일을 public에 연결한다. 원문의 회귀 생성 측정값과 구별한다.
- 사용자 요청에 따라 FastAPI + SQLite queue + 별도 worker, GPT Responses와 Claude Messages provider, source ingest, 공유 facts cache, owner API-key env, frontend 실제 생성 모드를 추가했다.
- 단계 순서·render kit·데이터 계약을 유지한다. 추가 계약 검증은 line_id 경로 문자 제한, scene 중복 차단이다. 미검증 judge skip를 실서비스 통과로 보지 않는다. 통과 렌더도 기본 수동 검토 후 게시한다.
- 모델 선택보다 P0 설명 관점·필수 섹션·수식 깊이·대상·길이를 먼저 노출한다.
- API 키는 아직 미등록. LLM 및 Docker 격리 경로는 미실행. 개인 owner 개발용이며 멀티유저 BYOK/프로덕션 배포로 표현하지 않는다. 설정은 docs/BACKEND.md, 검증은 docs/VALIDATION.md 참고.

## 2026-10-18 추가 요구: reference v2와 인라인 카드

- `PIPELINE (2).md` / `scholarshorts-pipeline (2).zip`의 토큰 비용 효율화와 시각적 품질 향상 모두 통합한다.
- Flow Map 원 논문으로 GPT/Claude 실제 Manim 영상 각 1개를 생성하여 사용자가 올린 원본과 비교한다. 고정 템플릿 영상으로 대체하지 않는다. 제공 근거 목록은 공유하며 대본 이후는 별도 생성한다. 비용 상한/usage 기록을 유지한다.
- Abstract 화면의 카드에서 해당 논문만 뒤집어 Shorts 버전을 보여준다. 별도 목록 페이지로 이동하거나 다른 논문을 숨기지 않는다.
- Your Perspective 생성 타일은 마지막 행에 여유가 있을 때만 표시한다. 생성 버튼은 타일 유무와 관계없이 남긴다.
- 창 폭에 따라 카드 그리드를 조절하고 휴대폰에서도 가로 넘침 없이 제공한다.
- Windows Docker Desktop `desktop-linux`, 개발 컨테이너 `cuda13-dev`. 파일 큐 브리지로 별도 격리 렌더 컨테이너를 사용한다. Docker daemon TCP 공개나 기존 개발 컨테이너 재생성은 하지 않는다.

## 실제 Flow Map v2 비교 결과 보존

2026-10-18: Windows Docker Desktop 파일 큐 bridge에서 네트워크 없는 컨테이너로 생성 코드를 실행해 GPT 편집 보완본(77.600초)과 Claude 검토본(80.033초)을 같은 Flow Map 논문에 연결했다. 원본 제공 영상(83.6초)은 그대로 유지한다. reference (2)의 비용 효율·영상 품질 개선을 모두 적용했지만, 두 새 영상은 검토·수동 보완을 포함하므로 무개입 모델 비교로 제시하지 않는다. 비용·경과 시간·원문 근거 보충·최종 소스와 검증 기록은 `docs/experiments/flowmap-v2/`에 보관한다. 실제 신규 facts 추출은 이번 비교에서 재실행하지 않았다.

## 2026-10-20 방향 전환: 공급자 제작 + 개인화된 소비

이 결정은 위의 creator-first 서비스 계획보다 우선한다. 기존 MVP는 legacy로 보존하고 단계적으로 전환한다.

- 서비스 제공자가 논문별로 여러 설명 버전을 제작한다. 일반 사용자가 프롬프트를 작성하거나 생성 작업을 요청해야 하는 부담을 줄인다.
- 사용자는 관심 분야와 선호하는 설명 스타일을 선택해 추천 영상을 받는다. Paper 1:N Short는 유지한다.
- 기본 스타일: 직관적인 casual / 기하·시각적 설명(3Blue1Brown 참고) / 수학·수식 중심 formal. 목표 길이 1–3분, 한국어·영어 및 light/dark variation을 계획한다. 이 설정의 실제 영상 변형은 아직 구현하지 않았다.
- 일별 이메일은 relevance score, 논문 제목, 저자와 원문·Shorts 진입을 간결한 목록으로 제공한다.
- 현재 작업은 독립 Email Digest Preview만 추가한다. 기존 생성 UI, 피드, 백엔드와 모델은 그대로 둔다. 실제 이메일 발송·구독·인증·스케줄러·추천 학습은 범위 밖이다.
- `#/digest-preview`: 기존 출처 있는 논문 4개, 예시 점수 96/93/88/87 및 수집 규모 68/1,995. 날짜 2026-10-20은 이메일 시연 날짜이며 논문 출판일과 별개다. 최신 논문 실시간 추천으로 오해하지 않도록 화면에 명시한다.
- 제공된 발표 조사 보고서의 통계·서비스 비교·라이선스 주장과 연구 논문 요약은 이번 UI 작업에서 검증하지 않았다. 발표 자료에 확정 사실로 사용하기 전에 원출처 확인이 필요하다.
- 후속 사용자 연구: AI 연구자 8–12명, 현실적인 baseline(직접 프롬프트 등)과 비교, 조건·논문 순서 counterbalancing, 사후 인터뷰. 시간·이해도·관련성·성공 결과 수와 적절한 표준 설문(NASA-TLX/SUS/CSI 중 목적에 맞게 선택), 주제 분석을 계획한다. 선택적 formative study는 5–6명 인터뷰/관찰이다. 연구 결과는 아직 없다.

### 후속 수정: 일반 사용자 생성 진입 제거

사용자 확인에 따라 Generate Short / Create Your Version / Your Perspective 타일, Creator Studio, 생성 작업 및 제작 유도 안내를 일반 사용자 화면에서 제거한다. 영상이 없는 논문은 비대화형 준비 안내를 표시한다. 기존 브라우저 생성 job/preset 데이터는 삭제하지 않되 소비자 피드에는 더 이상 합치지 않는다. 공급자용 backend 파이프라인과 legacy 구성 파일은 유지한다.

- Email Digest Preview 진입은 상단 Research prototype과 Your interests 사이에도 제공한다. 모바일은 접근성 이름을 유지한 메일 아이콘으로 축약한다. 이메일 디자인은 기존 beige/orange 명세 대신 ScholarShorts white/teal/연한 mint 팔레트를 사용한다. 제목 날짜는 `20 Oct 2026`으로 표기한다.

### 2026-10-20 데모 썸네일의 세 설명 관점

- 실제 영상과 연결된 썸네일·manifest 5개는 그대로 보존한다. 변경 대상은 demo=true, videoUrl=null인 기존 12개뿐이다.
- 분류: Intuition(비유·핵심 아이디어), Geometry(곡선·벡터·공간의 움직임), Mathematics(수식·가정·유도). 난이도 등급이 아닌 설명 관점이다.
- 후킹을 스타일별 질문 템플릿으로 고정하지 않는다. 각 논문의 출처 있는 초록에서 특색을 뽑고 질문·주장·대비를 섞는다. 예: MeanFlow의 한 번 생성/평균 벡터/속도 항등식, iMF의 자기 의존 타깃/유연한 guidance, Drifting의 학습 중 이동/분포 변화/평형, Sinkhorn의 식별성.
- 황금색/민트/보라색뿐 아니라 아이콘·스타일명·설명 부제를 표시한다. 썸네일은 개념도이며 원문 그림이나 완성 영상으로 표시하지 않는다.
- 수정 직전 미커밋 변경을 포함한 프로젝트 파일은 `.cache/backups/before-demo-styles-20261020-155804.tar.gz`에 보관했다. ignored env/runtime 데이터는 제외했다. 실제 미디어 10개 SHA-256과 manifest 비교를 통과했다.

### Drifting baseline 숨김 및 스타일 공란

- Drifting의 직접 만든 두 baseline(`drifting-openai-baseline`, `drifting-anthropic-baseline`)은 소비자 피드/Explore/이메일에서 숨긴다. manifest와 MP4·썸네일 파일은 삭제·수정하지 않는다.
- 공개된 실제 영상이 없는 논문에서 미제작 스타일 슬롯을 표시한다. 기존 데모 시안이 있는 스타일은 그 썸네일을 유지하고, 없는 스타일만 Intuition / Geometry / Mathematics 점선 카드로 채운다. 실제 영상이 있는 Flow Map 카드는 보존한다. 점선 카드는 생성 버튼이 아니다.
- 필터 전환 시 카드 폭이 재분배되지 않도록 desktop grid는 190px, mobile은 반응형 2열로 구성한다. scrollbar gutter를 예약한다.

스타일 슬롯의 최종 순서는 **Intuition → Geometry → Mathematics (I → G → M)**다. 빈칸도 원래 스타일 위치에 두고, 뒤로 몰아넣지 않는다. 이 정렬은 미제작 데모/공란에 적용하며 실제 Flow Map 영상의 순서는 유지한다.

Paper Feed와 Paper Shorts 모두 개별 카드의 초록/쇼츠 양방향 전환을 지원한다. sidebar 또는 상단 feed tab에서 Paper Feed/Paper Shorts를 선택하면(같은 페이지 재선택 포함) 개별 뒤집힘을 초기화한다. 검색·주제·정렬은 유지하며 페이지 기본 보기로만 통일한다.

Explore는 메인 상단 Papers / Paper Shorts 옆에서도 접근한다. Explore에서는 화면 높이를 고정하고 Behind the short를 독립 스크롤 패널로 제공한다. 설명 패널 안의 wheel은 본문만 스크롤하며 끝에서도 쇼츠를 넘기지 않는다. 패널 밖 Explore 영역의 wheel은 다음/이전 쇼츠로 전환한다. 모바일은 영상/액션 위, 독립 설명 패널 아래의 고정 화면 구성이다.

Explore의 쇼츠 위아래 여백은 최종 desktop 각각 36px, mobile 각각 20px로 조정한다. 독립 설명 패널과 wheel 전환은 유지한다.

모바일에서 쇼츠 크기 확보를 위해 상단 Papers/Paper Shorts/Explore 탭을 숨기고 햄버거 내비게이션을 사용한다. Explore 영상 여백은 각각 8px로 줄이고, 영상/설명 패널 높이 비중은 65%/35%로 조정한다. Desktop은 그대로 유지한다.

모바일 상단 탭 숨김은 Explore 화면에만 적용한다. Paper Feed/Paper Shorts에서는 상단 탭을 계속 표시한다.

Explore에서는 PC/모바일 모두 상단 Papers/Paper Shorts/Explore 탭을 제거한다. 일반 피드 상단 탭과 sidebar 내비게이션은 유지한다. 실제 MP4와 데모 썸네일 모두 동일한 9:16 공통 프레임을 사용하고 caption과 설명 패널 위치를 통일한다. 원본 영상·썸네일 파일은 수정하지 않는다.

### Explore 논문 이해 패널 (2026-10-20)
제목 아래에는 21편의 실제 abstract에 근거해 AI가 작성한 한 문장 TL;DR을 제공한다. Abstract details / Open original PDF → 논문 질문 → 다른 perspective(스타일 배지) → 설명 평가 순서다. 질문은 의견 댓글이 아니라 논문 기반 AI Q&A를 지향한다. 현재 정적 MVP는 질문을 브라우저에 논문별로 저장하고, 출처가 있는 미리 작성한 AI 예시 답변만 제공한다. 실시간 LLM 응답·공개 공유는 미연결임을 표시한다.
