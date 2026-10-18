import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ..contracts import SceneRender, Storyboard
from ..sandbox import command
from ..render_kit.theme import CANVAS

KIT_ROOT = Path(__file__).resolve().parents[1]


def render_scene(job: Path, sid: str, quality: str, timeout: int = 900):
    w, h, fps = CANVAS[quality]
    media = job / "render" / "_media" / quality / sid
    env = dict(os.environ, SS_JOB_DIR=str(job), PYTHONPATH=f"{KIT_ROOT}:{job / 'scenes'}:{os.environ.get('PYTHONPATH', '')}")
    cmd = ["manim", "-r", f"{w},{h}", "--fps", str(fps), "--disable_caching", "--media_dir", str(media), "-o", f"{sid}.mp4",
           str(job / "scenes" / f"{sid}.py"), sid]
    p = command(job, sid, cmd, timeout)
    if p.returncode != 0:
        return sid, None, p.stderr[-3000:]
    found = list(media.glob(f"videos/{sid}/*/{sid}.mp4"))
    dst = job / "render" / quality / f"{sid}.mp4"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(found[0], dst)
    return sid, dst, ""


def contact_sheet(job: Path, sid: str, video: Path, timeline: list[dict]):
    times = [max(0.0, e["end"] - 0.15) for e in timeline] or [0.5]
    frames = []
    for i, t in enumerate(times):
        f = job / "render" / "preview" / f"_f_{sid}_{i}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", str(f)], check=True)
        frames.append(f)
    out = job / "render" / "preview" / f"sheet_{sid}.png"
    ins = sum([["-i", str(f)] for f in frames], [])
    fc = "".join(f"[{i}]" for i in range(len(frames))) + f"hstack=inputs={len(frames)}" if len(frames) > 1 else "null"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, str(out)], check=True)
    for f in frames:
        f.unlink()
    return out


def run(job: Path, quality: str = "final", workers: int = 2, only: list[str] | None = None):
    sb = Storyboard.model_validate_json((job / "storyboard.json").read_text())
    sids = [s.scene_id for s in sb.scenes if not only or s.scene_id in only]
    with ThreadPoolExecutor(workers) as ex:
        results = list(ex.map(lambda s: render_scene(job, s, quality), sids))
    reports, errors = [], {}
    for sid, path, err in results:
        if path is None:
            errors[sid] = err
            continue
        rep = json.loads((job / "render" / f"report_{sid}.json").read_text())
        sr = SceneRender(scene_id=sid, path=str(path.relative_to(job)), duration_sec=rep["duration_sec"], overrun_sec=rep["overrun_sec"])
        if quality == "preview":
            contact_sheet(job, sid, path, rep["timeline"])
        reports.append(sr)
    (job / "render" / quality / "render_report.json").write_text(json.dumps(
        {"scenes": [r.model_dump() for r in reports], "errors": errors}, ensure_ascii=False, indent=1))
    return reports, errors


if __name__ == "__main__":
    reps, errs = run(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "final")
    for r in reps:
        print(r.scene_id, r.duration_sec, "overrun", r.overrun_sec)
    for k, v in errs.items():
        print("ERROR", k, v)
