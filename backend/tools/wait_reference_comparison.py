"""Wait for the user-started bridge, smoke-test isolation plumbing, then run two jobs."""
import os,shutil,subprocess,time
from pathlib import Path
from app.settings import ROOT,DATA
from pipeline.stages.render import render_scene

beat=DATA/'render-bridge/heartbeat'
print('Waiting for Windows Docker Desktop bridge; no paid calls yet.',flush=True)
deadline=time.monotonic()+1800
while not (beat.exists() and time.time()-beat.stat().st_mtime<30):
    if time.monotonic()>deadline:raise SystemExit('Renderer not connected; no paid calls made')
    time.sleep(2)
print('Bridge heartbeat detected. Running keyless S1 smoke test.',flush=True)
job=DATA/'bridge-smoke'
if not job.exists():
    shutil.copytree(ROOT/'golden/flowmap_2610.20674',job)
    shutil.copytree(DATA/'golden-regression-01/audio',job/'audio')
    shutil.copy2(DATA/'golden-regression-01/narration.json',job/'narration.json')
os.environ['SS_RENDER_MODE']='desktop_bridge'
sid,path,error=render_scene(job,'S1','preview',timeout=300)
if error:raise SystemExit('Bridge smoke failed: '+error)
print('Bridge smoke passed; starting budgeted API runs.',flush=True)
for provider in ['openai','anthropic']:
    log=DATA/f'flowmap-v2-{provider}.log'
    print('Starting '+provider,flush=True)
    # Heartbeat is refreshed at the next host poll after the previous render returns.
    time.sleep(3)
    with log.open('a') as stream:
        result=subprocess.run([str(ROOT.parent/'.venv/bin/python'),str(ROOT/'tools/run_reference_comparison.py'),'--provider',provider],stdout=stream,stderr=subprocess.STDOUT)
    print(provider+' command exited '+str(result.returncode),flush=True)
