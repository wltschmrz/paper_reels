"""Persistent per-job spend ceiling including uncertain requests; no silent paid retries."""
import json,time
from pathlib import Path
from filelock import FileLock

class BudgetLLM:
    def __init__(self, llm, job, stage, choice, price, limit):
        self.llm,self.path,self.stage,self.choice,self.p,self.limit=llm,Path(job)/'budget.json',stage,choice,price,limit
    def complete(self, system, user, images=None, max_tokens=8000):
        ip,op=self.p['input_per_mtok'],self.p['output_per_mtok']
        # UTF8 bytes bound text tokens; image bytes deliberately conservative.
        bound=len(system.encode())+len(user.encode())+4096+sum(len(i) for i in images or [])
        reserve=(bound*ip*1.25+max_tokens*op)/1e6
        with FileLock(str(self.path)+'.lock'):
            data=json.loads(self.path.read_text()) if self.path.exists() else {'limit_usd':self.limit,'calls':[]}
            spent=sum(c.get('actual_usd',c['reserved_usd']) for c in data['calls'])
            if spent+reserve>self.limit:raise RuntimeError(f'Cost ceiling ${self.limit:.2f}: request not sent')
            record={'stage':self.stage,'model':self.choice.model,'params':self.choice.params,'reserved_usd':reserve,'status':'uncertain'}
            data['calls'].append(record);self.path.write_text(json.dumps(data,indent=2));index=len(data['calls'])-1
        start=time.monotonic()
        text,usage=self.llm.complete(system,user,images=images,max_tokens=max_tokens)
        responses=self.path.parent/'responses'
        responses.mkdir(exist_ok=True)
        (responses/f'{index:03d}-{self.stage}.txt').write_text(text)
        actual=(usage.get('input_tokens',0)*ip+usage.get('cache_write_tokens',0)*ip*self.p.get('cache_write_multiplier',1.25)+usage.get('cache_read_tokens',0)*ip*self.p.get('cache_read_multiplier',.1)+usage.get('output_tokens',0)*op)/1e6
        with FileLock(str(self.path)+'.lock'):
            data=json.loads(self.path.read_text());data['calls'][index].update(status='returned',actual_usd=actual,usage=usage,seconds=round(time.monotonic()-start,2));self.path.write_text(json.dumps(data,indent=2))
        return text,usage
