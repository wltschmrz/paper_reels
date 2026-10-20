"""Regenerate ONLY known unrendered demo covers; retain all real media and metadata.

Artwork is conceptual, not a reproduced paper figure or mathematical proof.
Hooks are grounded in the catalogue abstracts. Style names describe a perspective,
not a rigid headline template or an assertion that a video has been generated.
"""
import json
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
STYLES = json.loads((ROOT / 'src/data/explanationStyles.json').read_text())
# id: lens, paper-specific hook, editorial focus, conceptual artwork motif
DESIGNS = {
 'demo-01': ('intuition', '이미지 생성,\n딱 한 번이면\n된다고?', '순간 속도 대신 평균 속도로 보는 한 번의 생성', 'jump'),
 'demo-02': ('geometry', '굽은 여정,\n한 개의\n평균 벡터', '곡선 위 이동과 구간 전체의 변위를 비교', 'curve'),
 'demo-03': ('mathematics', '순간 속도와\n평균 속도를\n잇는 항등식', 'MeanFlow의 두 속도를 연결하는 학습 원리', 'identity'),
 'demo-04': ('mathematics', '학습 목표에\n모델 자신이\n들어 있다면', 'iMF가 순간 속도 회귀로 다시 쓰는 학습 목표', 'regression'),
 'demo-05': ('geometry', '한 번의 생성에도\n방향을 조절할\n여지는 있다', 'iMF의 유연한 guidance를 방향 변화로 설명', 'fan'),
 'demo-06': ('intuition', '추론은 한 번.\n움직임은 이미\n학습에서.', '추론의 반복 대신 학습 중 분포를 바꾸는 발상', 'training'),
 'demo-07': ('geometry', '점들이 움직이면\n분포의 모양이\n바뀝니다', 'Drifting field에 따른 표본과 분포의 변화', 'particles'),
 'demo-08': ('mathematics', '분포가 같아질 때\nDrifting field는\n멈춘다', 'Drifting의 분포 일치와 평형 조건을 구분해 읽기', 'equilibrium'),
 'demo-09': ('geometry', '한 번에 가려는데\n경로가 너무\n휘어 있다', 'Rectified MeanFlow의 경로 직선화와 곡률 병목', 'straighten'),
 'demo-10': ('mathematics', '평균 속도 다음은\n평균 가속도.\n성립 조건은?', 'Second-Order MeanFlow의 일반화된 일관성 조건', 'order'),
 'demo-11': ('mathematics', '멈췄다고\n같은 분포일까?\nSinkhorn의 답', 'Sinkhorn divergence가 보완하는 평형의 식별성', 'sinkhorn'),
 'demo-12': ('intuition', '노이즈에게\n길을 알려주면\n그림이 된다', 'Flow Matching을 길 안내에 비유해 이해하기', 'route'),
}


def artwork(style, motif, accent):
    # Reserve upper area for the hook and lower area for readable metadata.
    bg = {'intuition':'#291d36','geometry':'#071e29','mathematics':'#161328'}[style]
    base = f'<rect width="360" height="640" fill="{bg}"/>'
    if style != 'intuition':
        base += '<defs><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#ffffff" stroke-opacity=".07"/></pattern></defs><rect width="360" height="640" fill="url(#grid)"/>'
    body = ''
    if style == 'intuition':
        body += f'<circle cx="268" cy="345" r="67" fill="{accent}"/><circle cx="268" cy="345" r="80" stroke="{accent}" fill="none" opacity=".25"/>'
        for i in range(18):
            body += f'<circle cx="{32+(i*19)%70}" cy="{295+(i*29)%110}" r="{3+i%5}" fill="{accent}" opacity="{.3+i%5*.13}"/>'
        body += f'<path d="M112 346 C150 290 180 290 210 330 M198 307 L210 330 L184 331" stroke="{accent}" stroke-width="8" fill="none" stroke-linecap="round"/>'
        symbol = '1' if motif == 'jump' else ('✓' if motif == 'training' else '→')
        body += f'<text x="268" y="373" text-anchor="middle" fill="{bg}" font-family="sans-serif" font-size="85" font-weight="900">{symbol}</text>'
        labels = {'jump':('NOISE','ONE STEP'),'training':('TRAIN','GENERATE'),'route':('NOISE','DATA')}
        left,right=labels[motif]
        body += f'<text x="28" y="453" fill="#fff" font-family="sans-serif" font-size="14">{left}</text><text x="225" y="453" fill="{accent}" font-family="sans-serif" font-size="14">{right}</text>'
    elif style == 'geometry':
        body += '<path d="M28 458 H338 M48 470 V250" stroke="#ffffff" opacity=".25" fill="none"/>'
        if motif == 'particles':
            for i in range(22):
                x=32+(i*37)%120;y=280+(i*31)%160;tx=235+(i*17)%85;ty=290+(i*23)%120
                body += f'<circle cx="{x}" cy="{y}" r="3" fill="#fff" opacity=".6"/><path d="M{x} {y} Q180 230 {tx} {ty}" stroke="{accent}" opacity=".16" fill="none"/><circle cx="{tx}" cy="{ty}" r="4" fill="{accent}"/>'
        elif motif == 'fan':
            for i in range(5):
                end=260+i*27
                body += f'<path d="M55 430 Q140 {220+i*28} 310 {end} l-18 -4 m18 4 l-10 16" stroke="{accent}" stroke-width="{2+i%2}" opacity="{.35+i*.15}" fill="none"/>'
        else:
            body += f'<path d="M55 425 C30 190 300 490 310 280" stroke="{accent}" stroke-width="5" fill="none"/><path d="M55 425 L310 280 l-28 2 m28 -2 l-14 24" stroke="#ffe18a" stroke-width="4" fill="none"/>'
            if motif == 'straighten':body += '<path d="M55 425 Q150 280 310 280" stroke="#fff" stroke-width="2" stroke-dasharray="7 9" opacity=".5" fill="none"/>'
            body += f'<circle cx="55" cy="425" r="6" fill="{accent}"/><circle cx="310" cy="280" r="6" fill="#ffe18a"/>'
    else:
        text = {'identity':('v ↔ u','INSTANT / AVERAGE'), 'regression':('uθ → v','REWRITE THE TARGET'), 'equilibrium':('p = q ⇒ V = 0','EQUILIBRIUM'), 'order':('v → a','SECOND ORDER'), 'sinkhorn':('V = 0 ⇒ p = q','IDENTIFIABILITY')}[motif]
        body += f'<rect x="24" y="292" width="312" height="124" rx="10" fill="{accent}" fill-opacity=".08" stroke="{accent}" stroke-opacity=".6"/>'
        body += f'<text x="180" y="348" text-anchor="middle" fill="{accent}" font-family="Georgia,serif" font-size="{29 if len(text[0])>9 else 43}">{escape(text[0])}</text><text x="180" y="386" text-anchor="middle" fill="#fff" font-family="sans-serif" font-size="12" letter-spacing="1">{text[1]}</text>'
        body += f'<path d="M60 450 H130 M145 450 H215 M230 450 H300" stroke="{accent}" stroke-width="3"/><circle cx="135" cy="450" r="3" fill="#fff"/><circle cx="220" cy="450" r="3" fill="#fff"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640"><title>{style} — conceptual illustration</title>{base}{body}</svg>'


def main():
    manifest = ROOT / 'src/data/shorts.json'
    shorts = json.loads(manifest.read_text())
    for s in shorts:
        if s.get('videoUrl') or not s.get('demo') or s['id'] not in DESIGNS:
            continue
        style, hook, focus, motif = DESIGNS[s['id']]
        spec = STYLES[style]
        s.update(explanationStyle=style, style=spec['label'], hookLines=hook.split('\n'),
                 title=hook.replace('\n',' '), editorialFocus=focus,
                 kicker={'intuition':'THE BIG IDEA','geometry':'SEE IT MOVE','mathematics':'UNDER THE EQUATIONS'}[style],
                 accent=spec['accent'])
        s['thumbnailUrl'] = f"thumbnails/{s['id']}.svg"
        (ROOT/'public'/s['thumbnailUrl']).write_text(artwork(style,motif,spec['accent']))
    manifest.write_text(json.dumps(shorts,ensure_ascii=False,indent=2)+'\n')

if __name__ == '__main__':
    main()
