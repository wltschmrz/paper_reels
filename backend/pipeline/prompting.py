import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .contracts import FactSheet, Storyboard, StyleSpec
from .style_compile import compile_style

P = Path(__file__).parent / "prompts"
SECTIONS = ("SYSTEM_FIXED", "SYSTEM_STYLE", "SYSTEM_EXAMPLE", "USER_DATA", "USER_TASK")
CACHED = {"SYSTEM_FIXED", "SYSTEM_STYLE", "SYSTEM_EXAMPLE", "USER_DATA"}
DROP_SECTIONS = re.compile(r"^(references|bibliography|acknowledg|ai use statement|author contributions|broader impact)", re.I)


@dataclass
class Block:
    text: str
    cache: bool


@dataclass
class Prompt:
    system: list[Block] = field(default_factory=list)
    user: list[Block] = field(default_factory=list)

    def __iter__(self):
        # Preserve existing runner/provider pair interface without dropping cache boundaries.
        yield BlockText(self.system)
        yield BlockText(self.user)

    def extend_user(self, text: str):
        self.user.append(Block(text, False))
        return self

    def text(self) -> str:
        return "\n\n".join(b.text for b in self.system + self.user)


class BlockText(str):
    def __new__(cls, blocks):
        obj = super().__new__(cls, "\n\n".join(b.text for b in blocks))
        obj.blocks = list(blocks)
        return obj

    def __add__(self, text):
        return BlockText(self.blocks + ([Block(str(text), False)] if text else []))


def compact(obj) -> str:
    return obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def load(name):
    return (P / f"{name}.md").read_text()


def fill(name: str, cache: bool = True, **slots) -> Prompt:
    text = load(name).replace("{{FIDELITY_RULES}}", load("fidelity_rules"))
    for k, v in slots.items():
        text = text.replace("{{" + k + "}}", compact(v))
    parts = re.split(r"^@@ (" + "|".join(SECTIONS) + r")\n", text, flags=re.M)
    prompt = Prompt()
    for tag, body in zip(parts[1::2], parts[2::2]):
        body = body.strip()
        if body:
            (prompt.system if tag.startswith("SYSTEM") else prompt.user).append(Block(body, cache and tag in CACHED))
    return prompt


def trim_paper(paper: dict) -> dict:
    out = dict(paper)
    out["sections"] = [s for s in paper.get("sections", []) if not DROP_SECTIONS.match(s.get("title", "").strip())]
    return out


def schema(model) -> dict:
    s = model.model_json_schema()
    for d in [s] + list(s.get("$defs", {}).values()):
        d.pop("title", None)
        for p in d.get("properties", {}).values():
            p.pop("title", None)
    return s


def understand(paper_json: dict) -> Prompt:
    paper_json = dict(paper_json)
    sections = []
    for item in paper_json.get("sections", []):
        item = dict(item)
        if item["id"].startswith("latex"):
            if not item["title"].startswith("sections/"):
                continue
            item["text"] = re.sub(r"(?m)^\s*%.*$", "", item["text"])
        sections.append(item)
    paper_json["sections"] = sections
    if len(compact(paper_json)) > 450_000:
        raise ValueError("Paper exceeds single-pass budget")
    return fill("understand", cache=False, PAPER_JSON=trim_paper(paper_json), FACTSHEET_SCHEMA=schema(FactSheet))


def storyboard(facts: FactSheet, style: StyleSpec) -> Prompt:
    return fill("storyboard", STYLE_BLOCK=compile_style(style), VISUAL_CATALOG=load("visual_catalog"),
                STORYBOARD_EXAMPLE=(P / "examples" / "storyboard_excerpt.json").read_text(),
                STORYBOARD_SCHEMA=schema(Storyboard), FACTS_JSON=facts.model_dump(exclude_none=True))


def visual_code(scene: dict, durations: dict, facts: list[dict], style: StyleSpec, golden_example: str, repair: str = "",
                cache_example: bool = True) -> Prompt:
    p = fill("visual_code", STYLE_BLOCK=compile_style(style), RENDER_KIT_API=load("render_kit_api"), GOLDEN_EXAMPLE=golden_example,
                SCENE_JSON=scene, DURATIONS_JSON=durations, FACTS_JSON=facts, REPAIR_CONTEXT=repair)
    p.system[-1].cache = cache_example
    return p


def visual_qa(scene: dict) -> Prompt:
    return fill("visual_qa", SCENE_JSON=scene)


def judge(timeline: list, onscreen: dict, facts: FactSheet) -> Prompt:
    return fill("judge", cache=False, TIMELINE_JSON=timeline, ONSCREEN_JSON=onscreen, FACTS_JSON=facts.model_dump(exclude_none=True))

def reference_direction():
    """Borrow visual grammar, not the Flow Map paper's claims or fixed scene sequence."""
    path = P.parents[1] / "golden/flowmap_2610.20674/storyboard.json"
    scenes = json.loads(path.read_text())["scenes"]
    return json.dumps([{"section": s["section"], "visual": s["visual"]["type"],
                        "choreography": s["visual"]["description"]} for s in scenes], ensure_ascii=False)


def reference_scene(visual_type: str):
    root = P.parents[1] / "golden/flowmap_2610.20674"
    examples = {"title_card":"S1", "cards":"S1", "flow_plot":"S4", "function_plot":"S5",
                "param_sweep":"S6", "equation_build":"S3", "bar_chart":"S7", "diagram":"S3", "custom":"S4"}
    code = (root / "scenes" / (examples.get(visual_type, "S4") + ".py")).read_text()
    helpers = (root / "scenes/_shared.py").read_text().split("def sig", 1)[1]
    return code.replace("from _shared import *\n", "from _shared import *\n\ndef sig" + helpers + "\n", 1)
