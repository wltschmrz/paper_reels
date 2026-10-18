from render_kit import *
from _shared import *
import numpy as np
import math


class S7(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()

        def y_of(v, y0, height, ymax):
            return y0 + height * (v / ymax)

        ps_num = [0.00, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50]
        ps_lab = ["0", "0.25", "0.5", "0.75", "1", "1.25", "1.5"]
        fid = [10.62, 6.81, 5.51, 5.46, 5.61, 5.93, 6.32]
        ymax = 12

        title = fitw(
            T("CIFAR-10 · NFE 1 · FID\nMeanFlow loss · mean of 3 runs · 200K steps", 13.5, FG, MEDIUM),
            4.0,
        ).move_to([0, 2.08, 0])

        cols = [RED, RED, TEAL, YEL, TEAL, TEAL, TEAL]
        ch = BarChart(fid, ps_lab, cols, ymax=ymax)
        axis_tag = M("p", size=22, color=GRAY).move_to([ch.x(0) - 0.48, ch.y0 - 0.17, 0])

        p_tracker = ValueTracker(0.00)

        def interp_xy(p):
            if p <= ps_num[0]:
                i, a = 0, 0.0
            elif p >= ps_num[-1]:
                i, a = len(ps_num) - 2, 1.0
            else:
                i = 0
                while not (ps_num[i] <= p <= ps_num[i + 1]):
                    i += 1
                a = (p - ps_num[i]) / (ps_num[i + 1] - ps_num[i])
            x0, x1 = ch.x(i), ch.x(i + 1)
            y0 = y_of(fid[i], ch.y0, ch.height, ymax)
            y1 = y_of(fid[i + 1], ch.y0, ch.height, ymax)
            return (1 - a) * x0 + a * x1, (1 - a) * y0 + a * y1

        sweep_line = always_redraw(
            lambda: Line(
                [interp_xy(p_tracker.get_value())[0], ch.y0 - 0.02, 0],
                [interp_xy(p_tracker.get_value())[0], interp_xy(p_tracker.get_value())[1] + 0.18, 0],
                color=YEL,
                stroke_width=3,
            ).set_stroke(opacity=0.95)
        )
        sweep_dot = always_redraw(
            lambda: Dot(
                [interp_xy(p_tracker.get_value())[0], interp_xy(p_tracker.get_value())[1], 0],
                radius=0.06,
                color=YEL,
            )
        )
        p_read = always_redraw(
            lambda: VGroup(
                M("p", size=22, color=YEL),
                T(f"= {p_tracker.get_value():.2f}", 13.5, YEL, MEDIUM),
            ).arrange(RIGHT, buff=0.08).move_to([0, 1.68, 0])
        )

        sweet = T("sweet spot", 12.5, YEL, MEDIUM).move_to([1.0, 1.9, 0])

        cond0 = fitw(
            T("CIFAR-10, FID 10.62 at p = 0.00 · NFE 1", 11.5, FG, MEDIUM),
            3.55,
        ).move_to([0.72, 1.32, 0])

        cond1 = fitw(
            T("CIFAR-10, FID 5.46 at p = 0.75 · NFE 1", 11.5, YEL, MEDIUM),
            3.55,
        ).move_to([0.72, 1.32, 0])

        cond2 = fitw(
            T("CIFAR-10, FID 6.32 at p = 1.50 · NFE 1", 11.5, RED, MEDIUM),
            3.55,
        ).move_to([0.72, 1.32, 0])

        halo = SurroundingRectangle(ch.bars[3], color=YEL, buff=0.05, corner_radius=0.04)
        halo.set_stroke(width=2.5)

        self.say("s7a")
        self.play(
            FadeIn(h),
            FadeIn(title),
            Create(ch.base),
            FadeIn(ch.labels),
            FadeIn(axis_tag),
            run_time=0.45,
        )
        self.play(
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in ch.bars], lag_ratio=0.08),
            FadeIn(ch.vals),
            FadeIn(sweep_line),
            FadeIn(sweep_dot),
            FadeIn(p_read),
            run_time=0.45,
        )
        self.play(
            p_tracker.animate.set_value(0.75),
            FadeIn(sweet),
            Create(halo),
            ch.vals[3].animate.set_color(YEL).scale(1.12),
            run_time=0.3,
        )

        self.say("s7b")
        self.play(
            p_tracker.animate.set_value(0.00),
            Indicate(ch.bars[0], color=RED, scale_factor=1.04),
            run_time=0.9,
        )
        self.play(
            ch.vals[0].animate.set_color(RED).scale(1.14),
            run_time=0.55,
        )
        self.play(FadeIn(cond0), run_time=0.45)

        self.say("s7c")
        self.play(
            p_tracker.animate.set_value(0.75),
            FadeOut(cond0),
            run_time=0.9,
        )
        self.play(
            Indicate(ch.bars[3], color=YEL, scale_factor=1.05),
            ch.vals[3].animate.set_color(YEL).scale(1.06),
            run_time=0.55,
        )
        self.play(FadeIn(cond1), run_time=0.45)
        self.play(Indicate(sweet, color=YEL, scale_factor=1.08), run_time=0.35)

        self.say("s7d")
        self.play(
            p_tracker.animate.set_value(1.50),
            FadeOut(cond1),
            run_time=0.9,
        )
        self.play(
            Indicate(ch.bars[6], color=RED, scale_factor=1.04),
            ch.vals[6].animate.set_color(RED).scale(1.14),
            run_time=0.5,
        )
        self.play(FadeIn(cond2), run_time=0.45)
        self.play(Indicate(ch.vals[6], color=RED, scale_factor=1.08), run_time=0.3)

        self.finish()