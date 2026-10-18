from render_kit import *
from _shared import *


class S7(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        title = fitw(T("CIFAR-10 · 한 번에 생성 · FID (낮을수록 좋음)", 14, FG, MEDIUM)).move_to([0, 2.15, 0])
        ps = ["0", "0.25", "0.5", "0.75", "1", "1.25", "1.5"]
        fid = [10.62, 6.81, 5.51, 5.46, 5.61, 5.93, 6.32]
        cols = [RED, RED, TEAL, TEAL, TEAL, TEAL, TEAL]
        ch = BarChart(fid, ps, cols, ymax=12)
        bnd = ch.row(["✗", "✗", "✓", "✓", "✓", "✓", "✓"], cols)
        rl1 = M("p", size=22, color=GRAY).move_to([ch.x(0) - 0.5, ch.y0 - 0.17, 0])
        rl2 = T("상한", 10.5, GRAY).move_to([ch.x(0) - 0.5, ch.y0 - 0.45, 0])

        self.say("s7a")
        self.play(FadeIn(h), FadeIn(title), Create(ch.base), FadeIn(ch.labels), FadeIn(rl1), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in ch.bars], lag_ratio=0.15), run_time=1.3)
        self.play(FadeIn(ch.vals), FadeIn(bnd), FadeIn(rl2), run_time=0.4)

        self.say("s7b")
        self.play(Indicate(ch.vals[0], color=YEL, scale_factor=1.4), run_time=0.7)
        self.play(ch.bars[3].animate.set_fill(YEL), ch.vals[3].animate.set_color(YEL).scale(1.25), run_time=0.5)
        arr = CurvedArrow(ch.vals[0].get_right() + RIGHT * 0.05, ch.vals[3].get_top() + UP * 0.05, angle=-0.9, color=YEL,
                          stroke_width=3, tip_length=0.12)
        lab = T("약 49% 감소", 14, YEL, MEDIUM).move_to([0.25, 1.55, 0])
        self.play(Create(arr), FadeIn(lab), run_time=0.8)

        self.say("s7c")
        br = Brace(VGroup(ch.bars[5], ch.bars[6], ch.vals[6]), UP, color=RED, buff=0.08)
        bl = T("다시 나빠짐", 12, RED).next_to(br, UP, buff=0.05)
        note = fitw(T("FFHQ 64×64에서도 p = 1.5는 FID 20.25 (최저는 p = 0.75의 8.67)", 10, GRAY)).move_to([0, -1.62, 0])
        self.play(FadeIn(br), FadeIn(bl), FadeOut(lab), run_time=0.5)
        self.play(FadeIn(note), run_time=0.4)
        self.finish()
