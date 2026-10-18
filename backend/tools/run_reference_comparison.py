"""One paid reference-v2 run per provider; actual generated Manim via Desktop bridge."""
import argparse,json,os,shutil,time
from pathlib import Path
from app.settings import DATA,ROOT,keys
from pipeline import runner
from pipeline.contracts import Preset,JobState
from pipeline.budget import BudgetLLM

PRICES={'openai':{'gpt-5.4':{'input_per_mtok':2.5,'output_per_mtok':15,'cache_read_multiplier':.1}},
'anthropic':{'claude-opus-5-5':{'input_per_mtok':4,'output_per_mtok':20,'cache_read_multiplier':.05},
'claude-sonnet-5-5':{'input_per_mtok':2,'output_per_mtok':10,'cache_read_multiplier':.05}}}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--provider',choices=['openai','anthropic'],required=True);args=parser.parse_args()
    beat=DATA/'render-bridge/heartbeat'
    if not beat.exists() or time.time()-beat.stat().st_mtime>60:raise SystemExit('Windows renderer not connected; no paid call made')
    provider=args.provider;limit=3.5
    job=DATA/'jobs'/f'flowmap-v2-{provider}';job.mkdir(parents=True,exist_ok=True)
    prices=json.loads(runner.PRICING.read_text()) if runner.PRICING.exists() else {}
    for k,v in PRICES.items():prices.setdefault(k,{}).update(v)
    runner.PRICING.write_text(json.dumps(prices,indent=2))
    if not (job/'preset.json').exists():
        preset=Preset.model_validate_json((ROOT/'presets/reference_3b1b_ko.json').read_text())
        preset.creator_id='you';preset.preset_id=f'reference_v2_{provider}'
        preset.style.free_instruction='Use 6-8 scenes, at most 24 narration lines total. Aim for 430 Hangul/Latin letters TOTAL across every tts_text to fit 75 seconds. Keep visual descriptions under 120 Korean characters each. Complete all required sections with compact JSON.'
        for stage in ['understand','storyboard','visual_code','visual_qa','judge']:
            choice=getattr(preset.models,stage);choice.provider=provider
            choice.params={'reasoning_effort':'low'} if provider=='openai' else {}
            choice.model='gpt-5.4' if provider=='openai' else ('claude-sonnet-5-5' if stage in ['visual_qa','judge'] else 'claude-opus-5-5')
        (job/'preset.json').write_text(preset.model_dump_json(indent=2))
        (job/'job.json').write_text(JobState(job_id=job.name,paper_id='2610.20674',user_id='you',preset_id=preset.preset_id).model_dump_json(indent=2))
        shutil.copy2(ROOT/'golden/flowmap_2610.20674/facts.json',job/'facts.json')
        (job/'provenance.json').write_text(json.dumps({'facts':'Shared reference v2 facts from supplied ZIP; extraction is reused, not regenerated.','renderer':'generated Manim in isolated Windows Docker Desktop container','budget_usd':limit},indent=2))
    base=runner.Ctx
    class BudgetCtx(base):
        def llm(self, stage, choice):
            return BudgetLLM(super().llm(stage,choice),self.job,stage,choice,self.prices[choice.provider][choice.model],limit)
    runner.Ctx=BudgetCtx
    os.environ['SS_RENDER_MODE']='desktop_bridge'
    def progress(event):
        with (job/'events.jsonl').open('a') as f:f.write(json.dumps(dict(event,wall_time=time.time()))+'\n')
        print(json.dumps(event),flush=True)
    state=runner.run(job,keys(),progress)
    print(state.model_dump_json(indent=2),flush=True)
