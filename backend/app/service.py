import importlib.util, json, os, shutil, subprocess
from pathlib import Path
from pipeline.contracts import Preset
from .settings import ROOT, DATA, MODELS, LLM_STAGES, keys, model_choices

PAPERS = ROOT.parent / "src/data/papers.json"


def job_dir(jid):
    if len(jid) != 32 or any(c not in "0123456789abcdef" for c in jid):
        raise ValueError("Invalid job ID")
    return DATA / "jobs" / jid


def readiness(preset=None):
    reasons = []
    choices = (
        [getattr(preset.models, s).model_dump() for s in LLM_STAGES] if preset else []
    )
    for provider in {c["provider"] for c in choices}:
        if not keys().get(provider):
            reasons.append(f"{provider.upper()} API key not configured")
    if not shutil.which("ffmpeg"):
        reasons.append("ffmpeg not installed")
    if not importlib.util.find_spec("sherpa_onnx"):
        reasons.append("sherpa-onnx not installed")
    for directory in [
        "sherpa-onnx-supertonic-3-tts-int8-2026-05-11",
        "sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17",
    ]:
        if not (MODELS / directory).is_dir():
            reasons.append("Local voice model missing: " + directory)
    if not shutil.which("docker"):
        reasons.append("Docker renderer not available")
    else:
        try:
            r = subprocess.run(
                [
                    "docker",
                    "image",
                    "inspect",
                    os.getenv("SS_RENDER_IMAGE", "scholarshorts-render:local"),
                ],
                capture_output=True,
                timeout=5,
            )
            if r.returncode:
                reasons.append("Render image or Docker daemon unavailable")
        except (OSError, subprocess.TimeoutExpired):
            reasons.append("Docker daemon unavailable")
    return reasons


def validate_preset(preset):
    allowed = {(c["provider"], c["model"]) for c in model_choices()}
    for stage in LLM_STAGES:
        c = getattr(preset.models, stage)
        if (c.provider, c.model) not in allowed:
            raise ValueError(f"{stage}: select a server-configured model")
        if c.params:
            raise ValueError("LLM parameter overrides are not enabled in owner MVP")
    if (
        preset.models.tts.provider != "supertonic_local"
        or preset.models.asr.provider != "sensevoice_local"
    ):
        raise ValueError("Local TTS/ASR required")
    if preset.models.tts.params.keys() - {
        "sid",
        "num_steps",
        "threads",
    } or preset.models.asr.params.keys() - {"threads"}:
        raise ValueError("Unsupported voice parameters")
    for key, value in preset.models.tts.params.items():
        maximum = {"sid": 9, "num_steps": 32, "threads": 4}[key]
        if (
            not isinstance(value, int)
            or not (0 if key == "sid" else 1) <= value <= maximum
        ):
            raise ValueError("Invalid TTS setting")
    if not 1 <= preset.models.asr.params.get("threads", 2) <= 4:
        raise ValueError("Invalid ASR threads")
    preset.creator_id = "owner"
    return preset


def frontend_short(jid, preset):
    path = job_dir(jid)
    sb = json.loads((path / "storyboard.json").read_text())
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path / "out/short.mp4"),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return {
        "id": jid,
        "paperId": sb["paper_id"],
        "creator": "you",
        "title": sb["hook_title"],
        "style": preset["style"]["tone"],
        "duration": round(float(probe.stdout), 1),
        "videoUrl": f"/api/media/{jid}/short.mp4",
        "thumbnailUrl": f"/api/media/{jid}/thumbnail.jpg",
        "preset": preset,
        "validation": "reviewed",
    }
