from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

PIPELINE_VERSION = "0.1.0"

Lang = Literal["ko", "en"]
SectionTag = Literal["hook", "background", "problem", "method", "theory", "result", "limitation", "takeaway", "outro"]
VisualType = Literal[
    "title_card", "cards", "flow_plot", "function_plot", "param_sweep", "equation_build", "bar_chart", "diagram", "custom"
]
JobStatus = Literal["queued", "running", "needs_review", "failed", "published", "cancelled"]
StageName = Literal[
    "ingest", "understand", "storyboard", "narration", "visual_code", "preview_qa", "final_render", "compose", "validate", "publish"
]


class SourceRef(BaseModel):
    kind: Literal["abstract", "section", "equation", "theorem", "table", "figure", "appendix", "page"]
    label: str
    page: Optional[int] = None
    quote: Optional[str] = None


class ModelChoice(BaseModel):
    provider: str
    model: str
    params: dict = Field(default_factory=dict)


class ModelConfig(BaseModel):
    understand: ModelChoice
    storyboard: ModelChoice
    visual_code: ModelChoice
    visual_qa: ModelChoice
    judge: ModelChoice
    tts: ModelChoice
    asr: ModelChoice
    thumbnail: ModelChoice


class Lens(BaseModel):
    geometric: float = Field(0.5, ge=0)
    equation: float = Field(0.2, ge=0)
    analogy: float = Field(0.1, ge=0)
    empirical: float = Field(0.2, ge=0)

    @model_validator(mode="after")
    def _normalize(self):
        s = self.geometric + self.equation + self.analogy + self.empirical
        if s <= 0:
            raise ValueError("lens weights must not all be zero")
        self.geometric, self.equation, self.analogy, self.empirical = (
            self.geometric / s, self.equation / s, self.analogy / s, self.empirical / s)
        return self


Arc = Literal["mystery_twist", "problem_method_result", "claim_evidence_caveat", "derivation_walkthrough"]

class Narrative(BaseModel):
    arc: Arc = "mystery_twist"
    required_sections: list[SectionTag] = Field(default_factory=lambda: ["problem", "method", "result"])
    opening: Literal["hook_question", "hook_number", "problem_first"] = "hook_question"
    ending: Literal["takeaway", "open_question", "limitation"] = "takeaway"


class MathPolicy(BaseModel):
    depth: int = Field(1, ge=0, le=3)
    min_equation_dwell_sec: float = Field(2.5, ge=0, le=10)
    color_terms: bool = True


class VisualPolicy(BaseModel):
    theme: Literal["dark", "light"] = "dark"
    subtitles: bool = True
    term_header: bool = True
    source_line: bool = True
    bgm: Literal["none", "soft_pad"] = "soft_pad"
    bgm_db: float = Field(-28, ge=-40, le=-18)


class VoicePolicy(BaseModel):
    pace: float = Field(1.22, ge=0.9, le=1.4)


class StyleSpec(BaseModel):
    language: Lang = "ko"
    audience: Literal["beginner", "grad", "expert"] = "grad"
    target_length_sec: int = Field(60, ge=30, le=90)
    tone: Literal["calm_visual", "energetic_shorts", "lecture", "critical_review"] = "calm_visual"
    lens: Lens = Field(default_factory=Lens)
    narrative: Narrative = Field(default_factory=Narrative)
    math: MathPolicy = Field(default_factory=MathPolicy)
    visual: VisualPolicy = Field(default_factory=VisualPolicy)
    voice: VoicePolicy = Field(default_factory=VoicePolicy)
    free_instruction: str = Field("", max_length=600)


class Preset(BaseModel):
    preset_id: str
    name: str
    creator_id: str
    visibility: Literal["public", "private"] = "private"
    style: StyleSpec
    models: ModelConfig


class Section(BaseModel):
    id: str
    title: str
    text: str
    page: Optional[int] = None


class Equation(BaseModel):
    id: str
    label: str
    latex: Optional[str] = None
    context: str = ""


class Table(BaseModel):
    id: str
    label: str
    caption: str
    text: str


class Figure(BaseModel):
    id: str
    label: str
    caption: str
    page: Optional[int] = None
    image_path: Optional[str] = None


class PaperDoc(BaseModel):
    paper_id: str
    arxiv_id: Optional[str] = None
    version: Optional[str] = None
    source_kind: Literal["latex", "pdf"]
    title: str
    authors: list[str]
    abstract: str
    sections: list[Section]
    equations: list[Equation] = Field(default_factory=list)
    tables: list[Table] = Field(default_factory=list)
    figures: list[Figure] = Field(default_factory=list)


class Fact(BaseModel):
    id: str
    kind: Literal["problem", "method", "contribution", "definition", "equation", "theorem", "setup", "result", "limitation", "tension"]
    statement: str
    value: Optional[str] = None
    condition: Optional[str] = None
    latex: Optional[str] = None
    params: dict = Field(default_factory=dict)
    source: SourceRef


class Term(BaseModel):
    term: str
    definition: str


class FactSheet(BaseModel):
    paper_id: str
    pipeline_version: str = PIPELINE_VERSION
    extractor: Optional[ModelChoice] = None
    facts: list[Fact]
    glossary: list[Term] = Field(default_factory=list)

    def ids(self) -> set[str]:
        return {f.id for f in self.facts}


class SceneHeader(BaseModel):
    definition: str
    source: str


class VisualIntent(BaseModel):
    type: VisualType
    description: str
    moving: str = ""
    reuse_frame_from: Optional[str] = None
    fact_refs: list[str] = Field(default_factory=list)


class Line(BaseModel):
    line_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")
    subtitle: str
    tts_text: str
    claims: list[str] = Field(default_factory=list)


class Scene(BaseModel):
    scene_id: str
    section: SectionTag
    header: SceneHeader
    visual: VisualIntent
    lines: list[Line]
    min_dwell_sec: float = 0.0


class RenderFlags(BaseModel):
    subtitles: bool = True
    term_header: bool = True
    source_line: bool = True
    theme: Literal["dark", "light"] = "dark"


class Storyboard(BaseModel):
    paper_id: str
    preset_id: str
    language: Lang
    title: str
    hook_title: str
    render: RenderFlags = Field(default_factory=RenderFlags)
    scenes: list[Scene]

    @model_validator(mode="after")
    def _ids(self):
        seen = set()
        if len({s.scene_id for s in self.scenes}) != len(self.scenes):
            raise ValueError("duplicate scene IDs")
        for s in self.scenes:
            if not re.fullmatch(r"S\d{1,2}", s.scene_id):
                raise ValueError(f"scene_id must look like S1..S99: {s.scene_id}")
            for ln in s.lines:
                if ln.line_id in seen:
                    raise ValueError(f"duplicate line_id {ln.line_id}")
                seen.add(ln.line_id)
        return self

    def all_lines(self) -> list[Line]:
        return [ln for s in self.scenes for ln in s.lines]


class LineAudio(BaseModel):
    line_id: str
    path: str
    duration_sec: float
    asr_text: str = ""
    asr_similarity: float = 0.0
    attempts: int = 1


class NarrationTrack(BaseModel):
    provider: ModelChoice
    pace: float
    lines: dict[str, LineAudio]


class TimelineEntry(BaseModel):
    scene_id: str
    line_id: str
    start: float
    end: float
    subtitle: str = ""
    claims: list[str] = Field(default_factory=list)


class QAIssue(BaseModel):
    scene_id: str
    line_id: Optional[str] = None
    severity: Literal["blocker", "major", "minor"]
    problem: str
    fix_hint: str = ""


class SceneRender(BaseModel):
    scene_id: str
    path: str
    duration_sec: float
    overrun_sec: float = 0.0
    attempts: int = 1
    qa_issues: list[QAIssue] = Field(default_factory=list)


class ClaimVerdict(BaseModel):
    line_id: str
    verdict: Literal["supported", "unsupported", "contradicted", "overgeneralized", "no_claim"]
    note: str = ""


class Check(BaseModel):
    name: str
    passed: bool
    detail: str = ""


class ValidationReport(BaseModel):
    checks: list[Check]
    claim_verdicts: list[ClaimVerdict] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)


class UsageRecord(BaseModel):
    stage: StageName
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    characters: int = 0
    compute_sec: float = 0.0
    est_cost_usd: float = 0.0


class JobState(BaseModel):
    job_id: str
    paper_id: str
    user_id: str
    preset_id: str
    status: JobStatus = "queued"
    stage: Optional[StageName] = None
    progress: float = 0.0
    error: Optional[str] = None
    usage: list[UsageRecord] = Field(default_factory=list)


class ShortManifest(BaseModel):
    short_id: str
    paper_id: str
    creator_id: str
    preset_snapshot: Preset
    pipeline_version: str = PIPELINE_VERSION
    video_path: str
    thumbnail_path: str
    captions_path: str
    claims_timeline_path: str
    duration_sec: float
    usage: list[UsageRecord] = Field(default_factory=list)
