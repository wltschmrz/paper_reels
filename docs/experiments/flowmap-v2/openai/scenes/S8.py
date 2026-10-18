from render_kit import *
from _shared import *

class S8(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        h = VGroup(T("이론의 결론과 적용 범위",18,FG).move_to([0,3.1,0]), T("Theorem 1, 4 · Proposition 1",13,GRAY).move_to([0,2.78,0]))
        def row(title, body, source, color, y):
            box = RoundedRectangle(width=3.95,height=1.02,corner_radius=0.1,stroke_color=color,stroke_width=2)
            box.set_fill(self.C["BG"], opacity=1)
            texts = VGroup(T(title,18,color,MEDIUM), T(body,16,FG), T(source,13,GRAY)).arrange(DOWN,buff=0.08)
            fitw(texts,3.7)
            return VGroup(box,texts).move_to([0,y,0])
        c1 = row("연속 학습은 수렴", "참 flow map에 점별 수렴", "Theorem 1 · functional gradient flow", TEAL,1.65)
        c2 = row("유한한 보폭은 발산 가능", "작은 초기 오차도 발산하는 반례", "Proposition 1 · MeanFlow/Lagrangian, v=0", RED,0.46)
        c3 = row("정규화로 업데이트 억제", "p ≥ 0.5: 업데이트 크기 유계", "Theorem 4의 가정 아래", YEL,-0.73)
        cards = VGroup(c1,c2,c3)
        c2.set_opacity(0.25);c3.set_opacity(0.25)
        limitation = VGroup(T("한계: 이상화된 함수 공간의 이론",13,GRAY),T("신경망 매개변수화·확률적 학습은 제외",13,GRAY)).arrange(DOWN,buff=0.08).move_to([0,-1.65,0])
        self.say("s8a")
        self.play(FadeIn(h),FadeIn(cards),run_time=0.8)
        self.play(Indicate(c1[0],color=TEAL,scale_factor=1.02),run_time=0.8)
        self.say("s8b")
        self.play(c1.animate.set_opacity(0.25),c2.animate.set_opacity(1),run_time=0.7)
        self.play(Indicate(c2[0],color=RED,scale_factor=1.02),run_time=0.7)
        self.say("s8c")
        self.play(c2.animate.set_opacity(0.25),c3.animate.set_opacity(1),run_time=0.7)
        self.play(Indicate(c3[0],color=YEL,scale_factor=1.02),run_time=0.7)
        self.say("s8d")
        self.play(c1.animate.set_opacity(0.7),c2.animate.set_opacity(0.7),FadeIn(limitation),run_time=0.8)
        self.play(Indicate(limitation,color=FG,scale_factor=1.02),run_time=0.7)
        self.finish()
