from render_kit import *
from _shared import *


class S6(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        eA = M(r"u_{k+1}", "=", r"u_k", "-", r"\eta\rho\,", r"r_k", size=34).move_to([0, 2.12, 0])
        eB = M(r"u_{k+1}", "=", r"u_k", "-", r"\eta\rho\,", r"{r_k \over (\|r_k\|^2+c)^{p}}", size=30)
        fitw(eB, 3.9).move_to([0, 2.02, 0])
        eB[5].set_color(YEL)
        eB[5][0:2].set_color(FG)
        rdef = T("r = 모델 답 − 정답지 (잔차)", 11, GRAY).move_to([0, 1.5, 0])
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 2.5, 1], x_length=3.3, y_length=1.9, tips=False,
                  axis_config={"color": MGRAY, "stroke_width": 2, "include_ticks": False})
        ax.move_to([0.1, -0.12, 0])
        xl = T("잔차 크기", 11, GRAY).next_to(ax.x_axis.get_end(), DOWN, buff=0.1).align_to(ax.x_axis.get_end(), RIGHT)
        yl = T("한 걸음 크기", 11, GRAY).next_to(ax.y_axis.get_end(), RIGHT, buff=0.1).shift(DOWN * 0.02)
        c = 0.25
        p = ValueTracker(0.0)

        def fp(r, pv):
            return r / (r * r + c) ** pv

        def build():
            pv = p.get_value()
            rs = np.linspace(0, 4, 300)
            ys = fp(rs, pv)
            keep = ys <= 2.5
            if not keep.all():
                i = int(np.argmax(~keep))
                rs, ys = rs[:i + 1], np.minimum(ys[:i + 1], 2.5)
            col = RED if pv < 0.5 - 1e-6 else TEAL
            return VMobject(stroke_color=col, stroke_width=3.4).set_points_smoothly([ax.c2p(r, y) for r, y in zip(rs, ys)])

        cv = always_redraw(build)
        pd = DecimalNumber(0, num_decimal_places=2, font_size=26, color=FG)
        pd.add_updater(lambda m: m.set_value(p.get_value()))
        pl = VGroup(M("p =", size=26), pd).arrange(RIGHT, buff=0.08).move_to([0.05, 1.12, 0])
        bad = T("상한 없음 ✗", 13, RED).next_to(pl, RIGHT, buff=0.25)
        good = T("상한 있음 ✓", 13, TEAL).move_to(bad).align_to(bad, LEFT)
        cap0 = T("보통 경사하강: 잔차에 비례 → 끝없이 커질 수 있음", 11.5, RED).move_to([0, -1.42, 0])
        fitw(cap0, 4.1)

        self.say("s6a")
        self.play(FadeIn(h), FadeIn(eA), FadeIn(rdef), Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.5)
        self.play(Create(cv), FadeIn(pl), FadeIn(bad), FadeIn(cap0), run_time=0.8)

        self.say("s6b")
        self.play(TransformMatchingTex(eA, eB), FadeOut(cap0), run_time=0.7)
        self.play(Indicate(eB[5][2:], color=YEL, scale_factor=1.15), run_time=0.7)

        self.say("s6c")
        ub = DashedLine(ax.c2p(0, 1), ax.c2p(4, 1), color=TEAL, stroke_width=1.6, dash_length=0.06).set_opacity(0.7)
        ul = T("상한", 10.5, TEAL).next_to(ub, RIGHT, buff=0.05).shift(UP * 0.1)
        self.play(p.animate.set_value(0.5), run_time=2.0, rate_func=smooth)
        self.play(FadeIn(ub), FadeIn(ul), FadeOut(bad), FadeIn(good, scale=1.3), run_time=0.45)

        self.say("s6d")
        c1 = T("p = 1: 정답 근처로 수렴 보장 (Theorem 4)", 13, YEL).move_to([0, -1.42, 0])
        c2 = T("MeanFlow 원 논문도 ImageNet 처음부터 학습에서 p = 1이 최적", 10, GRAY).move_to([0, -1.7, 0])
        fitw(c1, 4.1)
        fitw(c2, 4.1)
        self.play(p.animate.set_value(1.0), run_time=1.2, rate_func=smooth)
        self.play(FadeIn(c1, shift=UP * 0.1), FadeIn(c2), run_time=0.5)
        self.finish()
