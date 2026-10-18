from render_kit import *
from _shared import *
import numpy as np


class S6(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        h = VGroup(fitw(T('정규화로 큰 업데이트 억제', 18, FG), 4.1).move_to([0,3.1,0]), T('Theorem 4 · Appendix B.5', 13, GRAY).move_to([0,2.78,0]))

        c = 1.0
        p = ValueTracker(0.0)

        eq = M(
            r"u_{k+1}",
            r"=",
            r"u_k",
            r"-",
            r"\eta\rho\,",
            r"{r_k \over (\|r_k\|^2+c)^p}",
            size=26,
            color=FG,
        )
        eq[5].set_color(YEL)
        fitw(eq, 3.8).move_to([0, 1.9, 0])

        rdef = T("정규화: 잔차를 (‖r‖² + c)^p 로 나눔", 12.5, GRAY).move_to([0, 1.5, 0])
        fitw(rdef, 4.0)

        ax = Axes(
            x_range=[0, 4, 1],
            y_range=[0, 1.8, 0.5],
            x_length=3.05,
            y_length=1.75,
            tips=False,
            axis_config={"color": MGRAY, "stroke_width": 2, "include_ticks": False},
        ).move_to([-0.1, 0.15, 0])

        xl = T("잔차 크기  ‖r‖", 12, GRAY).next_to(ax.x_axis.get_end(), DOWN, buff=0.1).align_to(
            ax.x_axis.get_end(), RIGHT
        )
        yl = T("업데이트 크기", 12, GRAY).rotate(PI / 2).move_to([-1.95, 0.1, 0])

        def step_mag(r, pv):
            return r / ((r * r + c) ** pv)

        def make_curve():
            pv = p.get_value()
            rs = np.linspace(0, 4, 320)
            ys = np.array([step_mag(r, pv) for r in rs])
            col = RED if pv < 0.5 - 1e-6 else TEAL
            pts = [ax.c2p(r, min(y, 1.8)) for r, y in zip(rs, ys)]
            return VMobject(stroke_color=col, stroke_width=3.6).set_points_smoothly(pts)

        curve = always_redraw(make_curve)

        sample_rs = [0.55, 1.15, 2.05, 3.15]

        def make_arrows():
            pv = p.get_value()
            grp = VGroup()
            for r in sample_rs:
                y = min(step_mag(r, pv), 1.72)
                col = RED if r >= 2.0 else DGRAY
                arr = Arrow(
                    ax.c2p(r, 0),
                    ax.c2p(r, y),
                    buff=0,
                    stroke_width=4.2,
                    max_tip_length_to_length_ratio=0.18,
                    color=col,
                )
                grp.add(arr)
            return grp

        arrows = always_redraw(make_arrows)

        pd = DecimalNumber(0, num_decimal_places=2, font_size=24, color=FG)
        pd.add_updater(lambda m: m.set_value(p.get_value()))
        pl = VGroup(M("p =", size=24, color=FG), pd).arrange(RIGHT, buff=0.07).move_to([-1.45, 1.03, 0])

        bound_line = DashedLine(
            ax.c2p(0, 1.0), ax.c2p(2.3, 1.0), color=TEAL, stroke_width=1.8, dash_length=0.07
        )
        bound_label = T("p = 0.5 경계", 12.5, TEAL, weight=BOLD).move_to([-0.65, 0.52, 0])

        p1_tag = VGroup(
            T("p = 1", 14, YEL, weight=BOLD),
            T("해 근방 수렴", 12.5, FG),
            M(r"O(\eta^{1/2})", size=20, color=YEL),
        ).arrange(DOWN, buff=0.05, aligned_edge=LEFT).move_to([1.43, 0.08, 0])

        img_note = T("ImageNet 256×256 · from scratch\np = 1.0 최적", 14.5, FG).move_to([0, -1.42, 0])
        fitw(img_note, 4.08)

        foot = T("Theorem 4 가정 · c = 1 개형", 13, GRAY).move_to([0, -1.88, 0])

        self.say("s6a")
        self.play(
            FadeIn(h),
            FadeIn(eq, shift=UP * 0.05),
            FadeIn(rdef, shift=UP * 0.04),
            Create(ax),
            FadeIn(xl),
            FadeIn(yl),
            run_time=0.72,
        )
        self.play(
            Create(curve),
            FadeIn(arrows),
            FadeIn(pl),
            FadeIn(foot),
            run_time=0.78,
        )

        self.say("s6b")
        self.play(
            p.animate.set_value(0.5),
            run_time=1.95,
            rate_func=smooth,
        )
        self.play(
            FadeIn(bound_line),
            FadeIn(bound_label, shift=UP * 0.04),
            run_time=0.42,
        )

        self.say("s6c")
        self.play(
            p.animate.set_value(1.0),
            run_time=1.3,
            rate_func=smooth,
        )
        self.play(
            FadeIn(p1_tag, shift=LEFT * 0.04),
            run_time=0.42,
        )

        self.say("s6d")
        self.play(
            Indicate(p1_tag[0], color=YEL, scale_factor=1.1),
            p.animate.set_value(1.0),
            run_time=0.68,
        )
        self.play(
            FadeIn(img_note, shift=UP * 0.04),
            run_time=0.45,
        )

        self.finish()