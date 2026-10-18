import json
import re
from pathlib import Path

from .contracts import FactSheet, Storyboard, StyleSpec
from .style_compile import compile_style

P = Path(__file__).parent / "prompts"


def load(name):
    return (P / f"{name}.md").read_text()


def fill(name: str, **slots) -> tuple[str, str]:
    text = load(name).replace("{{FIDELITY_RULES}}", load("fidelity_rules"))
    for k, v in slots.items():
        text = text.replace("{{" + k + "}}", v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, indent=1))
    system, _, user = text.partition("\nUSER\n")
    return system.replace("SYSTEM\n", "", 1).strip(), user.strip()


def understand(paper_json: dict):
    # Use page-numbered PDF text once, plus compact LaTeX evidence (not plotting coordinates).
    paper_json = dict(paper_json)
    sections = []
    for section in paper_json.get("sections", []):
        section = dict(section)
        if section["id"].startswith("latex"):
            if not section["title"].startswith("sections/"):
                continue
            section["text"] = re.sub(r"(?m)^\s*%.*$", "", section["text"])
        sections.append(section)
    paper_json["sections"] = sections
    payload = json.dumps(paper_json, ensure_ascii=False)
    if len(payload) > 450_000:
        raise ValueError("Paper exceeds single-pass extraction budget; chunked extraction required")
    return fill("understand", PAPER_JSON=paper_json, FACTSHEET_SCHEMA=FactSheet.model_json_schema())


def reference_direction():
    """Borrow visual grammar, not the Flow Map paper's claims or fixed scene sequence."""
    path = P.parents[1] / "golden/flowmap_2610.20674/storyboard.json"
    scenes = json.loads(path.read_text())["scenes"]
    return json.dumps([{"section": s["section"], "visual": s["visual"]["type"],
                        "choreography": s["visual"]["description"]} for s in scenes], ensure_ascii=False)


def reference_scene(visual_type: str):
    root = P.parents[1] / "golden/flowmap_2610.20674"
    scenes = json.loads((root / "storyboard.json").read_text())["scenes"]
    match = next((s for s in scenes if s["visual"]["type"] == visual_type), None)
    return (root / "scenes" / (match["scene_id"] + ".py" if match else "S4.py")).read_text()


def storyboard(facts: FactSheet, style: StyleSpec):
    return fill("storyboard", STYLE_BLOCK=compile_style(style), VISUAL_CATALOG=load("visual_catalog"),
                STORYBOARD_SCHEMA=Storyboard.model_json_schema(), FACTS_JSON=facts.model_dump(), REFERENCE_DIRECTION=reference_direction())


def visual_code(scene: dict, durations: dict, facts: list[dict], style: StyleSpec, golden_example: str, repair: str = ""):
    return fill("visual_code", SCENE_ID=scene["scene_id"], STYLE_BLOCK=compile_style(style), RENDER_KIT_API=load("render_kit_api"),
                GOLDEN_EXAMPLE=golden_example, SCENE_JSON=scene, DURATIONS_JSON=durations, FACTS_JSON=facts, REPAIR_CONTEXT=repair)


def visual_qa(scene: dict):
    return fill("visual_qa", SCENE_JSON=scene)


def judge(timeline: list, onscreen: dict, facts: FactSheet):
    return fill("judge", TIMELINE_JSON=timeline, ONSCREEN_JSON=onscreen, FACTS_JSON=facts.model_dump())
