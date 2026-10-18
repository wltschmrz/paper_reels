import pytest
from pydantic import ValidationError
from experiments.drifting import Scene, call


def test_generated_code_is_not_a_visual():
    with pytest.raises(ValidationError):
        Scene(heading='hello', narration='x'*55, visual="__import__('os').system('id')", section='problem', page=1, quote='a source quote long enough')


def test_budget_stops_before_network(tmp_path):
    report={'calls':[{'estimated_usd':.99,'uncertain':False}]}
    with pytest.raises(RuntimeError, match='budget ceiling'):
        call('anthropic','system','prompt',report,tmp_path,'test')
    assert len(report['calls'])==1


def test_uncertain_charge_remains_reserved(tmp_path):
    report={'calls':[{'reserved_usd':.99,'uncertain':True}]}
    with pytest.raises(RuntimeError, match='budget ceiling'):
        call('openai','system','prompt',report,tmp_path,'test')


def test_reference_direction_and_examples_are_available():
    from pipeline.prompting import reference_direction, reference_scene
    from pipeline.contracts import Preset
    from pathlib import Path
    assert 'choreography' in reference_direction()
    assert 'class ' in reference_scene('flow_plot')
    preset=Preset.model_validate_json(Path('backend/presets/reference_quality_ko.json').read_text())
    assert preset.style.target_length_sec==60
    assert 'limitation' in preset.style.narrative.required_sections


def test_v2_prompt_preserves_cache_boundaries_during_repair():
    from pipeline.prompting import Prompt, Block
    from pipeline.providers.llm_anthropic import text_blocks
    p=Prompt([Block('fixed', True)],[Block('facts',True),Block('task',False)])
    system,user=p
    blocks=text_blocks(user+'repair')
    assert blocks[0]['cache_control']=={'type':'ephemeral'}
    assert 'cache_control' not in blocks[-1]
    assert blocks[-1]['text']=='repair'


def test_v2_golden_validates_motion_fields():
    from pipeline.contracts import Storyboard, Preset, FactSheet
    from pipeline.validators import validate_storyboard
    from pathlib import Path
    root=Path('backend/golden/flowmap_2610.20674')
    sb=Storyboard.model_validate_json((root/'storyboard.json').read_text())
    style=Preset.model_validate_json((root/'preset.json').read_text()).style
    facts=FactSheet.model_validate_json((root/'facts.json').read_text())
    assert all(c.passed for c in validate_storyboard(sb,style,facts))


def test_budget_keeps_uncertain_reservation(tmp_path):
    from pipeline.budget import BudgetLLM
    from pipeline.contracts import ModelChoice
    import json
    class Broken:
        def complete(self,*args,**kwargs):raise TimeoutError('network')
    choice=ModelChoice(provider='openai',model='test')
    llm=BudgetLLM(Broken(),tmp_path,'storyboard',choice,{'input_per_mtok':2.5,'output_per_mtok':15},1)
    with pytest.raises(TimeoutError):llm.complete('system','user')
    data=json.loads((tmp_path/'budget.json').read_text())
    assert data['calls'][0]['status']=='uncertain'
    assert data['calls'][0]['reserved_usd']>0


def test_bridge_copies_only_render_inputs(tmp_path,monkeypatch):
    import json
    from pipeline import desktop_bridge as bridge
    monkeypatch.setattr(bridge,'ROOT',tmp_path)
    monkeypatch.setattr(bridge,'QUEUE',tmp_path/'queue')
    (tmp_path/'pipeline/render_kit').mkdir(parents=True)
    job=tmp_path/'data/job';job.mkdir(parents=True)
    for name in ['storyboard.json','narration.json']:(job/name).write_text('{}')
    for name in ['scenes','audio']:(job/name).mkdir()
    (job/'.env').write_text('SECRET=never-copy')
    (job/'cancel.requested').touch()
    with pytest.raises(TimeoutError):
        bridge.command(job,'S1',['manim','--media_dir',str(job/'render/_media/preview/S1'),'-r','540,960','--fps','15'],0)
    inputs=next((tmp_path/'queue').glob('*/input'))
    assert not (inputs/'.env').exists()
    assert (inputs/'runtime/render_kit').is_dir()


def test_claude_stream_preserves_cache_usage(monkeypatch):
    from contextlib import contextmanager
    from types import SimpleNamespace
    from pipeline.providers import llm_anthropic
    from pipeline.prompting import Prompt, Block
    captured={}
    response=SimpleNamespace(content=[SimpleNamespace(type='text',text='{}')],
        stop_reason='end_turn',usage=SimpleNamespace(input_tokens=7,output_tokens=3,
        cache_creation_input_tokens=100,cache_read_input_tokens=200))
    class Fake:
        def __init__(self,**kwargs):self.messages=self
        @contextmanager
        def stream(self,**kwargs):
            captured.update(kwargs)
            yield SimpleNamespace(get_final_message=lambda:response)
    monkeypatch.setattr(llm_anthropic.anthropic,'Anthropic',Fake)
    system,user=Prompt([Block('fixed',True)],[Block('data',True),Block('task',False)])
    text,usage=llm_anthropic.AnthropicLLM('model','fake').complete(system,user,images=[b'png'])
    assert captured['system'][0]['cache_control']=={'type':'ephemeral'}
    assert [b['type'] for b in captured['messages'][0]['content']]==['text','image','text']
    assert usage['cache_write_tokens']==100 and usage['cache_read_tokens']==200
    assert usage['input_tokens']==7 and not usage['incomplete']


def test_resume_does_not_accept_failed_scene_code(tmp_path):
    from types import SimpleNamespace
    from pathlib import Path
    from pipeline.runner import done
    import shutil, json
    source = Path('backend/golden/flowmap_2610.20674')
    shutil.copy(source / 'storyboard.json', tmp_path / 'storyboard.json')
    shutil.copytree(source / 'scenes', tmp_path / 'scenes')
    ctx = SimpleNamespace(job=tmp_path)
    assert done(ctx, 'visual_code')
    scene_id = json.loads((tmp_path / 'storyboard.json').read_text())['scenes'][0]['scene_id']
    (tmp_path / 'scenes' / f'{scene_id}.py').write_text('import os\n')
    assert not done(ctx, 'visual_code')
