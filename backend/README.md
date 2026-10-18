# ScholarShorts backend

사용자 제공 `reference/scholarshorts-pipeline.zip`을 기반으로 한 개인용 생성 backend.

**실행·키 등록·Docker 격리·검증 안내: [../docs/BACKEND.md](../docs/BACKEND.md)**

- `app/`: FastAPI, SQLite queue, owner access, worker, publication, timestamp flags.
- `pipeline/`: 고정 stage contracts, provider adapters, source ingest, shared fact cache, render kit, sandbox.
- `golden/`: 제공된 원본 회귀 fixture. 장면 코드를 변경하지 않았다.
- `tools/smoke_llm.py`: API 키 등록 후 수동으로 실행하는 유료 M1 검사.
- `tools/run_golden.sh`: 원본 fixture의 키 없는 회귀 렌더. 기존 job 폴더는 덮어쓰지 않는다.
- `tools/Dockerfile.render`: 생성 Python 장면용 네트워크 없는 renderer 이미지.

원본 인계 문서는 `REFERENCE_README.md`, 원본 설계는 `docs/PIPELINE.md`. API 키 없는 golden 실행의 `published` 상태는 회귀 fixture 내부 상태일 뿐 과학적 사실 검증이나 웹 게시를 뜻하지 않는다. 서비스에서는 검증 skip를 공개 조건으로 인정하지 않는다.
