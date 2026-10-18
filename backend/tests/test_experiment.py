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
