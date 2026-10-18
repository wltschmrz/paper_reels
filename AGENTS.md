# ScholarShorts repository guidance

- Read `PROJECT_BRIEF.md` before product changes; it preserves the user's concept, scope, research questions, and schedule.
- Read `docs/ARCHITECTURE.md` for component ownership and the future API/worker boundary.
- Keep Paper Feed and Paper Shorts on the same paper data, search, topic, and sorting state.
- Preserve `Paper 1:N Short`. Several creators/presets may explain one paper.
- Real paper abstracts and PDF previews must have source provenance. Do not invent paper metadata.
- The supplied Flow Map video and two validated v2 API outputs (GPT edited / Claude reviewed) are linked to arXiv:2610.20674; two explicitly labeled Drifting fixed-template baselines are linked to arXiv:2602.04770. Other demo videos remain empty. Demo jobs produce explicitly labeled previews with no video URL; do not claim successful real generation or charge real fees.
- Register supplied media through `src/data/shorts.json`; follow `docs/VIDEOS.md` for GitHub Pages-compatible paths.
- Browser state is local-only until a backend is deliberately integrated. Keep API credentials out of client code.
- Run `npm test` and `npm run build` after substantive changes; use `npm run test:e2e` with the dev server running for interaction changes.
- The user reviews changes from Windows through Docker port 5173. Keep the dev server bound to 0.0.0.0 and preserve file polling.
- Update the brief or architecture docs when product decisions change.

- Read `docs/BACKEND.md` for owner API/worker setup and `reference/PIPELINE (2).md` for current v2 pipeline contracts. Never execute generated scenes locally; only the unchanged golden fixture is eligible for trusted local regression. The Windows Desktop bridge runs generated scenes in separate networkless Docker containers; never replace it with local execution.
- Run `PYTHONPATH=backend .venv/bin/python -m pytest backend/tests` for backend changes. API keys belong only in ignored `backend/.env`.
