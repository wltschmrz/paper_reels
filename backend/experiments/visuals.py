"""Trusted renderer: bounded text and six hardcoded diagrams. Never eval/exec/model code."""
import json, math, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
W,H,FPS=540,960,24
CYAN='#64dfdf'; GOLD='#ffe175'; MUTED='#8190aa'; WHITE='#edf1ff'
def font(n): return ImageFont.truetype(FONT,n,index=1)
def wrap(text,n):
    lines=[];line=''
    for c in text:
        if font(n).getlength(line+c)>450: lines.append(line);line=''
        line+=c
    if line:lines.append(line)
    return lines

def render(job,film,provider):
    durations=json.loads((job/'audio.json').read_text())['durations']
    rng=np.random.default_rng(42)
    initial=rng.normal(size=(36,2))*[85,90]+[270,475]
    ang=np.linspace(0,2*np.pi,36,endpoint=False)
    target=np.array([270+125*np.cos(ang),475+125*np.sin(ang)]).T
    bases=[]
    for i,s in enumerate(film['scenes']):
        im=Image.new('RGB',(W,H),'#0b101d');d=ImageDraw.Draw(im)
        d.text((34,35),'SCHOLARSHORTS   /   DRIFTING',font=font(15),fill=MUTED)
        d.text((34,78),f'0{i+1}  /  '+s['section'].upper(),font=font(15),fill=CYAN)
        for k,line in enumerate(wrap(s['heading'],32)):d.text((32,120+k*44),line,font=font(32),fill=WHITE)
        d.rounded_rectangle((24,252,516,682),radius=18,fill='#101a2b',outline='#24324b')
        d.text((42,268),'QUALITATIVE FEATURE-SPACE ILLUSTRATION',font=font(11),fill=MUTED)
        if s['visual'] not in ['one_step','limits']:
            d.ellipse((43,309,52,318),fill=CYAN);d.text((60,300),'실제 데이터',font=font(15),fill=CYAN)
            d.ellipse((182,309,191,318),fill=GOLD);d.text((199,300),'생성 샘플',font=font(15),fill=GOLD)
            for x in range(70,500,40):d.line((x,350,x,640),fill='#1b2940')
            for y in range(355,650,40):d.line((44,y,496,y),fill='#1b2940')
        d.text((36,703),{'noise':'TRAINING / 분포에서 시작하기','attract':'TRAINING / 실제 데이터 쪽으로','repel':'TRAINING / 생성 샘플끼리 퍼지기','balance':'TRAINING / 분포가 가까워질 때','one_step':'INFERENCE / 학습 이후','limits':'TAKEAWAY / 무엇을 기억할까'}[s['visual']],font=font(15),fill=CYAN)
        d.text((34,891),f'arXiv:2602.04770 · p.{s["page"]}   |   {provider.upper()}',font=font(12),fill=MUTED)
        d.text((34,917),'AI 설명 · 개념도는 논문 실험 결과가 아닙니다',font=font(12),fill=MUTED)
        bases.append(im)
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','540x960','-framerate',str(FPS),'-i','-', '-i',str(job/'voice.wav'),'-vf','scale=1080:1920','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart',str(job/'short.tmp.mp4')]
    with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
        for i,(s,duration) in enumerate(zip(film['scenes'],durations)):
            lines=wrap(s['narration'],22);chunks=[lines[k:k+3] for k in range(0,len(lines),3)]
            frames=math.ceil(duration*FPS)
            for frame in range(frames):
                t=frame/max(frames-1,1);ease=(1-math.cos(math.pi*t))/2
                im=bases[i].copy();d=ImageDraw.Draw(im)
                kind=s['visual']
                if kind not in ['one_step','limits']:
                    for x,y in target:d.ellipse((x-3,y-3,x+3,y+3),fill=CYAN)
                    if kind=='noise': pos=initial+np.sin(t*math.pi*2)*3
                    elif kind=='attract':pos=initial*(1-ease*.75)+target*ease*.75
                    elif kind=='repel':
                        collapsed=np.array([270+50*np.cos(ang),475+50*np.sin(ang)]).T
                        pos=collapsed*(1-ease)+target*ease
                    else:pos=target+np.c_[np.cos(ang+t*3),np.sin(ang+t*3)]*(10*(1-ease))
                    for j,(x,y) in enumerate(pos):
                        x=float(np.clip(x,55,485));y=float(np.clip(y,350,630))
                        if kind=='attract' and j%4==0:
                            tx,ty=target[j];d.line((x,y,tx,ty),fill='#756944',width=1)
                        d.ellipse((x-4,y-4,x+4,y+4),fill=GOLD)
                    label={'noise':'생성 분포 ≠ 데이터 분포','attract':'끌어당김 +','repel':'밀어냄 −','balance':'분포 일치 → 드리프트 소멸'}[kind]
                    d.text((65,645),label,font=font(17),fill=WHITE)
                elif kind=='one_step':
                    for k,(yy,label,color) in enumerate([(355,'잡음  z',MUTED),(455,'학습된 생성기  fθ',CYAN),(565,'샘플  x',GOLD)]):
                        d.rounded_rectangle((100,yy,440,yy+60),radius=12,outline=color,width=2)
                        d.text((125,yy+14),label,font=font(22),fill=color)
                    for yy in [420,525]:d.line((270,yy,270,yy+25),fill=WHITE,width=3);d.polygon([(263,yy+19),(277,yy+19),(270,yy+29)],fill=WHITE)
                    yy=335+300*t;d.ellipse((77,yy,87,yy+10),fill=GOLD)
                else:
                    for k,(a,b) in enumerate([('01','학습과 추론을 구분하기'),('02','분포의 힘으로 학습하기'),('03','근거와 한계는 원문에서')]):
                        y=365+k*92;d.text((57,y),a,font=font(28),fill=GOLD);d.text((115,y+7),b,font=font(20),fill=WHITE)
                chunk=chunks[min(len(chunks)-1,int(t*len(chunks)))]
                for k,line in enumerate(chunk): d.text((34,750+k*35),line,font=font(22),fill=WHITE)
                d.rectangle((0,953,int(W*(i+t)/6),960),fill=CYAN)
                if i==1 and frame==frames//2:im.resize((1080,1920)).save(job/'thumbnail.jpg',quality=92)
                proc.stdin.write(im.tobytes())
        proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('FFmpeg failed')

    (job/'short.tmp.mp4').replace(job/'short.mp4')
