"""File queue for a Windows Docker Desktop host; never executes generated code here."""
import json, os, shutil, subprocess, time, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/'data/render-bridge'

def command(job, sid, args, timeout):
    job=Path(job).resolve()
    if not job.is_relative_to(ROOT/'data'):
        raise ValueError('Desktop bridge only accepts backend/data jobs')
    quality='preview' if '/preview/' in args[args.index('--media_dir')+1] else 'final'
    resolution=args[args.index('-r')+1];fps=args[args.index('--fps')+1]
    ticket=QUEUE/uuid.uuid4().hex; inputs=ticket/'input';inputs.mkdir(parents=True)
    for name in ['storyboard.json','narration.json','scenes','audio']:
        src=job/name
        if src.is_symlink() or (src.is_dir() and any(p.is_symlink() for p in src.rglob('*'))):
            raise ValueError('Symlinks forbidden in render input')
        if src.is_dir():shutil.copytree(src,inputs/name)
        else:shutil.copy2(src,inputs/name)
    shutil.copytree(ROOT/'pipeline/render_kit', inputs/'runtime/render_kit', ignore=shutil.ignore_patterns('__pycache__'))
    payload={'ticket':ticket.name,'sid':sid,'quality':quality,'resolution':resolution,'fps':fps,'timeout':timeout}
    (ticket/'request.tmp').write_text(json.dumps(payload));(ticket/'request.tmp').replace(ticket/'request.json')
    deadline=time.monotonic()+timeout+120
    while time.monotonic()<deadline:
        if (ticket/'result.json').exists():
            result=json.loads((ticket/'result.json').read_text(encoding='utf-8-sig'))
            if result['returncode']==0:
                out=ticket/'output'
                if any(p.is_symlink() for p in out.rglob('*')):raise ValueError('Symlink in output')
                shutil.copytree(out,job/'render',dirs_exist_ok=True)
            return subprocess.CompletedProcess(args,result['returncode'],'',result.get('stderr',''))
        if (job/'cancel.requested').exists():break
        time.sleep(2)
    (ticket/'cancel').touch()
    raise TimeoutError('Windows renderer did not return before deadline')
