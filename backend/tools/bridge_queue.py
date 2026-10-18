"""Trusted host queue inspection; no model-controlled command execution."""
import json,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'data/render-bridge'
ROOT.mkdir(parents=True,exist_ok=True)
(ROOT/'heartbeat').write_text(str(time.time()))
for p in sorted(ROOT.glob('*/request.json')):
    if (p.parent/'result.json').exists() or (p.parent/'claimed').exists() or (p.parent/'cancel').exists():continue
    d=json.loads(p.read_text())
    assert re.fullmatch(r'[a-f0-9]{32}',d['ticket']) and d['ticket']==p.parent.name
    assert re.fullmatch(r'S\d{1,2}',d['sid'])
    assert d['quality'] in ['preview','final']
    assert d['resolution'] in ['540,960','1080,1920']
    assert d['fps'] in ['15','30','24']
    (p.parent/'claimed').touch()
    print(json.dumps(d));break
