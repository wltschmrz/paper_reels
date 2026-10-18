"""Fail if the local deterministic regression no longer meets M0 acceptance."""

import json, subprocess, sys
from pathlib import Path

job = Path(sys.argv[1])
probe = json.loads(
    subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,width,height",
            "-of",
            "json",
            str(job / "out/short.mp4"),
        ]
    )
)
video = next(s for s in probe["streams"] if s["codec_type"] == "video")
assert (video["width"], video["height"]) == (1080, 1920)
assert 80 <= float(probe["format"]["duration"]) <= 88
render = json.loads((job / "render/final/render_report.json").read_text())
assert len(render["scenes"]) == 8 and not render["errors"]
assert all(s["overrun_sec"] < 0.3 for s in render["scenes"])
report = json.loads((job / "out/validation.json").read_text())
checks = [
    c
    for c in report["checks"]
    if c["name"] not in {"visual_review_executed", "claims_judged"}
]
assert checks and all(c["passed"] for c in checks)
assert json.loads((job / "job.json").read_text())["status"] == "published"
print("M0 deterministic regression passed; LLM visual QA and judge are NOT validated.")
