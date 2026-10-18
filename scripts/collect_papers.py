"""Curated arXiv metadata + actual PDF first pages. Run with requirements-data.txt.
Caches downloads; a failed fetch never substitutes invented metadata.
"""
import json, re, time, urllib.request, datetime
from pathlib import Path
from bs4 import BeautifulSoup
import pymupdf as fitz
ROOT = Path(__file__).resolve().parents[1]
SELECTION = [
('2610.20674','Flow Map Theory'),
('2505.13447','MeanFlow'), ('2512.02012','MeanFlow'), ('2602.04770','Drifting'),
('2511.23342','MeanFlow'), ('2508.07102','MeanFlow'), ('2607.27431','MeanFlow'),
('2603.12366','Drifting'), ('2605.10727','Drifting'), ('2605.17244','Drifting'),
('2606.02521','Drifting'), ('2606.15553','Drifting'), ('2604.04528','Drifting'),
('2210.02747','Flow Matching'), ('2209.03003','Flow Matching'),
('2303.01469','Consistency'), ('2310.14189','Consistency'),
('2410.12557','One-step Generation'), ('2503.07565','One-step Generation'),
('2010.02502','Diffusion'), ('2006.11239','Diffusion')]
cache = ROOT / '.cache/papers'; cache.mkdir(parents=True, exist_ok=True)
(ROOT / 'public/previews').mkdir(parents=True, exist_ok=True)
def download(url, target):
    if target.exists(): return target.read_bytes()
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'ScholarShorts-Academic-Demo/0.1'})
            with urllib.request.urlopen(req, timeout=90) as response: data=response.read()
            target.write_bytes(data); time.sleep(3); return data
        except Exception:
            if attempt==2: raise
            time.sleep(5*(attempt+1))
results=[]; errors=[]
for paper_id,topic in SELECTION:
    try:
        soup=BeautifulSoup(download(f'https://arxiv.org/abs/{paper_id}',cache/f'{paper_id}.html'),'html.parser')
        def meta(name):
            tag=soup.find('meta',attrs={'name':name}); return tag.get('content','') if tag else ''
        title=meta('citation_title')
        abstract=soup.select_one('blockquote.abstract')
        if not title or not abstract: raise ValueError('Missing original metadata')
        abstract=re.sub(r'^\s*Abstract:\s*','',abstract.get_text(' ',strip=True))
        preview=f'previews/{paper_id}.webp'; preview_error=None
        try:
            pdf=download(f'https://arxiv.org/pdf/{paper_id}',cache/f'{paper_id}.pdf')
            with fitz.open(stream=pdf,filetype='pdf') as doc:
                page=doc[0]; pix=page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False)
                # PNG is supported without an extra imaging dependency.
                preview=f'previews/{paper_id}.png'; pix.save(str(ROOT/'public'/preview))
        except Exception as exc:
            preview=None; preview_error=str(exc)
        item={'id':paper_id,'title':title,'authors':[m['content'] for m in soup.find_all('meta',attrs={'name':'citation_author'})], 'abstract':abstract,'date':meta('citation_date').replace('/','-'),'topics':[topic], 'url':f'https://arxiv.org/abs/{paper_id}','pdfUrl':f'https://arxiv.org/pdf/{paper_id}','preview':preview,'source':'arXiv','fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'previewError':preview_error}
        results.append(item); print(f'{len(results):02d} {paper_id} {title} preview={bool(preview)}',flush=True)
    except Exception as exc:
        errors.append({'id':paper_id,'error':str(exc)}); print(f'ERROR {paper_id}: {exc}',flush=True)
(ROOT/'src/data/papers.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
(ROOT/'docs/collection-report.json').write_text(json.dumps({'count':len(results),'errors':errors},indent=2)+'\n')
if errors: raise SystemExit(1)
