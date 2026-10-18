"""Generated Python only runs in a networkless, keyless, bounded container."""

import hashlib, os, subprocess, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def command(job, sid, manim_args, timeout):
    if os.getenv("SS_RENDER_MODE") == "desktop_bridge":
        from .desktop_bridge import command as bridge_command
        return bridge_command(job, sid, manim_args, timeout)
    if os.getenv("SS_RENDER_MODE") == "trusted_golden":
        expected = ROOT / "golden/flowmap_2610.20674/scenes"
        for p in (job / "scenes").glob("*.py"):
            src = expected / p.name
            if not src.exists() or p.read_bytes() != src.read_bytes():
                raise PermissionError(
                    "Local render accepts only unchanged golden scene files"
                )
        env = {
            "PATH": os.environ["PATH"],
            "HOME": str(job),
            "SS_JOB_DIR": str(job),
            "PYTHONPATH": f"{ROOT / 'pipeline'}:{job / 'scenes'}",
            "LANG": "C.UTF-8",
        }
        return subprocess.run(
            manim_args, env=env, capture_output=True, text=True, timeout=timeout
        )
    render = job / "render"
    render.mkdir(exist_ok=True)
    name = f"ss-render-{job.name}-{sid}-{uuid.uuid4().hex[:6]}"
    args = [
        "docker",
        "run",
        "--rm",
        "--name",
        name,
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--cpus",
        "2",
        "--memory",
        "3g",
        "--pids-limit",
        "128",
        "--user",
        f"{os.getuid()}:{os.getgid()}",
        "--tmpfs",
        "/tmp:rw,size=512m",
        "-v",
        f"{job}:{job}:ro",
        "-v",
        f"{render}:{render}:rw",
        "-e",
        f"SS_JOB_DIR={job}",
        "-e",
        f"PYTHONPATH=/app/pipeline:{job}/scenes",
        "-e",
        "HOME=/tmp",
        os.getenv("SS_RENDER_IMAGE", "scholarshorts-render:local"),
        *manim_args,
    ]
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)
