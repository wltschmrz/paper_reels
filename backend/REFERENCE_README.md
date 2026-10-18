# scholarshorts-pipeline

ScholarShorts의 "논문 → 쇼츠" 생성 파이프라인 레퍼런스 구현. 설계와 구현 계획은 `docs/PIPELINE.md`.

## 빠른 실행 (golden 예제 재현)

```bash
docker build -f tools/Dockerfile -t scholarshorts-pipeline .
docker run --rm -v $PWD/jobs:/jobs scholarshorts-pipeline
```

로컬에서 직접:

```bash
sudo apt-get install -y ffmpeg texlive-latex-base texlive-latex-extra dvisvgm libpango1.0-dev libcairo2-dev pkg-config fonts-noto-cjk
pip install -U pip setuptools wheel && pip install -r requirements.txt
bash tools/fetch_models.sh
bash tools/run_golden.sh /tmp/ss_jobs/golden
```

결과: `/tmp/ss_jobs/golden/out/{short.mp4, captions.srt, claims_timeline.json, thumbnail.jpg, validation.json}`

## 코딩 에이전트에게 넘길 지시문

```
이 저장소의 docs/PIPELINE.md를 먼저 끝까지 읽어라.
고정 영역(pipeline/contracts.py의 schema, pipeline/render_kit, stage 순서, 검증 게이트)은 바꾸지 말고, 바꿔야 할 이유가 생기면 PR 설명에 근거를 적어라.
11절의 M0부터 순서대로 진행하고, 각 마일스톤의 완료 기준을 만족하는 실행 로그를 PR에 붙여라.
M1(LLM stage 실행 검증)에서 실제 토큰 사용량을 job.json으로 기록하고 7절의 추정치를 실측값으로 고쳐라.
golden/flowmap_2610.20674는 회귀 테스트 기준이다. 어떤 변경 후에도 tools/run_golden.sh가 published로 끝나야 한다.
```
