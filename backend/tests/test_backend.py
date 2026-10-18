import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from app import api as api_module, db, service
from pipeline.contracts import (
    Preset,
    PaperDoc,
    Section,
    FactSheet,
    Fact,
    SourceRef,
    Storyboard,
)
from pipeline.stages.ingest import quote_errors

GOLDEN = Path(__file__).parents[1] / "golden/flowmap_2610.20674"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATA", tmp_path)
    monkeypatch.setattr(service, "DATA", tmp_path)
    monkeypatch.setattr(api_module, "API_TOKEN", "unit-test-token")
    return TestClient(api_module.app, headers={"x-ss-token": "unit-test-token"})


@pytest.fixture
def preset():
    return Preset.model_validate_json((GOLDEN / "preset.json").read_text())


def test_owner_required_and_secrets_not_returned(client):
    assert client.get("/api/jobs", headers={"x-ss-token": ""}).status_code == 401
    response = client.get("/api/config")
    assert response.status_code == 200
    assert "unit-test-token" not in response.text
    assert all(isinstance(v, bool) for v in response.json()["providers"].values())


def test_missing_resources_block_generation(client, preset, monkeypatch):
    monkeypatch.setattr(
        service, "readiness", lambda p=None: ["OPENAI API key not configured"]
    )
    response = client.post(
        "/api/papers/2610.20674/shorts", json={"preset": preset.model_dump()}
    )
    assert response.status_code == 409
    assert db.all_jobs() == []


def test_queue_claim_cancel_resume(client, preset, monkeypatch):
    monkeypatch.setattr(service, "readiness", lambda p=None: [])
    response = client.post(
        "/api/papers/2610.20674/shorts", json={"preset": preset.model_dump()}
    )
    assert response.status_code == 202
    jid = response.json()["id"]
    with ThreadPoolExecutor(2) as pool:
        claims = list(pool.map(lambda _: db.claim(), range(2)))
    assert sum(c is not None for c in claims) == 1
    assert client.post(f"/api/jobs/{jid}/cancel", json={}).status_code == 200
    assert db.get(jid)["cancel_requested"] == 1
    db.update(jid, status="cancelled")
    assert client.post(f"/api/jobs/{jid}/retry", json={}).status_code == 200
    assert db.get(jid)["status"] == "queued"


def test_publish_rejects_skipped_validation(client, preset):
    row = db.create("2610.20674", preset.model_dump())
    jid = row["id"]
    db.update(jid, status="needs_review")
    folder = service.job_dir(jid) / "out"
    folder.mkdir(parents=True)
    (folder / "validation.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "name": name,
                        "passed": True,
                        "detail": "skipped: no key" if name == "claims_judged" else "",
                    }
                    for name in [
                        "claims_judged",
                        "layout_qa",
                        "no_overrun",
                        "narration_intelligible",
                    ]
                ]
            }
        )
    )
    assert client.post(f"/api/jobs/{jid}/publish", json={}).status_code == 409
    assert client.get(f"/api/media/{jid}/short.mp4").status_code == 404


def test_timestamp_flag_maps_original_evidence(client, preset):
    jid = db.create("2610.20674", preset.model_dump())["id"]
    folder = service.job_dir(jid)
    (folder / "out").mkdir(parents=True)
    db.store("shorts", jid, {"id": jid})
    (folder / "out/claims_timeline.json").write_text(
        json.dumps([{"line_id": "s1a", "start": 2, "end": 4, "claims": ["F1"]}])
    )
    (folder / "facts.json").write_text(
        json.dumps({"facts": [{"id": "F1", "source": {"label": "Theorem 4"}}]})
    )
    res = client.post(
        f"/api/shorts/{jid}/flags",
        json={"timestamp": 3, "kind": "incorrect", "comment": "Check this claim"},
    )
    assert res.status_code == 200
    assert res.json()["facts"][0]["source"]["label"] == "Theorem 4"
    assert (
        client.post(
            f"/api/shorts/{jid}/flags",
            json={"timestamp": 4, "kind": "incorrect", "comment": "Gap"},
        ).json()["lines"]
        == []
    )


def test_quote_gate():
    paper = PaperDoc(
        paper_id="test",
        title="test",
        authors=[],
        abstract="Original source",
        sections=[Section(id="p1", title="Page 1", text="A bounded update converges.")],
        source_kind="pdf",
    )
    fs = FactSheet(
        paper_id="test",
        facts=[
            Fact(
                id="F1",
                kind="theorem",
                statement="bounded",
                source=SourceRef(
                    kind="page", label="Page 1", quote="A bounded update converges."
                ),
            )
        ],
    )
    assert quote_errors(fs, paper) == []
    fs.facts[0].source.quote = "Invented evidence"
    assert quote_errors(fs, paper)


def test_golden_and_unsafe_line_ids(preset):
    from pipeline.validators import validate_storyboard

    fs = FactSheet.model_validate_json((GOLDEN / "facts.json").read_text())
    sb = Storyboard.model_validate_json((GOLDEN / "storyboard.json").read_text())
    assert all(c.passed for c in validate_storyboard(sb, preset.style, fs))
    data = sb.model_dump()
    data["scenes"][0]["lines"][0]["line_id"] = "../../secret"
    with pytest.raises(ValueError):
        Storyboard.model_validate(data)


def test_unapproved_model_or_parameters_rejected(preset):
    preset.models.understand.model = "unconfigured"
    with pytest.raises(ValueError):
        service.validate_preset(preset)


def test_openai_adapter_uses_responses_and_records_tokens(monkeypatch):
    from types import SimpleNamespace
    from pipeline.providers import llm_openai

    captured = {}

    class Fake:
        def __init__(self, **kw):
            self.responses = self

        def create(self, **kw):
            captured.update(kw)
            return SimpleNamespace(
                status="completed",
                output_text="{}",
                usage=SimpleNamespace(input_tokens=10, output_tokens=2),
            )

    monkeypatch.setattr(llm_openai, "OpenAI", Fake)
    text, usage = llm_openai.OpenAILLM("model", "fake").complete(
        "system", "user", [b"png"]
    )
    assert (
        captured["store"] is False
        and captured["input"][0]["content"][1]["type"] == "input_image"
    )
    assert usage == {"input_tokens": 10, "output_tokens": 2}


def test_resume_does_not_publish_failed_validation(tmp_path, preset, monkeypatch):
    from pipeline import runner

    (tmp_path / "preset.json").write_text(preset.model_dump_json())
    (tmp_path / "out").mkdir()
    (tmp_path / "out/validation.json").write_text(
        json.dumps({"checks": [{"name": "bad", "passed": False}]})
    )
    monkeypatch.setattr(runner, "done", lambda ctx, name: True)
    state = runner.run(tmp_path, on_progress=lambda _: None)
    assert state.status == "needs_review"
