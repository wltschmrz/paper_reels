from render_kit import *
from _shared import *
import numpy as np
import math


class S5(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        h.scale(1.14)
        fitw(h, 4.1)

        def err_curve(ax, power, amp, color):
            return ax.plot(
                lambda x: float(np.clip(amp * (max(x, 0) ** power), -1.05, 1.05)),
                x_range=[0, 1, 0.004],
                color=color,
                stroke_width=3.4,
                use_smoothing=False,
            )

        ax = Axes(
            x_range=[0, 1, 0.5],
            y_range=[-1.1, 1.1, 0.55],
            x_length=3.0,
            y_length=1.95,
            tips=False,
            axis_config={"color": MGRAY, "stroke_width": 2, "include_ticks": False},
        ).move_to([0, 0.78, 0])

        xl = M("t-s", size=23, color=GRAY).next_to(ax.x_axis.get_end(), DOWN, buff=0.08).shift(LEFT * 0.08)
        yl = T("오차", 13, GRAY).next_to(ax.y_axis.get_end(), UP, buff=0.05)

        cs = err_curve(ax, 2, 0.72, TEAL)
        ct = err_curve(ax, 8, 0.72, RED)

        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.28, color=TEAL, stroke_width=3.2), T("완만한 오차", 12.8, TEAL)).arrange(RIGHT, buff=0.08),
            VGroup(Line(ORIGIN, RIGHT * 0.28, color=RED, stroke_width=3.2), T("가파른 오차", 12.8, RED)).arrange(RIGHT, buff=0.08),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT).move_to([-1.08, 1.94, 0])

        flow_lab = T("gradient flow: 수렴", 13, TEAL).move_to([1.0, 1.95, 0])
        gd_lab = T("gradient descent: 발산 가능", 13, RED).move_to([1.03, 1.66, 0])

        e0 = M(r"e_k", "=", r"\varepsilon\,(t-s)^m", size=28).move_to([0, -0.05, 0])
        e0[2].set_color(YEL)

        ek1 = M(r"e_{k+1}", "=", r"\big(1-\eta(m+1)\big)", r"e_k", size=26).move_to([0, -0.05, 0])
        ek1[2].set_color(YEL)

        cond = VGroup(
            M(r"\eta(m+1)>2", size=26, color=YEL),
            T("이면 발산", 13, FG),
        ).arrange(RIGHT, buff=0.12).move_to([0, -0.58, 0])

        ktr = ValueTracker(0)
        kn = DecimalNumber(0, num_decimal_places=0, font_size=26, color=FG)
        kn.add_updater(lambda m: m.set_value(ktr.get_value()))
        kl = VGroup(T("걸음 수", 12.8, GRAY), M("k=", size=24), kn).arrange(RIGHT, buff=0.07).move_to([1.26, 1.3, 0])

        foot = T("개형 예시 · 설정: MeanFlow, Lagrangian, v = 0", 10.2, GRAY).move_to([0, -1.62, 0])

        self.say("s5a")
        self.play(FadeIn(h), Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(foot), run_time=0.55)
        self.play(Create(cs), Create(ct), FadeIn(leg), run_time=0.75)

        self.say("s5b")
        self.play(FadeIn(flow_lab, shift=RIGHT * 0.08), FadeIn(gd_lab, shift=RIGHT * 0.08), run_time=0.65)
        self.play(Indicate(flow_lab, color=TEAL, scale_factor=1.05), run_time=0.55)
        self.play(
            ct.animate.set_stroke(width=4.8),
            Indicate(gd_lab, color=RED, scale_factor=1.06),
            run_time=0.75,
        )

        self.say("s5c")
        steeper = err_curve(ax, 20, 0.72, RED)
        cap = T("끝으로 갈수록 더 가파른 형태", 13, FG).move_to([0, -0.52, 0])
        self.play(FadeIn(e0, shift=UP * 0.08), run_time=0.5)
        self.play(Transform(ct, steeper), Indicate(e0[2], color=YEL, scale_factor=1.12), run_time=0.85)
        self.play(FadeIn(cap), run_time=0.55)

        self.say("s5d")
        self.play(
            FadeOut(flow_lab),
            FadeOut(gd_lab),
            FadeOut(cap),
            FadeOut(e0, shift=UP * 0.06),
            FadeIn(ek1, shift=UP * 0.06),
            FadeIn(kl),
            run_time=0.45,
        )

        stable_r = 0.72
        unstable_r = -1.18
        for i in range(1, 9):
            ns = err_curve(ax, 2, 0.72 * (stable_r ** i), TEAL)
            nt = err_curve(ax, 20, 0.72 * (unstable_r ** i), RED)
            anims = [Transform(cs, ns), Transform(ct, nt), ktr.animate.set_value(i)]
            if i == 8:
                anims.append(FadeIn(cond, shift=UP * 0.05))
            self.play(*anims, run_time=0.29)

        self.finish()