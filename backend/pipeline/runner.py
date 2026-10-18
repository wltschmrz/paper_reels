import json
import re
import sys
import time
import os
import hashlib
from filelock import FileLock
from pathlib import Path

from . import prompting
from .contracts import (
    Check,
    FactSheet,
    JobState,
    Preset,
    QAIssue,
    Storyboard,
    UsageRecord,
    ValidationReport,
    PaperDoc,
    ClaimVerdict,
)
from .providers.base import get_llm
from .stages import compose, lint, narration, render
from .validators import validate_storyboard

STAGES = [
    ("ingest", 0.03),
    ("understand", 0.10),
    ("storyboard", 0.10),
    ("narration", 0.17),
    ("visual_code", 0.15),
    ("preview_qa", 0.20),
    ("final_render", 0.15),
    ("compose", 0.05),
    ("validate", 0.05),
]
PRICING = Path(__file__).resolve().parents[1] / "pricing.json"
GOLDEN_SCENE = (
    Path(__file__).resolve().parents[1]
    / "golden"
    / "flowmap_2610.20674"
    / "scenes"
    / "S4.py"
)


class Ctx:
    def __init__(self, job: Path, keys: dict, on_progress):
        self.job, self.keys, self.on_progress = job, keys, on_progress
        self.preset = Preset.model_validate_json((job / "preset.json").read_text())
        self.state = (
            JobState.model_validate_json((job / "job.json").read_text())
            if (job / "job.json").exists()
            else JobState(
                job_id=job.name,
                paper_id="",
                user_id=self.preset.creator_id,
                preset_id=self.preset.preset_id,
            )
        )
        self.prices = json.loads(PRICING.read_text()) if PRICING.exists() else {}

    def save(self):
        temp = self.job / "job.tmp"
        temp.write_text(self.state.model_dump_json(indent=1))
        temp.replace(self.job / "job.json")

    def llm(self, stage, choice):
        key = self.keys.get(choice.provider)
        if not key:
            raise PermissionError(
                f"no API key for provider {choice.provider} (stage {stage})"
            )
        return get_llm(choice, key)

    def charge(self, stage, choice, usage: dict):
        p = self.prices.get(choice.provider, {}).get(choice.model, {})
        cost = usage.get("input_tokens", 0) / 1e6 * p.get(
            "input_per_mtok", 0
        ) + usage.get("output_tokens", 0) / 1e6 * p.get("output_per_mtok", 0)
        self.state.usage.append(
            UsageRecord(
                stage=stage,
                provider=choice.provider,
                model=choice.model,
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                est_cost_usd=round(cost, 4),
            )
        )
        self.save()


def first_json(text):
    i, j = text.find("{"), text.rfind("}")
    return json.loads(text[i : j + 1])


def code_block(text):
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    return m.group(1) if m else text


def ask_json(ctx, stage, choice, system, user, model_cls, extra_check=None, tries=3):
    llm, note = ctx.llm(stage, choice), ""
    for _ in range(tries):
        text, usage = llm.complete(system, user + note)
        ctx.charge(stage, choice, usage)
        try:
            obj = model_cls.model_validate(first_json(text))
            problems = extra_check(obj) if extra_check else []
            if not problems:
                return obj
            note = (
                "\n\nYOUR PREVIOUS OUTPUT FAILED THESE CHECKS, FIX THEM:\n"
                + "\n".join(problems)
            )
        except Exception as e:
            note = f"\n\nYOUR PREVIOUS OUTPUT WAS INVALID: {e}. Return valid JSON only."
    raise RuntimeError(f"{stage}: no valid output after {tries} tries")


def done(ctx, name):
    j = ctx.job
    if name == "ingest":
        return (j / "paper.json").exists() or (j / "facts.json").exists()
    if name == "visual_code":
        sb = Storyboard.model_validate_json((j / "storyboard.json").read_text())
        return all((j / "scenes" / f"{s.scene_id}.py").exists() for s in sb.scenes)
    marker = {
        "understand": "facts.json",
        "storyboard": "storyboard.json",
        "narration": "narration.json",
        "preview_qa": "render/preview/qa.json",
        "final_render": "render/final/render_report.json",
        "compose": "out/short.mp4",
        "validate": "out/validation.json",
    }[name]
    return (j / marker).exists()


def stage_ingest(ctx):
    from .stages.ingest import ingest
    from app.settings import DATA

    paper = ingest(ctx.state.paper_id, DATA / "papers" / ctx.state.paper_id)
    (ctx.job / "paper.json").write_text(paper.model_dump_json(indent=2))


def stage_understand(ctx):
    from .stages.ingest import quote_errors
    from app.settings import DATA

    paper = PaperDoc.model_validate_json((ctx.job / "paper.json").read_text())
    choice = ctx.preset.models.understand
    digest = hashlib.sha256(
        (paper.model_dump_json() + choice.model_dump_json() + "facts-v2").encode()
    ).hexdigest()
    cache = DATA / "facts"
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (digest + ".json")
    with FileLock(str(path) + ".lock", timeout=600):
        if path.exists():
            fs = FactSheet.model_validate_json(path.read_text())
        else:
            s, u = prompting.understand(paper.model_dump())
            fs = ask_json(
                ctx,
                "understand",
                choice,
                s,
                u,
                FactSheet,
                lambda f: quote_errors(f, paper),
            )
            fs.extractor = choice
            temp = path.with_suffix(".tmp")
            temp.write_text(fs.model_dump_json(indent=2))
            temp.replace(path)
        (ctx.job / "facts.json").write_text(fs.model_dump_json(indent=2))


def stage_storyboard(ctx):
    fs = FactSheet.model_validate_json((ctx.job / "facts.json").read_text())
    s, u = prompting.storyboard(fs, ctx.preset.style)
    check = lambda sb: [
        f"{c.name}: {c.detail}"
        for c in validate_storyboard(sb, ctx.preset.style, fs)
        if not c.passed
    ]
    sb = ask_json(
        ctx, "storyboard", ctx.preset.models.storyboard, s, u, Storyboard, check
    )
    v = ctx.preset.style.visual
    sb.preset_id = ctx.preset.preset_id
    (
        sb.render.subtitles,
        sb.render.term_header,
        sb.render.source_line,
        sb.render.theme,
    ) = v.subtitles, v.term_header, v.source_line, v.theme
    (ctx.job / "storyboard.json").write_text(sb.model_dump_json(indent=1))


def stage_narration(ctx):
    _, usage = narration.run(ctx.job)
    ctx.state.usage.append(usage)


def write_scene(ctx, scene, repair=""):
    sb = json.loads((ctx.job / "storyboard.json").read_text())
    nar = json.loads((ctx.job / "narration.json").read_text())
    facts = {
        f["id"]: f for f in json.loads((ctx.job / "facts.json").read_text())["facts"]
    }
    durs = {
        ln["line_id"]: nar["lines"][ln["line_id"]]["duration_sec"]
        for ln in scene["lines"]
    }
    used = [
        facts[i]
        for i in set(
            scene["visual"]["fact_refs"]
            + [c for ln in scene["lines"] for c in ln["claims"]]
        )
        if i in facts
    ]
    choice = ctx.preset.models.visual_code
    llm = ctx.llm("visual_code", choice)
    s, u = prompting.visual_code(
        scene, durs, used, ctx.preset.style, prompting.reference_scene(scene["visual"]["type"]), repair
    )
    path = ctx.job / "scenes" / f"{scene['scene_id']}.py"
    for _ in range(3):
        text, usage = llm.complete(s, u, max_tokens=12000)
        ctx.charge("visual_code", choice, usage)
        path.write_text(code_block(text))
        issues = lint.lint_scene(path, Storyboard.model_validate(sb))
        if not issues:
            return
        u += "\n\nLINT ERRORS, FIX THEM:\n" + "\n".join(issues)
    raise RuntimeError(f"visual_code {scene['scene_id']}: lint failed")


def stage_visual_code(ctx):
    (ctx.job / "scenes").mkdir(exist_ok=True)
    shared = ctx.job / "scenes" / "_shared.py"
    if not shared.exists():
        shared.write_text(
            "from render_kit import C\n\n\ndef pal():\n    return C['FG'], C['GRAY'], C['MGRAY'], C['DGRAY'], C['YEL'], C['TEAL'], C['RED']\n"
        )
    sb = json.loads((ctx.job / "storyboard.json").read_text())
    for scene in sb["scenes"]:
        if not (ctx.job / "scenes" / f"{scene['scene_id']}.py").exists():
            write_scene(ctx, scene)


def qa_scene(ctx, scene) -> list[QAIssue]:
    choice = ctx.preset.models.visual_qa
    if not ctx.keys.get(choice.provider):
        return []
    s, u = prompting.visual_qa(scene)
    img = (
        ctx.job / "render" / "preview" / f"sheet_{scene['scene_id']}.png"
    ).read_bytes()
    text, usage = ctx.llm("preview_qa", choice).complete(
        s, u, images=[img], max_tokens=2000
    )
    ctx.charge("preview_qa", choice, usage)
    return [QAIssue.model_validate(i) for i in first_json(text).get("issues", [])]


def stage_preview_qa(ctx, max_repairs=2):
    sb = json.loads((ctx.job / "storyboard.json").read_text())
    by_id = {s["scene_id"]: s for s in sb["scenes"]}
    todo, log = list(by_id), {}
    for attempt in range(max_repairs + 1):
        reports, errors = render.run(ctx.job, "preview", only=todo)
        bad = {}
        for sid, err in errors.items():
            bad[sid] = f"RENDER ERROR:\n{err}"
        for r in reports:
            issues = [
                i
                for i in qa_scene(ctx, by_id[r.scene_id])
                if i.severity in ("blocker", "major")
            ]
            if r.overrun_sec > 0.3:
                issues.append(
                    QAIssue(
                        scene_id=r.scene_id,
                        severity="major",
                        problem=f"animations overrun narration by {r.overrun_sec:.2f}s",
                    )
                )
            log[r.scene_id] = [i.model_dump() for i in issues]
            if issues:
                bad[r.scene_id] = "REVIEW ISSUES:\n" + "\n".join(
                    f"- [{i.severity}] {i.problem} -> {i.fix_hint}" for i in issues
                )
        if not bad or attempt == max_repairs:
            break
        for sid, msg in bad.items():
            prev = (ctx.job / "scenes" / f"{sid}.py").read_text()
            write_scene(ctx, by_id[sid], repair=f"PREVIOUS CODE:\n{prev}\n\n{msg}")
        todo = list(bad)
    (ctx.job / "render" / "preview" / "qa.json").write_text(
        json.dumps(
            {"issues": log, "unresolved": list(bad)}, ensure_ascii=False, indent=1
        )
    )


def stage_final_render(ctx):
    _, errors = render.run(ctx.job, "final")
    if errors:
        raise RuntimeError(f"final render failed: {list(errors)}")


def stage_compose(ctx):
    compose.run(ctx.job)


def stage_validate(ctx):
    sb = Storyboard.model_validate_json((ctx.job / "storyboard.json").read_text())
    fs = FactSheet.model_validate_json((ctx.job / "facts.json").read_text())
    nar = json.loads((ctx.job / "narration.json").read_text())
    checks = validate_storyboard(sb, ctx.preset.style, fs)
    numeric = {ln.line_id for ln in sb.all_lines() if re.search(r"\d", ln.subtitle)}
    weak = [
        k
        for k, v in nar["lines"].items()
        if v["asr_similarity"] < (0.65 if k in numeric else 0.85)
    ]
    checks.append(
        Check(
            name="narration_intelligible",
            passed=not weak,
            detail=f"low ASR similarity {weak}" if weak else "",
        )
    )
    rr = json.loads((ctx.job / "render" / "final" / "render_report.json").read_text())
    over = [s["scene_id"] for s in rr["scenes"] if s["overrun_sec"] > 0.3]
    checks.append(
        Check(name="no_overrun", passed=not over, detail=str(over) if over else "")
    )
    qa = ctx.job / "render" / "preview" / "qa.json"
    unresolved = json.loads(qa.read_text())["unresolved"] if qa.exists() else []
    checks.append(
        Check(
            name="layout_qa",
            passed=not unresolved,
            detail=str(unresolved) if unresolved else "",
        )
    )
    if not ctx.keys.get(ctx.preset.models.visual_qa.provider):
        checks.append(
            Check(
                name="visual_review_executed",
                passed=os.getenv("SS_RENDER_MODE") == "trusted_golden",
                detail="skipped: no visual QA key",
            )
        )
    report = ValidationReport(checks=checks)
    choice = ctx.preset.models.judge
    if ctx.keys.get(choice.provider):
        timeline = json.loads((ctx.job / "out" / "claims_timeline.json").read_text())
        onscreen = {
            s.scene_id: json.loads(
                (ctx.job / "render" / f"report_{s.scene_id}.json").read_text()
            )["onscreen_text"]
            for s in sb.scenes
        }
        s, u = prompting.judge(timeline, onscreen, fs)
        text, usage = ctx.llm("validate", choice).complete(s, u, max_tokens=6000)
        ctx.charge("validate", choice, usage)
        out = first_json(text)
        report.claim_verdicts = [
            ClaimVerdict.model_validate(v) for v in out.get("claim_verdicts", [])
        ]
        bad = [
            v.line_id
            for v in report.claim_verdicts
            if v.verdict in ("unsupported", "contradicted", "overgeneralized")
        ]
        report.checks.append(
            Check(
                name="claims_judged",
                passed=not bad
                and {v.line_id for v in report.claim_verdicts}
                == {ln.line_id for ln in sb.all_lines()}
                and not out.get("onscreen_issues"),
                detail=f"lines {bad}; onscreen {out.get('onscreen_issues')}",
            )
        )
    else:
        report.checks.append(
            Check(
                name="claims_judged",
                passed=os.getenv("SS_RENDER_MODE") == "trusted_golden",
                detail="skipped: no judge key; golden regression only, not scientific validation",
            )
        )
    (ctx.job / "out" / "validation.json").write_text(report.model_dump_json(indent=1))
    ctx.state.status = "published" if report.passed else "needs_review"


def run(job: Path, keys: dict | None = None, on_progress=print):
    ctx = Ctx(job, keys or {}, on_progress)
    ctx.state.status, progress = "running", 0.0
    ctx.state.error = None
    try:
        for name, weight in STAGES:
            if (job / "cancel.requested").exists():
                ctx.state.status = "cancelled"
                break
            if done(ctx, name):
                progress += weight
                continue
            ctx.state.stage = name
            ctx.save()
            on_progress(
                {
                    "job_id": ctx.state.job_id,
                    "stage": name,
                    "progress": round(progress, 2),
                    "status": "running",
                }
            )
            t0 = time.time()
            globals()[f"stage_{name}"](ctx)
            progress += weight
            ctx.state.progress = round(progress, 2)
            on_progress(
                {
                    "job_id": ctx.state.job_id,
                    "stage": name,
                    "progress": ctx.state.progress,
                    "sec": round(time.time() - t0, 1),
                }
            )
        if ctx.state.status == "running":
            report_path = job / "out/validation.json"
            report = (
                ValidationReport.model_validate_json(report_path.read_text())
                if report_path.exists()
                else None
            )
            ctx.state.status = (
                "published" if report and report.passed else "needs_review"
            )
    except Exception as e:
        message = f"{ctx.state.stage}: {e}"
        for secret in ctx.keys.values():
            if secret:
                message = message.replace(secret, "[REDACTED]")
        ctx.state.status, ctx.state.error = "failed", message
    ctx.state.progress = round(progress, 2)
    ctx.save()
    on_progress(
        {
            "job_id": ctx.state.job_id,
            "status": ctx.state.status,
            "error": ctx.state.error,
            "est_cost_usd": round(sum(u.est_cost_usd for u in ctx.state.usage), 4),
        }
    )
    return ctx.state


if __name__ == "__main__":
    run(Path(sys.argv[1]))
