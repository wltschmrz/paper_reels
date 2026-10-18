import difflib
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from ..contracts import LineAudio, NarrationTrack, Preset, Storyboard, UsageRecord
from ..providers.base import get_asr, get_tts

MAX_ATTEMPTS = 4
ACCEPT = 0.93
ACCEPT_NUMERIC = 0.8


DIG = "영일이삼사오육칠팔구"


def ko_int(n: str) -> str:
    if len(n) > 1 and n.startswith("0"):
        return "".join(DIG[int(c)] for c in n)
    v = int(n)
    if v == 0:
        return "영"
    out = ""
    for big, name in ((10 ** 4, "만"), (1, "")):
        chunk = v // big % 10 ** 4
        if not chunk:
            continue
        part = ""
        for unit, un in ((1000, "천"), (100, "백"), (10, "십"), (1, "")):
            d = chunk // unit % 10
            if d:
                part += ("" if d == 1 and un else DIG[d]) + un
        out += part + name
    return out


def ko_number(m) -> str:
    i, _, f = m.group(0).partition(".")
    return ko_int(i) + ("점" + "".join(DIG[int(c)] for c in f) if f else "")


def norm(s, lang):
    if lang == "ko":
        return re.sub(r"[^가-힣]", "", re.sub(r"\d+(?:\.\d+)?", ko_number, s))
    return re.sub(r"[^a-z]", "", s.lower())


def trim(x, sr, th=0.01):
    idx = np.where(np.abs(x) > th)[0]
    if len(idx) == 0:
        return x
    return x[max(0, idx[0] - int(0.03 * sr)):min(len(x), idx[-1] + int(0.1 * sr))]


def run(job: Path):
    sb = Storyboard.model_validate_json((job / "storyboard.json").read_text())
    preset = Preset.model_validate_json((job / "preset.json").read_text())
    tts, asr = get_tts(preset.models.tts), get_asr(preset.models.asr)
    pace, lang = preset.style.voice.pace, sb.language
    (job / "audio").mkdir(exist_ok=True)
    lines, chars, t0 = {}, 0, time.time()
    for ln in sb.all_lines():
        best = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            x, sr = tts.synth(ln.tts_text, lang)
            x = trim(x, sr)
            hyp = asr.transcribe(x, sr, lang)
            sim = difflib.SequenceMatcher(None, norm(hyp, lang), norm(ln.tts_text, lang)).ratio()
            if best is None or sim > best[0]:
                best = (sim, hyp, x, sr, attempt)
            if sim >= (ACCEPT_NUMERIC if re.search(r"\d", ln.subtitle) else ACCEPT):
                break
        sim, hyp, x, sr, attempt = best
        raw = job / "audio" / f"raw_{ln.line_id}.wav"
        out = job / "audio" / f"{ln.line_id}.wav"
        sf.write(raw, x, sr, subtype="PCM_16")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"atempo={pace}", "-ar", "44100", "-ac", "1", str(out)],
                       check=True)
        y, ysr = sf.read(out)
        chars += len(ln.tts_text)
        lines[ln.line_id] = LineAudio(line_id=ln.line_id, path=f"audio/{ln.line_id}.wav", duration_sec=round(len(y) / ysr, 3),
                                      asr_text=hyp, asr_similarity=round(sim, 3), attempts=attempt)
        print(f"{ln.line_id} {lines[ln.line_id].duration_sec:.2f}s sim={sim:.3f} try={attempt}", flush=True)
    track = NarrationTrack(provider=preset.models.tts, pace=pace, lines=lines)
    (job / "narration.json").write_text(track.model_dump_json(indent=1))
    usage = UsageRecord(stage="narration", provider=preset.models.tts.provider, model=preset.models.tts.model, characters=chars,
                        compute_sec=round(time.time() - t0, 1))
    return track, usage


if __name__ == "__main__":
    tr, us = run(Path(sys.argv[1]))
    print("total", round(sum(l.duration_sec for l in tr.lines.values()), 2), "s", us.model_dump())
