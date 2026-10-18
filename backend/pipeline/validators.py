import re

from .contracts import Check, FactSheet, StyleSpec, Storyboard
from .render_kit.theme import GAP_SEC, SUBTITLE

RATE = {"ko": ("syllable", 5.94), "en": ("word", 2.6)}
NUM = re.compile(r"(?<![A-Za-z_])-?\d+(?:\.\d+)?")
NO_CLAIM_SECTIONS = {"hook", "outro"}


def width_units(row):
    return sum(SUBTITLE["hangul_unit"] if "가" <= ch <= "힣" else SUBTITLE["other_unit"] for ch in row)


def units(text, lang):
    return len(re.sub(r"[^가-힣A-Za-z]", "", text)) if lang == "ko" else len(re.findall(r"[A-Za-z']+", text))


def estimate_sec(sb: Storyboard, pace: float) -> float:
    unit, rate = RATE[sb.language]
    speech = sum(units(ln.tts_text, sb.language) for ln in sb.all_lines()) / (rate * pace)
    return speech + GAP_SEC * len(sb.all_lines()) + 0.35 * len(sb.scenes) + 1.3


def fact_numbers(f) -> set[float]:
    blob = " ".join(str(x) for x in [f.statement, f.value, f.condition, f.latex, f.params] if x)
    return {float(m) for m in NUM.findall(blob)}


def validate_storyboard(sb: Storyboard, style: StyleSpec, facts: FactSheet) -> list[Check]:
    checks = []
    have = {s.section for s in sb.scenes}
    miss = [s for s in style.narrative.required_sections if s not in have]
    checks.append(Check(name="required_sections", passed=not miss, detail=f"missing {miss}" if miss else ""))

    bad = []
    for ln in sb.all_lines():
        rows = ln.subtitle.split("\n")
        if len(rows) > SUBTITLE["max_lines"] or any(width_units(r) > SUBTITLE["max_units"] for r in rows):
            bad.append(ln.line_id)
    checks.append(Check(name="subtitle_shape", passed=not bad, detail=f"too long: {bad}" if bad else ""))

    ids = facts.ids()
    unknown, uncited = [], []
    for s in sb.scenes:
        for ln in s.lines:
            unknown += [c for c in ln.claims if c not in ids]
            if not ln.claims and s.section not in NO_CLAIM_SECTIONS:
                uncited.append(ln.line_id)
    checks.append(Check(name="claims_exist", passed=not unknown, detail=f"unknown fact ids {unknown}" if unknown else ""))
    checks.append(Check(name="claims_cited", passed=not uncited, detail=f"lines without claims {uncited}" if uncited else ""))

    by_id = {f.id: f for f in facts.facts}
    ungrounded = []
    for ln in sb.all_lines():
        nums = {float(m) for m in NUM.findall(ln.subtitle)}
        allowed = set().union(*[fact_numbers(by_id[c]) for c in ln.claims if c in by_id]) if ln.claims else set()
        extra = [n for n in nums if not any(abs(n - a) < 1e-9 for a in allowed)]
        if extra:
            ungrounded.append(f"{ln.line_id}:{extra}")
    checks.append(Check(name="numbers_grounded", passed=not ungrounded, detail="; ".join(ungrounded)))

    if sb.language == "ko":
        digits = [ln.line_id for ln in sb.all_lines() if re.search(r"\d", ln.tts_text)]
        checks.append(Check(name="tts_numbers_spelled", passed=not digits, detail=f"digits in tts_text {digits}" if digits else ""))

    est = estimate_sec(sb, style.voice.pace)
    lo, hi = style.target_length_sec * 0.8, style.target_length_sec * 1.2
    checks.append(Check(name="length_budget", passed=lo <= est <= hi, detail=f"estimated {est:.1f}s, target {style.target_length_sec}s"))
    return checks
