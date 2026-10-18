import json, secrets, time, uuid
from pathlib import Path
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pipeline.contracts import Preset, ValidationReport
from . import db, service
from .settings import ROOT, DATA, API_TOKEN, LLM_STAGES, keys, model_choices

app = FastAPI(title="ScholarShorts owner API", version="0.2.0")


def owner(x_ss_token: str = Header(default="")):
    if not API_TOKEN or not secrets.compare_digest(x_ss_token, API_TOKEN):
        raise HTTPException(401, "Owner access required")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mode": "single-owner",
        "generation": "key-and-renderer-required",
    }


@app.get("/api/config", dependencies=[Depends(owner)])
def config():
    return {
        "providers": {p: bool(k) for p, k in keys().items()},
        "models": model_choices(),
        "stages": LLM_STAGES,
        "blockers": service.readiness(),
        "pricing": "unconfigured"
        if not (ROOT / "pricing.json").exists()
        else "configured",
        "publication": "manual review required",
    }


@app.get("/api/presets", dependencies=[Depends(owner)])
def presets():
    base = [json.loads(p.read_text()) for p in (ROOT / "presets").glob("*.json")]
    configured = model_choices()
    for p in base:
        for stage in LLM_STAGES:
            provider = p["models"][stage]["provider"]
            pick = next(c for c in configured if c["provider"] == provider)
            p["models"][stage] = {**pick, "params": {}}
    return base + db.documents("presets")


@app.post("/api/presets", dependencies=[Depends(owner)])
def save_preset(preset: Preset):
    try:
        preset = service.validate_preset(preset)
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not preset.preset_id or len(preset.preset_id) > 100:
        raise HTTPException(422, "Invalid preset ID")
    db.store("presets", preset.preset_id, preset.model_dump())
    return preset


class GenerationRequest(BaseModel):
    preset: Preset


@app.post(
    "/api/papers/{paper_id}/shorts", status_code=202, dependencies=[Depends(owner)]
)
def generate(paper_id: str, body: GenerationRequest):
    if paper_id not in {p["id"] for p in json.loads(service.PAPERS.read_text())}:
        raise HTTPException(404, "Paper not in library")
    try:
        preset = service.validate_preset(body.preset)
    except ValueError as e:
        raise HTTPException(422, str(e))
    blockers = service.readiness(preset)
    if blockers:
        raise HTTPException(409, {"blockers": blockers})
    return db.create(paper_id, preset.model_dump())


@app.get("/api/jobs", dependencies=[Depends(owner)])
def jobs():
    return db.all_jobs()


@app.get("/api/jobs/{jid}", dependencies=[Depends(owner)])
def job(jid: str):
    row = db.get(jid)
    if not row:
        raise HTTPException(404, "Job not found")
    return row


@app.post("/api/jobs/{jid}/cancel", dependencies=[Depends(owner)])
def cancel(jid: str):
    row = job(jid)
    if row["status"] not in ("queued", "running"):
        raise HTTPException(409, "Job is not active")
    db.update(
        jid,
        cancel_requested=1,
        status="cancelled" if row["status"] == "queued" else "running",
    )
    return job(jid)


@app.post("/api/jobs/{jid}/retry", dependencies=[Depends(owner)])
def retry(jid: str):
    row = job(jid)
    if row["status"] not in ("failed", "cancelled"):
        raise HTTPException(409, "Only failed/cancelled jobs can resume")
    blockers = service.readiness(Preset.model_validate(row["preset"]))
    if blockers:
        raise HTTPException(409, {"blockers": blockers})
    cancel_file = service.job_dir(jid) / "cancel.requested"
    cancel_file.unlink(missing_ok=True)
    db.update(jid, status="queued", cancel_requested=0, error=None)
    return job(jid)


@app.get("/api/jobs/{jid}/validation", dependencies=[Depends(owner)])
def validation(jid: str):
    job(jid)
    p = service.job_dir(jid) / "out/validation.json"
    if not p.exists():
        raise HTTPException(404, "No validation report yet")
    return json.loads(p.read_text())


@app.post("/api/jobs/{jid}/publish", dependencies=[Depends(owner)])
def publish(jid: str):
    row = job(jid)
    if row["status"] != "needs_review":
        raise HTTPException(409, "Job is not ready for review")
    report = validation(jid)
    required = {"claims_judged", "layout_qa", "no_overrun", "narration_intelligible"}
    checks = report.get("checks", [])
    if not required <= {c["name"] for c in checks} or any(
        not c["passed"] or "skipped" in c.get("detail", "") for c in checks
    ):
        raise HTTPException(409, "Validation incomplete or failed; cannot publish")
    short = service.frontend_short(jid, row["preset"])
    db.store("shorts", jid, short)
    db.update(jid, status="published", stage="publish", progress=1)
    return short


@app.get("/api/shorts")
def shorts():
    return db.documents("shorts")


@app.get("/api/media/{jid}/{filename}")
def media(jid: str, filename: str):
    if filename not in {"short.mp4", "thumbnail.jpg", "captions.srt"}:
        raise HTTPException(404)
    if not any(s["id"] == jid for s in db.documents("shorts")):
        raise HTTPException(404)
    p = service.job_dir(jid) / "out" / filename
    if not p.exists():
        raise HTTPException(404)
    return FileResponse(p)


@app.get("/api/jobs/{jid}/preview/{filename}", dependencies=[Depends(owner)])
def preview(jid: str, filename: str):
    job(jid)
    if filename not in {"short.mp4", "thumbnail.jpg", "captions.srt"}:
        raise HTTPException(404)
    p = service.job_dir(jid) / "out" / filename
    if not p.exists():
        raise HTTPException(404)
    return FileResponse(p)


class FlagRequest(BaseModel):
    timestamp: float = Field(ge=0, le=3600)
    kind: str = Field(max_length=80)
    comment: str = Field(min_length=1, max_length=2000)


@app.post("/api/shorts/{sid}/flags", dependencies=[Depends(owner)])
def flag(sid: str, body: FlagRequest):
    if not any(s["id"] == sid for s in db.documents("shorts")):
        raise HTTPException(404)
    folder = service.job_dir(sid)
    timeline = json.loads((folder / "out/claims_timeline.json").read_text())
    lines = [e for e in timeline if e["start"] <= body.timestamp < e["end"]]
    facts = json.loads((folder / "facts.json").read_text())["facts"]
    ids = {c for e in lines for c in e["claims"]}
    entry = {
        "id": uuid.uuid4().hex,
        "short_id": sid,
        **body.model_dump(),
        "lines": lines,
        "facts": [f for f in facts if f["id"] in ids],
        "created_at": time.time(),
    }
    db.store("flags", entry["id"], entry)
    return entry
