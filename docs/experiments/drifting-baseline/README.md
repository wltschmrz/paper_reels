# Drifting Models — GPT / Claude baseline comparison

2026-10-18 · arXiv:2602.04770v2, **Generative Modeling via Drifting**.

| | GPT‑5.4 mini | Claude Sonnet 5.5 |
|---|---:|---:|
| 영상 길이 | 51.636초 | 67.003초 |
| 측정된 단계 시간 합계 | 100.32초 | 76.66초 |
| 입력 토큰 (전체 호출 합계) | 79,468 | 76,524 |
| 출력 토큰 (추론 포함 API usage) | 9,217 | 3,910 |
| API 비용 추정 | $0.1010775 | $0.192148 |
| 대본 생성/수정/사실 검토 호출 | 3 | 2 |
| 음성 인식 유사도 범위 | 0.947–1.000 | 0.969–1.000 |

시간은 API 호출, TTS, 렌더·합성, 로컬 ASR 검사, 성공한 수집 단계의 **합계**다. 개발·수동 교정·대기 시간 및 최초 PDF 다운로드 실패 시간은 제외했다. GPT의 수집 17.24초는 포함하고 Claude는 이 원문 캐시를 재사용했으므로, 모델 자체 속도의 공정한 벤치마크는 아니다. 세부 시간은 `*-report.json` 참조.

비용은 반환된 실제 input/output 토큰과 확인한 공개 요율로 계산했다. OpenAI $0.75/$4.50, Anthropic $2/$10 (입력/출력 각 100만 토큰). 캐시 할인이 있다면 보수적인 상한 추정이며 공급자 결제 내역·세금과는 다를 수 있다. 로컬 음성·렌더 API 비용은 $0이며 서버 전력/운영 비용은 제외했다. 두 키의 모델 목록 조회는 과금 없이 성공했다. 요청별 보수적인 예약액을 적용해 공급자별 $1 상한을 지켰다. 자동 SDK 재시도는 사용하지 않았다.

- [OpenAI 공식 요율](https://developers.openai.com/api/docs/models/gpt-5.4-mini)
- [Anthropic 공식 요율](https://platform.claude.com/docs/en/about-claude/pricing)
- [원문](https://arxiv.org/abs/2602.04770v2)

## 실행한 구성

PDF 전체 텍스트 → 모델별 근거·한국어 대본·장면 JSON → 원문 인용 문자열 확인 → 같은 모델의 사실 검토 → 로컬 Supertonic 3 음성 → 직접 작성한 고정 애니메이션 + FFmpeg → MP4 검사 + 로컬 SenseVoice ASR → 직접 검토 후 웹 manifest 연결.

두 모델에 같은 baseline prompt를 사용했다. 약 60초, 기하적 직관, 문제/방법/결과/한계, 실제 데이터 청록색·생성 샘플 금색, 학습과 추론을 구분한다. GPT는 medium reasoning, Claude는 기본 inference 설정(추가 extended thinking 요청 없음)을 사용했다. 모델 생성 Python이나 Manim은 **실행하지 않았다**. 컨테이너의 Docker/namespace 격리가 없어 기존 자유 코드 생성 worker는 계속 차단된다. 실행한 렌더러는 허용된 여섯 종류의 도형 애니메이션과 텍스트만 받는 별도 실험이다. 도형은 논문 결과 재현이 아닌 개념도이며 영상에 표시한다. 논문별 공유 FactSheet/캐시, 전체 Manim 시각 검토·수정 루프를 검증한 실행은 아니다.

GPT 첫 초안과 수정 초안의 일부 인용이 원문과 일치하지 않았다. 추가 유료 대본 생성을 하지 않고 네 곳의 인용/페이지를 직접 원문 문장으로 교정했다. 한국어 내레이션은 모델 결과 그대로다. 그 후 모델 사실 검토를 통과했다. Claude는 최초 인용 검증을 통과했다. 두 모델의 자기 검토는 독립적인 학술 정확성 인증이 아니다.

## 보기

- 웹: http://localhost:5173 → Paper Shorts → Generative Modeling via Drifting → `you_openai` / `you_anthropic`.
- GPT: http://localhost:5173/videos/drifting-openai-baseline.mp4
- Claude: http://localhost:5173/videos/drifting-anthropic-baseline.mp4

고정 템플릿을 공유하므로 두 영상의 차이는 주로 대본·구성·길이에서 나타난다. Claude 웹 채팅에서 만든 기존 샘플과 같은 자유로운 애니메이션 품질을 재현했다고 주장하지 않는다. 이 한 논문·한 실행만으로 모델 일반 성능을 판단할 수 없다.

## 재현 / 과금 주의

```bash
PYTHONPATH=backend .venv/bin/python -m experiments.drifting --provider openai
PYTHONPATH=backend .venv/bin/python -m experiments.drifting --provider anthropic
PYTHONPATH=backend .venv/bin/python -m experiments.verify_audio openai
PYTHONPATH=backend .venv/bin/python -m experiments.verify_audio anthropic
```

기존 산출물을 재사용한다. `backend/data/experiments`를 삭제하면 유료 API를 다시 호출할 수 있다. 키는 ignored `backend/.env`에만 두고 프론트엔드·커밋·실행 보고서에 넣지 않는다. 원본 응답/프롬프트/음성 중간 결과는 ignored 작업 폴더에 있으며, 공개 가능한 사용량·대본·근거·검증만 이 문서 옆에 보관한다.
