from .contracts import StyleSpec
from .validators import RATE

AUDIENCE = {
    "beginner": "Assume no background beyond high-school math. Define every technical term the first time with an everyday picture. Prefer one idea per scene.",
    "grad": "Assume a first-year ML graduate student. Standard ML terms may be used, but paper-specific terms must be defined on screen.",
    "expert": "Assume a researcher in the field. Skip textbook background; spend time on what is new, the key equation, and evidence.",
}

TONE = {
    "calm_visual": "Calm, curious narration in the style of 3Blue1Brown: pose a question, let the picture answer it, short sentences, no hype words.",
    "energetic_shorts": "Fast, punchy Korean-YouTube-shorts narration: strong hook in the first 3 seconds, one surprise per scene, short sentences.",
    "lecture": "Clear lecture tone: state, show, explain, in that order; precise wording over flair.",
    "critical_review": "Reviewer tone: state the claim, then the evidence, then what is assumed or not shown. Neutral, never dismissive.",
}

LENS = {
    "geometric": "Show ideas as geometry: trajectories, vector fields, curves, areas, positions moving over time. The picture carries the argument; equations sit beside it as labels.",
    "equation": "Put the key equation at the center. Build it term by term with color, and say what each term means before moving on.",
    "analogy": "Anchor each abstract step in one concrete everyday analogy, then map the analogy back to the paper's object explicitly.",
    "empirical": "Lead with the numbers: show the paper's tables as bar or line charts, always naming dataset, metric, and condition.",
}

MATH = {
    0: "Do not show equations; describe the mathematics in words and pictures only.",
    1: "Show at most one or two key equations, each as a labeled object, without derivation.",
    2: "Show the key equations and explain each term; include one short transformation step if it carries the insight.",
    3: "Walk through the core derivation or theorem statement step by step; every displayed step must be from the paper.",
}

OPENING = {
    "hook_question": "Open with a question the paper answers, in one sentence.",
    "hook_number": "Open with the single most striking number from the results, with its condition.",
    "problem_first": "Open by stating the problem the paper solves, in one sentence.",
}

ENDING = {
    "takeaway": "End with a one-sentence takeaway, then a closing card pointing to the arXiv ID.",
    "open_question": "End with the open question the paper leaves, then the arXiv card.",
    "limitation": "End on the main limitation stated by the authors, then the arXiv card.",
}


def lens_block(style: StyleSpec) -> str:
    w = style.lens.model_dump()
    ranked = sorted(w.items(), key=lambda kv: -kv[1])
    rows = [f"- {k} ({v:.0%} of screen time): {LENS[k]}" for k, v in ranked if v >= 0.05]
    return "\n".join(rows)


def compile_style(style: StyleSpec) -> str:
    unit, rate = RATE[style.language]
    budget = int(style.target_length_sec * rate * style.voice.pace * 0.88)
    parts = [
        f"LANGUAGE: {'Korean' if style.language == 'ko' else 'English'} for subtitles and narration. Keep English technical terms in English on screen.",
        f"LENGTH: target {style.target_length_sec} s. Narration budget about {budget} {unit}s in total across all tts_text.",
        f"AUDIENCE: {AUDIENCE[style.audience]}",
        f"TONE: {TONE[style.tone]}",
        "EXPLANATION LENS (allocate screen time roughly by these weights):\n" + lens_block(style),
        f"MATH DEPTH {style.math.depth}: {MATH[style.math.depth]} Hold any displayed equation at least {style.math.min_equation_dwell_sec:.1f} s."
        + (" Color each named term consistently across scenes." if style.math.color_terms else ""),
        "REQUIRED SECTIONS (each must be the section tag of at least one scene): " + ", ".join(style.narrative.required_sections),
        f"OPENING: {OPENING[style.narrative.opening]}",
        f"ENDING: {ENDING[style.narrative.ending]}",
    ]
    if style.free_instruction.strip():
        parts.append("CREATOR NOTE (follow unless it conflicts with any rule above or with the fidelity rules):\n" + style.free_instruction.strip())
    return "\n\n".join(parts)
