"""Register validated local comparison outputs; never publishes remotely."""
import json
import shutil
import subprocess
from pathlib import Path
from pipeline.contracts import ValidationReport

ROOT = Path(__file__).resolve().parents[2]

def export(provider):
    name = f'flowmap-v2-{provider}'
    job = ROOT / 'backend/data/jobs' / name
    state = json.loads((job / 'job.json').read_text())
    report = ValidationReport.model_validate_json((job / 'out/validation.json').read_text())
    if state['status'] != 'published' or not report.passed:
        raise RuntimeError(f'{name}: validation must pass before registration')
    duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(job / 'out/short.mp4')], text=True))
    for src, dest in [('short.mp4', f'videos/{name}.mp4'), ('thumbnail.jpg', f'thumbnails/{name}.jpg')]:
        shutil.copy2(job / 'out' / src, ROOT / 'public' / dest)
    evidence = ROOT / 'docs/experiments/flowmap-v2' / provider
    evidence.mkdir(parents=True, exist_ok=True)
    for src in ['budget.json', 'facts.json', 'editorial-layout-changes.json', 'fidelity-repairs.json', 'speech-fidelity-repair.json', 'preset.json', 'storyboard.json', 'provenance.json', 'editorial-changes.json', 'speech-repairs.json', 'speech-repairs-round2.json', 'events.jsonl', 'out/validation.json', 'out/claims_timeline.json', 'out/captions.srt', 'render/preview/qa.json', 'render/final/render_report.json']:
        if (job / src).exists():
            shutil.copy2(job / src, evidence / Path(src).name)
    for folder in ['before-editorial-layout', 'before-editorial-fidelity']:
        source = job / folder
        if source.exists():
            target = evidence / folder
            target.mkdir(exist_ok=True)
            if (source / 'scenes').exists():
                shutil.copytree(source / 'scenes', target / 'scenes', dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
            for item in source.glob('*.json'):
                shutil.copy2(item, target / item.name)
    shutil.copytree(job / 'scenes', evidence / 'scenes', dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
    for image in (job / 'render/preview').glob('sheet_*.png'):
        shutil.copy2(image, evidence / image.name)
    qa = json.loads((job / 'render/preview/qa.json').read_text())
    for relative in qa.get('final_review_sources', {}).values():
        target = evidence / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(job / relative, target)
    budget = json.loads((job / 'budget.json').read_text())
    events = [json.loads(line) for line in (job / 'events.jsonl').read_text().splitlines()]
    returned = [c for c in budget['calls'] if c['status'] == 'returned']
    summary = {
        'duration_sec': duration,
        'returned_usage_estimated_usd': round(sum(c['actual_usd'] for c in returned), 6),
        'uncertain_reserved_usd': round(sum(c['reserved_usd'] for c in budget['calls'] if c['status'] != 'returned'), 6),
        'estimated_usd_by_model': {model: round(sum(c['actual_usd'] for c in returned if c['model'] == model), 6) for model in sorted({c['model'] for c in returned})},
        'api_response_wait_sec': round(sum(c['seconds'] for c in returned), 2),
        'wall_elapsed_including_retries_and_manual_interventions_sec': round(events[-1]['wall_time'] - events[0]['wall_time'], 1),
        'completed_stage_sec': {stage: round(sum(e.get('sec', 0) for e in events if e.get('stage') == stage), 1) for stage in ['storyboard','narration','visual_code','preview_qa','final_render','compose','validate']},
        'tokens': {k: sum(c['usage'].get(k, 0) for c in returned) for k in ['input_tokens','cache_write_tokens','cache_read_tokens','output_tokens']},
        'validation_passed': True,
    }
    (evidence / 'summary.json').write_text(json.dumps(summary, indent=2))
    storyboard = json.loads((job / 'storyboard.json').read_text())
    short = dict(id=name, paperId='2610.20674', creator=f'you_{provider}_v2', title=storyboard['hook_title'],
                 style='GPT-5.4 · Edited v2' if provider == 'openai' else 'Claude Opus 5.5 · Reference v2',
                 kicker='FLOW MAP · API V2', accent='#f4cb56' if provider == 'openai' else '#6bdcc4',
                 duration=duration, videoUrl=f'videos/{name}.mp4', thumbnailUrl=f'thumbnails/{name}.jpg', demo=False)
    manifest = ROOT / 'src/data/shorts.json'
    shorts = json.loads(manifest.read_text())
    shorts = [s for s in shorts if s['id'] != name]
    shorts.append(short)
    manifest.write_text(json.dumps(shorts, ensure_ascii=False, indent=2) + '\n')
    print(provider, json.dumps(summary))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', choices=['openai', 'anthropic'], required=True)
    export(parser.parse_args().provider)
