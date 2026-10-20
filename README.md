# ScholarShorts

[https://wltschmrz.github.io/paper_reels/](https://wltschmrz.github.io/paper_reels/)

**One paper, multiple perspectives.** 실제 논문 21편으로 체험하는 논문 탐색 + 개인화된 Shorts 제작 프로토타입.

제품 의도와 브레인스토밍 정리: [PROJECT_BRIEF.md](PROJECT_BRIEF.md). 구조 및 후속 backend 계획: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 로컬 실행

Node.js 22 기준.

```bash
npm ci
npm run dev
```

개발 서버: **http://localhost:5173/**. `0.0.0.0`에 bind하고 파일 polling을 활성화해 Windows/Docker에서도 수정 사항을 자동 반영한다. 서버 프로세스가 종료되면 같은 명령으로 다시 실행한다.

### 현재처럼 Windows의 기존 Docker 컨테이너에서 개발할 때

컨테이너 안의 localhost는 Windows localhost와 별개다. 아래 중 현재 환경에 맞는 방법 한 가지만 적용한다.

- **VS Code Dev Containers**: Ports 탭 → Forward a Port → `5173` → 표시된 Local Address 열기. `.devcontainer/devcontainer.json`에 `"forwardPorts": [5173]`를 추가하면 반복 접속이 편하다. 기존 설정이 없으므로 이 레포는 설정을 덮어쓰지 않는다.
- **이미 `-p 5173:5173`으로 실행한 컨테이너**: Windows 브라우저에서 http://localhost:5173/ 열기.
- **포트가 공개되지 않은 컨테이너**: 실행 중인 컨테이너에 `-p`를 나중에 추가할 수 없으므로 Dev Containers forwarding을 이용하거나, 기존 작업을 보존하고 컨테이너 실행 설정을 수정해 재생성한다. 기존 컨테이너를 무작정 삭제하지 않는다.
- **이 레포용 새 개발 컨테이너**: Windows의 레포 폴더 PowerShell에서 `docker compose up --build` 실행. 제공된 compose가 5173 포트를 publish한다. 이후 http://localhost:5173/ 접속. 기존 개발 컨테이너 안에서 nested Docker로 실행할 필요는 없다.

Windows PowerShell 확인:

```powershell
docker ps --format "table {{.Names}}\t{{.Ports}}"
Test-NetConnection localhost -Port 5173
```

`5173/tcp`만 있고 `0.0.0.0:5173->5173/tcp`가 없으면 포트 publish가 없는 상태다(VS Code forwarding은 별도). 포트 충돌 시 기존 프로세스를 확인하거나 compose의 왼쪽을 `5174:5173`으로 변경하고 localhost:5174로 접속한다. 컨테이너의 `172.17.x.x` 주소는 Windows에서 직접 접근 가능한 주소라고 가정하지 않는다.

## 구현한 흐름

- Paper Feed ↔ Paper Shorts의 공통 검색/주제/정렬.
- 실제 arXiv 제목·저자·초록·공개일·원문/PDF, 로컬 첫 페이지 이미지 21개.
- 논문 상세, 좋아요/싫어요, 북마크, 컬렉션, 관심 분야 기반 For you 정렬.
- Generation Studio: 대상·스타일·언어·길이·속도·시각 밀도·초점·모델 구성 예시·자연어 지시, preset 저장.
- 20초 **데모** job → 영상 없는 preview 생성, 작업 상태/취소, 재접속 상태 보존.
- Explore: 실제 MP4 연결 가능, 키보드/버튼/휠/스와이프 이동, 동일 논문의 다른 설명, 로컬 follow/평가/댓글.

실제 생성 백엔드 구조와 웹 연결은 추가했다. API 키와 Docker renderer 등록 전에는 실제 생성이 차단된다. 결제 서비스와 다중 사용자 인증은 없다. 비용은 예시 demo credits다. 로컬 상태는 현재 브라우저에만 저장되며 다른 기기와 공유하지 않는다.

## 영상 연결

현재 `src/data/shorts.json`에는 가상 사용자 8명의 데모 Shorts 12개와 직접 만든 SVG 썸네일이 등록되어 있다. 이와 별도로 원 논문 arXiv:2610.20674에 연결한 실제 Flow Map 영상 1개(83.6초)가 있다. 클릭하면 재생·평가·댓글을 체험할 수 있다. 샘플 MP4를 `public/videos/`에 넣고 manifest에 상대 경로나 외부 HTTPS URL을 등록한다. 자세한 예: [docs/VIDEOS.md](docs/VIDEOS.md).

## 논문 데이터 갱신

프론트엔드 실행에는 Python이 필요 없다. 이미 수집한 metadata와 PNG가 저장되어 있다.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-data.txt
npm run papers:sync
```

`venv`가 없는 Debian 컨테이너에서는 `uv venv .venv`와 `uv pip install --python .venv/bin/python -r requirements-data.txt`를 사용할 수 있다. 수집은 arXiv 원문 HTML 및 PDF만 사용하고 요청 사이 3초 대기, 다운로드 캐시와 실패 로그를 남긴다. 수집 목록은 `scripts/collect_papers.py`, 출처·수집 시점은 각 데이터 항목, 결과는 `docs/collection-report.json`에서 확인한다. 재수집하려면 해당 `.cache/papers/<id>.html` 또는 `.pdf` 캐시만 제거한다. 원본 abstract/PDF의 저작권은 각 저자와 권리자에게 있으며 프리뷰는 출처 링크와 함께 제공한다.

## 검증

```bash
npm test                 # metadata / asset / manifest 계약
npm run build            # TypeScript + production build
npm run test:e2e         # dev server 실행 중: 브라우저 핵심 흐름
```

브라우저 테스트 최초 1회 `npx playwright install chromium` 필요. 테스트는 앱 상태를 격리된 browser context에서 검증하며 screenshots는 `test-results/`에 저장한다.

## GitHub Pages

`.github/workflows/pages.yml`이 main push 시 build → GitHub Pages 배포를 수행한다. GitHub repo Settings → Pages → Source를 **GitHub Actions**로 설정한다. 배포 주소는 `https://wltschmrz.github.io/paper_reels/`이다. Actions의 Deploy 작업이 성공하면 접속할 수 있다. 첫 배포 전에는 저장소 Settings → Pages에서 GitHub Actions를 게시 소스로 선택해야 한다.

Vite `base: './'` 및 asset resolver로 프로젝트 하위 경로를 지원한다. 화면 전환은 client state이므로 별도 서버 라우팅이 필요 없다. GitHub Pages에는 Python/Manim/FFmpeg worker가 올라가지 않는다. 실제 backend는 [아키텍처 문서](docs/ARCHITECTURE.md)의 별도 서비스로 확장한다.

## GPT / Claude 백엔드 설정

키 발급 위치, `backend/.env` 등록, API·worker 실행, Docker renderer, M1 검증 명령은 **[docs/BACKEND.md](docs/BACKEND.md)**에 정리했다. 실제 제공 영상은 `public/videos/flowmap_reel.mp4`, 원본 자료는 `reference/`에 보존했다. **[docs/VALIDATION.md](docs/VALIDATION.md)**에서 실제 확인한 구간과 아직 실행하지 못한 구간을 구분한다.

## Email Digest Preview

Footer의 **Email Digest Preview** 링크에서 독립 이메일 시연 화면을 연다.

- 로컬: `http://localhost:5173/#/digest-preview`
- GitHub Pages 배포 후: `https://wltschmrz.github.io/paper_reels/#/digest-preview`
- 직접 접근·새로고침을 지원하는 hash 경로이며 서버 rewrite가 필요 없다.
- 논문 메타데이터는 기존 catalogue를 재사용한다. 점수·추천 규모·발신자·날짜는 시연 데이터다.
- Play the Digest / Watch Shorts는 연결된 실제 영상만 재생한다. 영상이 없으면 안내 modal을 표시한다.
- 실제 이메일 발송, 구독·해지, 자동 추천은 구현하지 않는다. 관심사는 기존 브라우저 설정으로만 저장된다.
- 방향 전환 전 MVP는 `legacy-mvp-before-digest-2026-10-20` tag (`7708aaf`)와 `.cache/backups/legacy-mvp-before-digest-2026-10-20.bundle`에 보존했다. bundle은 로컬 백업이며 git에 올리지 않는다.
