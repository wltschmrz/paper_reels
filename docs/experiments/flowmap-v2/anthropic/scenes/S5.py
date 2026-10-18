from render_kit import *
from _shared import *


class S5(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()

        # Appendix B.4 counterexample (rho = 1): e_{k+1} = (1 - eta (m+1)) e_k
        ETA = 0.1
        M_SOFT, M_STEEP = 2, 24
        A = 0.1  # schematic epsilon for drawing
        fs = 1 - ETA * (M_SOFT + 1)   # 0.7
        ft = 1 - ETA * (M_STEEP + 1)  # -1.5
        CAP = 1.05  # clamp curves inside the plot box

        ax = Axes(x_range=[0, 1, 0.5], y_range=[-1.2, 1.2, 0.6], x_length=3.4, y_length=1.9, tips=False,
                  axis_config={"color": MGRAY, "stroke_width": 2, "include_ticks": False})
        ax.move_to([0.05, 0.6, 0])  # spans y in [-0.35, 1.55]
        xl = M("t-s", size=20, color=GRAY).next_to(ax.x_axis.get_end(), DOWN, buff=0.1).shift(LEFT * 0.15)
        yl = T("오차", 11, GRAY).next_to(ax.y_axis.get_end(), UP, buff=0.06)

        def curve(m, amp, col):
            return ax.plot(lambda r: float(np.clip(amp * r ** m, -CAP, CAP)), x_range=[0, 1, 0.004],
                           color=col, stroke_width=3.2, use_smoothing=False)

        cs = curve(M_SOFT, A, TEAL)
        ct = curve(M_STEEP, A, RED)

        # labels row above the plot, outside the curve region
        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.28, color=TEAL, stroke_width=3), T("완만한 오차  m = 2", 11, TEAL)).arrange(RIGHT, buff=0.08),
            VGroup(Line(ORIGIN, RIGHT * 0.28, color=RED, stroke_width=3), T("가파른 오차  m = 24", 11, RED)).arrange(RIGHT, buff=0.08),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        leg.move_to([-0.95, 2.12, 0])
        k = Integer(0, font_size=24, color=YEL)
        kl = VGroup(T("걸음 수", 11, GRAY), M("k =", size=24, color=YEL), k).arrange(RIGHT, buff=0.08).move_to([1.3, 2.26, 0])
        etal = VGroup(M(r"\eta = 0.1", size=20, color=YEL), T("예시", 11, GRAY)).arrange(RIGHT, buff=0.08).move_to([1.3, 1.95, 0])

        slot = -0.72
        e0 = M(r"e_0", "=", r"\varepsilon\,(t-s)^m", size=22).move_to([0, slot, 0])
        foot = T("부록 B.4 반례(ρ = 1, v = 0) · η = 0.1로 그린 개형", 9.5, GRAY).move_to([0, -1.62, 0])
        fitw(foot, 4.1)

        self.say("s5a")
        self.play(FadeIn(h), Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.5)
        self.play(Create(cs), Create(ct), FadeIn(leg), FadeIn(kl), run_time=0.9)
        self.play(FadeIn(etal, shift=DOWN * 0.1), FadeIn(e0), FadeIn(foot), run_time=0.5)

        self.say("s5b")
        f1 = M(r"(t-s)\,\partial_t\,(t-s)^m", "=", r"m", r"\,(t-s)^m", size=26).move_to([0, slot, 0])
        f1[2].set_color(YEL)
        cap = T("가파를수록(m이 클수록) m배로 커짐", 12, FG).move_to([0, slot - 0.46, 0])
        fitw(cap, 4.1)
        self.play(FadeOut(e0, shift=UP * 0.1), FadeIn(f1, shift=UP * 0.1), run_time=0.5)
        self.play(FadeIn(cap), Indicate(f1[2], color=YEL, scale_factor=1.5), run_time=0.8)

        self.say("s5c")
        f2 = M(r"e_{k+1}", "=", r"\big(1-\eta\,(m+1)\big)", r"\,e_k", size=26).move_to([0, slot, 0])
        f2[2].set_color(YEL)
        r1 = T("m = 2 → 매 걸음 × 0.7 → 사라짐", 11.5, TEAL)
        r2 = T("m = 24 → 매 걸음 × (−1.5) → 뒤집히며 커짐", 11.5, RED)
        rows = VGroup(r1, r2).arrange(DOWN, buff=0.06).move_to([0, slot - 0.48, 0])
        fitw(rows, 4.1)
        self.play(FadeOut(f1, shift=UP * 0.1), FadeOut(cap), FadeIn(f2, shift=UP * 0.1), FadeIn(rows), run_time=0.45)
        boom = T("발산", 20, RED, BOLD).move_to(ax.c2p(0.4, 0.6))
        for i in range(1, 9):
            ns = curve(M_SOFT, A * fs ** i, TEAL)
            nt = curve(M_STEEP, A * ft ** i, RED)
            anims = [Transform(cs, ns), Transform(ct, nt), k.animate.set_value(i)]
            if i == 8:
                anims.append(FadeIn(boom, scale=1.6))
            self.play(*anims, run_time=0.25)

        self.say("s5d")
        cond = VGroup(M(r"\eta\,(m+1) > 2", size=26, color=YEL), T("이면 발산", 14, FG)).arrange(RIGHT, buff=0.12).move_to([0, slot, 0])
        t1 = VGroup(M(r"\eta = 0.1", size=20), T("→ m ≥ 20인 오차가 터짐", 11.5, FG)).arrange(RIGHT, buff=0.1)
        t2 = VGroup(M(r"\eta = 0.01", size=20), T("→ m ≥ 200인 오차가 터짐", 11.5, FG)).arrange(RIGHT, buff=0.1)
        tb = VGroup(t1, t2).arrange(DOWN, buff=0.06, aligned_edge=LEFT).move_to([0, slot - 0.5, 0])
        fitw(tb, 4.1)
        self.play(FadeOut(f2, shift=UP * 0.1), FadeOut(rows), FadeIn(cond, shift=UP * 0.1), run_time=0.45)
        self.play(FadeIn(t1, shift=RIGHT * 0.1), run_time=0.6)
        self.play(FadeIn(t2, shift=RIGHT * 0.1), run_time=0.6)
        self.finish()
