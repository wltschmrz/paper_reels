from render_kit import *
from _shared import *


class S7(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()

        # Title with dataset, metric and condition
        title = fitw(T("CIFAR-10 · NFE 1 · FID (낮을수록 좋음)", 14, FG, MEDIUM)).move_to([0, 2.15, 0])

        # Table 1 values (fact params): MeanFlow loss, mean of 3 runs, 200K steps
        ps = ["0", "0.25", "0.5", "0.75", "1", "1.25", "1.5"]
        fid = [10.62, 6.81, 5.51, 5.46, 5.61, 5.93, 6.32]
        cols = [RED, GRAY, GRAY, TEAL, GRAY, GRAY, GRAY]
        ch = BarChart(fid, ps, cols, ymax=12)
        rl1 = M("p", size=22, color=GRAY).move_to([ch.x(0) - 0.5, ch.y0 - 0.17, 0])

        # Moving quantity: p. Bars appear from p = 0.00 to p = 1.50.
        pt = ValueTracker(0.0)
        plab = M("p =", size=24, color=YEL)
        pnum = DecimalNumber(0.0, num_decimal_places=2, font_size=24, color=YEL)
        pgrp = VGroup(plab, pnum).arrange(RIGHT, buff=0.1).move_to([1.35, 1.9, 0])
        pnum.add_updater(lambda m: m.set_value(pt.get_value()))

        foot = fitw(T("Table 1 · MeanFlow loss · 3회 평균 · 200K steps", 10, GRAY)).move_to([0, -1.62, 0])

        # s7a: dataset and metric; bars appear for p = 0.00 -> 1.50
        self.say("s7a")
        self.play(FadeIn(h), FadeIn(title), Create(ch.base), FadeIn(ch.labels), FadeIn(rl1),
                  FadeIn(pgrp), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in ch.bars], lag_ratio=0.15),
                  pt.animate.set_value(1.5), run_time=1.6, rate_func=linear)
        self.play(FadeIn(ch.vals), FadeIn(foot), run_time=0.4)

        # s7b: p = 0 gives 10.62; p = 0.75 gives the lowest value, 5.46
        self.say("s7b")
        self.play(Indicate(ch.vals[0], color=RED, scale_factor=1.4),
                  pt.animate.set_value(0.0), run_time=0.7)
        self.play(ch.bars[3].animate.set_fill(YEL), ch.vals[3].animate.set_color(YEL).scale(1.25),
                  pt.animate.set_value(0.75), run_time=0.5)
        arr = CurvedArrow(ch.vals[0].get_right() + RIGHT * 0.05, ch.vals[3].get_top() + UP * 0.05,
                          angle=-0.9, color=YEL, stroke_width=3, tip_length=0.12)
        lab = T("10.62 → 5.46", 13, YEL, MEDIUM).move_to([0.25, 1.55, 0])
        self.play(Create(arr), FadeIn(lab), run_time=0.8)
        ymin = ch.bars[3].get_top()[1]
        best = DashedLine([ch.x(0) - 0.25, ymin, 0], [ch.x(6) + 0.25, ymin, 0],
                          color=YEL, stroke_width=2, dash_length=0.07)
        best.set_stroke(opacity=0.6)
        self.play(Create(best), run_time=0.8)

        # s7c: at p = 1.5 the value rises again to 6.32; good only in a range of p
        self.say("s7c")
        self.play(FadeOut(lab), FadeOut(arr), FadeOut(pgrp),
                  ch.bars[5].animate.set_fill(RED), ch.bars[6].animate.set_fill(RED),
                  run_time=0.5)
        br = Brace(VGroup(ch.bars[5], ch.bars[6], ch.vals[6]), UP, color=RED, buff=0.08)
        bl = T("다시 나빠짐", 12, RED).next_to(br, UP, buff=0.05)
        self.play(FadeIn(br), FadeIn(bl), Indicate(ch.vals[6], color=RED, scale_factor=1.3), run_time=0.5)
        self.play(ch.bars[2].animate.set_fill(TEAL), ch.bars[4].animate.set_fill(TEAL), run_time=0.6)
        self.finish()
