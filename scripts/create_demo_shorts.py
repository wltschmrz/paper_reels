"""Editable vector art for fictional research reels. No real video or metric claims."""
import json, random, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
items=[
('2505.13447','이미지 생성,\n딱 한 번이면\n된다고?','ONE STEP?!','Visual intuition','mint_tensor_42'),
('2505.13447','이 곡선 하나로\nMeanFlow가\n이해됩니다','MATH, VISUALIZED','Mathematical','latent_fox_17'),
('2505.13447','한 번에 생성?\n그럼 뭘\n포기했을까','WAIT A SECOND','Critical Review','paper_otter_08'),
('2512.02012','MeanFlow는\n여기서 한 번 더\n바뀝니다','PLOT TWIST','Quick summary','gradient_moon_63'),
('2512.02012','가이던스가\n그림을 바꾸는\n진짜 이유','FOLLOW THE VECTOR','Mathematical','latent_fox_17'),
('2602.04770','추론 대신\n학습할 때\n움직인다면?','DRIFTING MODELS','Visual intuition','pixel_sparrow_29'),
('2602.04770','노이즈에서\n이미지까지,\n중간은 어디로?','SKIP THE STEPS?','Beginner-friendly','noisy_panda_51'),
('2602.04770','Drifting,\n좋은 결과만\n보면 놓치는 것','THE BIG QUESTION','Critical Review','paper_otter_08'),
('2511.23342','생성 경로를\n쭉 펴버리면\n어떻게 될까?','STRAIGHT TO IT','Visual intuition','vector_cactus_34'),
('2508.07102','평균 속도,\n그다음 차원은\n어떤 모습일까','BEYOND FIRST ORDER','Mathematical','matrix_moth_76'),
('2603.12366','점들을 옮겨서\n분포를 만든다?','CONNECT THE DOTS','Quick summary','gradient_moon_63'),
('2210.02747','노이즈가\n그림이 되는\n순간을 보세요','FLOW MATCHING','Beginner-friendly','pixel_sparrow_29')]
colors=[('#110f32','#c6ff00','#ff3c96'),('#080d18','#58c4dd','#ffff00'),('#251020','#ff4777','#ffcf40'),('#170b40','#b994ff','#ff71ca')]
shorts=[]
for i,(paper,title,kicker,style,creator) in enumerate(items):
 bg,ink,accent=colors[i%4]; math_style=style=='Mathematical'; name=f'demo-{i+1:02d}';rng=random.Random(i)
 if math_style: bg,ink,accent='#080d18','#58c4dd','#ffff00'
 defs=f'<defs><radialGradient id="glow"><stop stop-color="{ink}" stop-opacity=".3"/><stop offset="1" stop-color="{bg}" stop-opacity="0"/></radialGradient><pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M 30 0 H 0 V 30" stroke="#fff" stroke-opacity=".09" fill="none"/></pattern><filter id="bloom"><feGaussianBlur stdDeviation="4"/></filter></defs>'
 art=f'<rect width="360" height="640" fill="{bg}"/><ellipse cx="270" cy="300" rx="280" ry="300" fill="url(#glow)"/><rect width="360" height="640" fill="url(#grid)"/>'
 if math_style or i in [0,8,11]:
  art+='<path d="M 25 410 H 345 M 65 460 V 160" stroke="#fff" stroke-opacity=".4" stroke-width="1.5"/>'
  for k in range(7):
   d=f'M 15 {390-k*12} C 110 {130+k*22}, 220 {530-k*26}, 350 {210+k*17}'
   art+=f'<path d="{d}" fill="none" stroke="{ink if k!=3 else accent}" stroke-width="{2 if k!=3 else 5}" opacity="{.3+k*.08}"/>'
  art+=f'<circle cx="182" cy="309" r="8" fill="{accent}"/><path d="M 182 309 l 66 -48 l -8 25 M 248 261 l -27 0" stroke="{accent}" stroke-width="4" fill="none"/>'
  art+=f'<text x="120" y="220" font-family="Georgia,serif" font-style="italic" font-size="32" fill="{accent}">u = Δx / Δt</text>' if math_style else f'<text x="225" y="285" font-family="Arial,sans-serif" font-size="140" font-weight="900" fill="{ink}" transform="rotate(10 225 285)">1</text>'
 elif i in [5,6,10]:
  for k in range(70):
   x=rng.randint(20,340);y=rng.randint(200,440)
   art+=f'<circle cx="{x}" cy="{y}" r="{rng.randint(2,6)}" fill="{ink if x<180 else accent}" opacity=".8"/>'
  art+=f'<path d="M 80 300 Q 185 160 280 300 M 280 300 l -7 -36 M 280 300 l -35 -7" stroke="{accent}" stroke-width="9" fill="none"/>'
 else:
  art+=f'<circle cx="180" cy="320" r="107" fill="{accent}"/><circle cx="180" cy="320" r="123" fill="none" stroke="{accent}" stroke-width="2" stroke-dasharray="9 7"/><text x="180" y="377" text-anchor="middle" font-family="Arial,sans-serif" font-size="175" font-weight="900" fill="{bg}">?</text>'
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640">{defs}{art}</svg>'
 (ROOT/'public/thumbnails'/f'{name}.svg').write_text(svg)
 shorts.append(dict(id=name,paperId=paper,creator=creator,title=title.replace('\n',' '),hookLines=title.split('\n'),kicker=kicker,accent=accent if math_style else ink,style=style,duration=[60,75,45,60][i%4],videoUrl=None,thumbnailUrl=f'thumbnails/{name}.svg',demo=True))
manifest=ROOT/'src/data/shorts.json'
existing=json.loads(manifest.read_text()) if manifest.exists() else []
real=[s for s in existing if not s.get('demo')]
manifest.write_text(json.dumps(real+shorts,ensure_ascii=False,indent=2)+'\n')
