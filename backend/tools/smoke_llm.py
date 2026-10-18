"""Explicit paid M1 probe: source -> facts -> storyboard, no generated code execution."""

import argparse, json, uuid
from pathlib import Path
from app.settings import DATA, ROOT, keys, model_choices
from pipeline.runner import Ctx, stage_ingest, stage_understand, stage_storyboard
from pipeline.contracts import Preset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["openai", "anthropic"], required=True)
    parser.add_argument("--preset", default="geometric_intuition_ko")
    args = parser.parse_args()
    if not keys()[args.provider]:
        raise SystemExit(f"Missing {args.provider} key; set backend/.env first")
    preset = Preset.model_validate_json(
        (ROOT / "presets" / f"{args.preset}.json").read_text()
    )
    choice = next(c for c in model_choices() if c["provider"] == args.provider)
    from pipeline.contracts import ModelChoice

    preset.models.understand = ModelChoice(**choice)
    preset.models.storyboard = ModelChoice(**choice)
    folder = DATA / "smoke" / uuid.uuid4().hex
    folder.mkdir(parents=True)
    (folder / "preset.json").write_text(preset.model_dump_json(indent=2))
    (folder / "job.json").write_text(
        json.dumps(
            {
                "job_id": folder.name,
                "paper_id": "2610.20674",
                "user_id": "owner",
                "preset_id": preset.preset_id,
            }
        )
    )
    ctx = Ctx(folder, keys(), print)
    for stage, func in [
        ("ingest", stage_ingest),
        ("understand", stage_understand),
        ("storyboard", stage_storyboard),
    ]:
        ctx.state.stage = stage
        func(ctx)
        ctx.save()
        print(stage, "complete", flush=True)
    print("Artifacts and measured usage:", folder)


if __name__ == "__main__":
    main()
