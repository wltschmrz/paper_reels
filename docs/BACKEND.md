# 백엔드 설정과 실제 생성 연결

## 현재 실행 상태

- frontend: `http://localhost:5173`
- owner API: 컨테이너 내부 `http://127.0.0.1:8000`; 문서 `/docs`
- frontend `/api`는 Vite 개발 프록시를 통해 API로 연결한다. 별도로 8000을 Windows에 공개할 필요는 없다.
- SQLite 작업 큐 + 별도 Python worker. 서버를 껐다 켜도 job·preset·공개 결과·신고가 보존된다.
- 현재는 **본인 한 명의 개발용 owner workspace**다. 서버에 등록한 본인의 GPT/Claude 키로 결제된다. 타인별 키 저장·계정별 권한·멀티테넌트 BYOK는 아직 구현하지 않았다.
- API 키 2개는 비어 있으며 실제 LLM 호출을 수행하지 않았다. Docker renderer가 없으면 실제 생성 요청은 409로 거절한다. 버튼이 20초 데모로 몰래 대체되지는 않는다.

## 1. API 키를 어디서 발급하나

### OpenAI (GPT)

1. [OpenAI API dashboard의 API keys](https://platform.openai.com/api-keys)에서 프로젝트 키를 생성한다.
2. 해당 API 프로젝트의 결제·사용 한도와 사용할 모델에 대한 접근을 확인한다.
3. `backend/.env`의 `OPENAI_API_KEY=` 뒤에 키를 넣는다.

SDK는 서버 환경변수의 키를 사용한다. [공식 OpenAI quickstart](https://developers.openai.com/api/docs/quickstart).

### Anthropic (Claude)

1. [Claude Console](https://platform.claude.com/) 로그인 → Settings → API keys → Create key.
2. 개인 개발용 키 또는 해당 workspace에 제한된 키를 생성한다. Console의 API 사용 비용과 한도를 확인한다.
3. `backend/.env`의 `ANTHROPIC_API_KEY=` 뒤에 키를 넣는다.
4. 계정 키가 명시적 workspace ID를 요구하면 `ANTHROPIC_WORKSPACE_ID=`도 채운다.

[Claude 공식 키 생성 안내](https://platform.claude.com/docs/en/get-api-key), [Messages API](https://platform.claude.com/docs/en/api/messages/create).

**채팅에 키를 붙이지 않는다. `src/`, `VITE_*`, GitHub 커밋에 넣지 않는다.** 일반 앱 구독 로그인 대신 각 API 콘솔에서 생성한 키를 사용한다.

## 2. 등록 파일

이미 이 작업 환경에는 빈 키와 임의의 로컬 접근 토큰을 가진 `backend/.env`를 만들어 두었다. 이 파일은 gitignore 대상이다. 다른 컴퓨터에서는:

```bash
cp backend/.env.example backend/.env
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

생성한 값을 `SS_API_TOKEN`에 넣고 다음을 편집한다:

```dotenv
OPENAI_API_KEY=발급한_OpenAI_키
ANTHROPIC_API_KEY=발급한_Claude_키
SS_API_TOKEN=임의의_긴_로컬_접근_토큰
SS_OPENAI_MODEL=gpt-6-astra
SS_ANTHROPIC_MODEL=claude-opus-5-5
SS_ANTHROPIC_REVIEW_MODEL=claude-sonnet-5-5
```

모델명은 출발 설정이며 실제 비교 평가로 선정한 최적 조합이 아니다. 계정에서 사용 가능한 ID로 변경한다. 서버에 설정한 모델만 UI에서 선택할 수 있다. API 키/모델을 변경한 후 API, worker, Vite를 재시작한다. `SS_API_TOKEN`은 개발 프록시에서만 사용하고 JS 번들에 넣지 않는다.

Vite 개발 서버는 신뢰하는 로컬 네트워크에서만 사용한다. 이 owner proxy를 공개 서비스의 인증으로 재사용하지 않는다. GitHub Pages에는 이 프록시가 없으므로 정적 샘플 영상·데모는 동작하지만 실제 생성에는 별도 인증된 backend deployment가 필요하다.

## 3. 설치와 실행

기본 API만 실행할 때:

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-api.txt
cd backend
../.venv/bin/python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```

다른 터미널에서:

```bash
cd backend
../.venv/bin/python -m app.worker
```

frontend는 레포 루트에서 `npm run dev`. Windows 포트 5173 전달 방법은 루트 README 참고. Python/ffmpeg 명령은 현재 Linux 컨테이너 안에서 실행한다.

생성 전체를 실행하려면 worker 환경에 FFmpeg, LaTeX, Manim, 로컬 TTS/ASR와 모델이 필요하다:

```bash
apt-get update
apt-get install -y ffmpeg texlive-latex-base texlive-latex-extra texlive-fonts-recommended dvisvgm libpango1.0-dev libcairo2-dev pkg-config fonts-noto-cjk build-essential
.venv/bin/pip install -r backend/requirements.txt
SS_MODELS_DIR="$PWD/backend/models" bash backend/tools/fetch_models.sh
```

이 작업 환경에는 위 도구와 모델을 설치했다. 모델 다운로드 파일은 git에 포함하지 않는다.

## 4. 생성 Python 코드 격리

API 키를 가진 trusted worker와 LLM이 작성한 Manim 실행 환경을 분리했다. 생성 장면은 Docker에서:

- 네트워크 없음, API 키 없음
- read-only root, 모든 Linux capability 제거, no-new-privileges
- CPU 2, RAM 3GB, PID 128, 장면당 timeout 900초
- job 입력 read-only, job의 `render/`만 쓰기 허용, 임시 파일은 제한된 `/tmp`

```bash
# Docker daemon을 사용할 수 있는 환경에서, 레포 루트 기준
# backend/.dockerignore로 .env와 runtime 데이터가 image에 포함되지 않는다.
docker build -f backend/tools/Dockerfile.render -t scholarshorts-render:local backend
```

**현재 컨테이너에는 Docker CLI/daemon이 없어 이미지 빌드와 격리 경로는 미실행이다.** 가장 단순한 개발 배치는 Docker를 사용할 수 있는 WSL/Linux에서 API와 worker를 실행하는 것이다. worker 자체를 컨테이너로 옮길 경우 daemon이 보는 bind mount의 job 경로가 worker의 절대 경로와 같아야 한다. 단순히 Docker socket을 아무 컨테이너에 연결하는 설정은 제공하지 않았다.

기존 `backend/tools/Dockerfile`은 원본 재현용 레퍼런스 이미지다. 새 API 생성의 보안 경계는 별도 `Dockerfile.render`와 `pipeline/sandbox.py`다. AST lint를 sandbox라고 간주하지 않는다.

## 5. 키 등록 직후 우선 실행할 M1

다음은 실제 API 비용이 발생하는 **명시적 수동 명령**이다. 아직 실행하지 않았다.

```bash
cd backend
PYTHONPATH=. ../.venv/bin/python -m tools.smoke_llm --provider anthropic --preset geometric_intuition_ko
PYTHONPATH=. ../.venv/bin/python -m tools.smoke_llm --provider openai --preset equation_first_ko
```

`understand → storyboard`만 실행하고 생성 코드를 실행하지 않는다. `backend/data/smoke/<id>/job.json`의 실제 input/output token을 확인한다. API key가 없는 상태에서는 호출 전에 중단한다. JSON 계약·인용·필수 섹션·길이·숫자 게이트를 최대 3회 내 통과하는지 먼저 검증해야 한다. 나머지 critical_review_en 프리셋도 같은 방식으로 비교한다.

현재 원문 프롬프트에는 PDF 페이지 본문과 필요한 LaTeX sections를 사용한다. 대형 TikZ 좌표 파일과 스타일 매크로는 프롬프트에서 제외한다. 큰 논문은 길이를 조용히 잘라 보내지 않고 chunked extraction 필요 오류를 낸다. 원본 PaperDoc에는 페이지 텍스트와 LaTeX 원문을 보존한다. 개별 equations/tables 배열에 대한 완전한 LaTeX semantic parser는 후속 개선이다.

## 6. 웹에서 실제 생성

논문 → Generate Short → **Real generation · my API keys**:

- P0: 설명 관점, 필수 섹션, 수식 깊이, 대상 수준, 길이.
- P1: understand / storyboard / visual_code / visual_qa / judge 단계별 GPT·Claude 선택.
- 키·모델·로컬 음성 모델·Docker renderer가 준비되지 않으면 생성을 차단한다.
- 제출하면 SQLite queue에 들어간다. 상단 시계 → Server generation jobs에서 progress·실제 사용 토큰·실패·취소·재시도 확인.
- 성공한 렌더도 먼저 `needs_review`로 보관한다. 영상·검증 JSON을 확인한 뒤 Publish.
- 필수 검증 실패, skip 또는 누락 상태의 결과는 Publish API가 거절한다.
- 게시되면 서버의 Short manifest를 frontend 피드에 추가한다.

가격표는 `backend/pricing.example.json` 형식으로 `backend/pricing.json`에 작성한다. 실제 가격을 확인하기 전에는 비용 미확정으로 표시한다. 레퍼런스 UsageRecord의 `est_cost_usd=0`은 가격표 부재 시 무료라는 뜻이 아니다. UI는 이 값을 청구액으로 표시하지 않고 실제 토큰과 pricing 구성 상태를 보여준다.

## 7. 코드 위치

| 역할                                         | 파일                                                           |
| -------------------------------------------- | -------------------------------------------------------------- |
| HTTP API / owner auth                        | `backend/app/api.py`                                           |
| SQLite queue / 영속 상태                     | `backend/app/db.py`                                            |
| worker / child process / 취소·timeout        | `backend/app/worker.py`, `run_job.py`                          |
| 키·모델·경로                                 | `backend/app/settings.py`, `.env`                              |
| 원문 수집 / PDF·LaTeX / quote gate           | `backend/pipeline/stages/ingest.py`                            |
| 단계 순서 / 공유 facts cache / usage / retry | `backend/pipeline/runner.py`                                   |
| GPT Responses / Claude Messages              | `backend/pipeline/providers/llm_openai.py`, `llm_anthropic.py` |
| 격리 렌더                                    | `backend/pipeline/sandbox.py`                                  |
| 고정 contracts/render kit / golden           | ZIP에서 가져온 `backend/pipeline`, `backend/golden`            |
| 웹 API adapter / 실제 생성 설정              | `src/lib/backend.ts`, `src/components/Studio.tsx`              |
| 서버 작업 UI                                 | `src/components/BackendJobs.tsx`                               |

공유 facts 캐시는 pinned paper version + 전체 source hash + understand model/params + extractor revision으로 분리하고 파일 잠금으로 중복 계산을 막는다. 내용이 같은 소스·모델의 다음 job은 캐시를 쓴다. 취소 전 이미 호출된 API 비용은 되돌리지 않는다.

## 8. API 계약

- `GET /api/config`: 키 유무 boolean, 설정된 모델, 미준비 의존성. 키 자체는 반환하지 않음.
- `GET/POST /api/presets`
- `POST /api/papers/{id}/shorts`: 전체 preset snapshot → 202 job
- `GET /api/jobs`, `GET /api/jobs/{id}`
- `POST /api/jobs/{id}/cancel`, `/retry`, `/publish`
- `GET /api/jobs/{id}/validation`, `/preview/short.mp4`
- `GET /api/shorts`, `/api/media/{id}/short.mp4`
- `POST /api/shorts/{id}/flags`: timestamp, kind, comment → line/claim/source 매핑

신고 API는 이 backend가 생성한 timeline이 있는 게시물에 적용한다. 제공 MP4에는 실제 timeline 파일이 없으므로 임의의 타임스탬프 근거를 만들어 붙이지 않았다. 기존 프론트의 댓글·좋아요는 여전히 localStorage이며 서버 신고 UI 연결은 후속 작업이다.

## 9. 확인 범위

`docs/VALIDATION.md`에 이 세션의 실행 결과와 미검증 범위를 기록한다. 원본 reference 문서의 84.1~84.2초와 이번 제공 MP4의 83.6초를 구분한다. API 키가 없어 LLM stage·실측 API 비용·혼합 공급자 전체 생성·모델 품질 비교는 검증하지 않았다. Docker build도 미실행이다. 이 한계를 숨기지 않고 개발 서버에서 상태로 보여준다.

## 원본 영상 품질 재현 방향 (2026-10-18)

두 Drifting baseline은 고정된 여섯 장면을 공유했기 때문에 영상 구성이 비슷하다. 같은 프롬프트가 다른 모델에서 같은 대본/영상을 보장하는 것은 아니다. 동일 모델도 추론 설정과 샘플링에 따라 달라질 수 있다.

`backend/presets/reference_quality_ko.json`은 원본 Flow Map 설정을 기반으로 60초, 문제/방법/결과/한계, 수식 깊이 2, 기하적 설명을 설정한다. 분석·대본·시각화 코드는 Opus, 검토는 Sonnet 구성이다. 비용이 더 들 수 있으므로 이 프리셋으로 이번에는 유료 실행하지 않았다.

실제 storyboard 프롬프트에 원본의 장면별 시각 설계를 참고 자료로 연결했다. 원본의 논문 주장/수치를 복사하지 않고, 장면마다 시작→변화→결론을 설계하도록 한다. 코드 생성에는 늘 같은 S4를 넣던 것에서 해당 visual type에 맞는 golden 장면을 선택하도록 바꿨다. 기존 음성 동기화·Manim·미리보기 검토·수정 루프는 유지한다.

이 개선은 프롬프트/구조 검증까지 완료했으며, 새로운 논문으로 원본 품질을 재현한 영상 검증은 아직 아니다. 생성 코드의 실행에 필요한 Docker가 현재 개발 컨테이너에 없다. Docker가 가능한 독립 worker 환경에서 `docker build -f backend/tools/Dockerfile.render -t scholarshorts-render:local backend`로 렌더 이미지를 준비하고 API의 readiness가 통과한 뒤 실행해야 한다. Docker CLI만 설치하는 것으로는 충분하지 않고 daemon 접근·bind mount 경로도 일치해야 한다. 격리를 우회해 생성 코드를 로컬로 실행하지 않는다.
