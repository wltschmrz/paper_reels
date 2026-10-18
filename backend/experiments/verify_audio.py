"""Local speech recognition check; never invokes paid APIs."""
import difflib,json,time
from pathlib import Path
import soundfile as sf
from app.settings import DATA
from pipeline.providers.asr_sensevoice import SenseVoiceASR
from pipeline.stages.narration import norm

def verify(job):
    t=time.monotonic();film=json.loads((job/'film.json').read_text());asr=SenseVoiceASR();results=[]
    for i,s in enumerate(film['scenes']):
        x,sr=sf.read(job/f'voice-{i}.wav');hyp=asr.transcribe(x,sr,'ko')
        score=difflib.SequenceMatcher(None,norm(hyp,'ko'),norm(s['narration'],'ko')).ratio()
        results.append({'scene':i+1,'expected':s['narration'],'recognized':hyp,'similarity':round(score,3)})
    out={'passed':all(r['similarity']>=.85 for r in results),'threshold':.85,'seconds':round(time.monotonic()-t,2),'lines':results}
    (job/'speech-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(job.name,out['passed'],[x['similarity'] for x in results],flush=True)
if __name__=='__main__':
    import sys
    verify(DATA/'experiments'/f'drifting-{sys.argv[1]}-baseline-v1')
