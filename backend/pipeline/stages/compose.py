import json
import subprocess
import sys
from pathlib import Path

from ..contracts import Preset, Storyboard, TimelineEntry
from .bgm import soft_pad


def probe(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout.strip())


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def run(job: Path):
    sb = Storyboard.model_validate_json((job / "storyboard.json").read_text())
    preset = Preset.model_validate_json((job / "preset.json").read_text())
    out = job / "out"
    out.mkdir(exist_ok=True)
    files = [job / "render" / "final" / f"{s.scene_id}.mp4" for s in sb.scenes]
    ins = sum([["-i", str(f)] for f in files], [])
    fc = "".join(f"[{i}:v][{i}:a]" for i in range(len(files))) + f"concat=n={len(files)}:v=1:a=1[v][a]"
    cat = out / "_concat.mkv"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
                    "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(cat)], check=True)
    dur = probe(cat)
    vis = preset.style.visual
    final = out / "short.mp4"
    if vis.bgm == "soft_pad":
        pad = out / "_bgm.wav"
        soft_pad(pad, dur)
        af = (f"[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[v];[1:a]volume={vis.bgm_db}dB[m];"
              f"[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(cat), "-i", str(pad), "-filter_complex", af, "-map", "0:v", "-map", "[a]",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", str(final)], check=True)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(cat), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", str(final)], check=True)
    entries, offset = [], 0.0
    for s, f in zip(sb.scenes, files):
        rep = json.loads((job / "render" / f"report_{s.scene_id}.json").read_text())
        for e in rep["timeline"]:
            entries.append(TimelineEntry(scene_id=s.scene_id, line_id=e["line_id"], start=round(offset + e["start"], 3),
                                         end=round(offset + e["end"], 3), subtitle=e["subtitle"], claims=e["claims"]))
        offset += probe(f)
    (out / "claims_timeline.json").write_text(json.dumps([e.model_dump() for e in entries], ensure_ascii=False, indent=1))
    srt = [f"{i}\n{srt_time(e.start)} --> {srt_time(e.end)}\n{e.subtitle}\n" for i, e in enumerate(entries, 1)]
    (out / "captions.srt").write_text("\n".join(srt))
    hook = [e for e in entries if e.scene_id == sb.scenes[0].scene_id][-1]
    t = hook.end - 0.2
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(final), "-frames:v", "1", "-q:v", "2",
                    str(out / "thumbnail.jpg")], check=True)
    cat.unlink()
    for p in out.glob("_bgm.wav"):
        p.unlink()
    return {"video": "out/short.mp4", "thumbnail": "out/thumbnail.jpg", "captions": "out/captions.srt",
            "claims_timeline": "out/claims_timeline.json", "duration_sec": round(probe(final), 2)}


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1])), indent=1))
