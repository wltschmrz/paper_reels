from render_kit import *
from _shared import *


class S5(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        ax = Axes(x_range=[0, 1, 0.5], y_range=[-1.2, 1.2, 0.6], x_length=3.4, y_length=2.2, tips=False,
                  axis_config={"color": MGRAY, "stroke_width": 2, "include_ticks": False})
        ax.move_to([0.05, 0.8, 0])
        xl = M("t-s", size=20, color=GRAY).next_to(ax.x_axis.get_end(), DOWN, buff=0.1).shift(LEFT * 0.15)
        yl = T("오차", 11, GRAY).next_to(ax.y_axis.get_end(), UP, buff=0.06)
        A = 0.1
        eta = 0.1
        fs, ft = 1 - eta * 3, 1 - eta * 25

        def curve(m, amp, col):
            return ax.plot(lambda r: float(np.clip(amp * r ** m, -1.2, 1.2)), x_range=[0, 1, 0.004], color=col, stroke_width=3.2,
                           use_smoothing=False)

        cs = curve(2, A, TEAL)
        ct = curve(24, A, RED)
        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.28, color=TEAL, stroke_width=3), T("완만한 오차  m = 2", 11, TEAL)).arrange(RIGHT, buff=0.08),
            VGroup(Line(ORIGIN, RIGHT * 0.28, color=RED, stroke_width=3), T("가파른 오차  m = 24", 11, RED)).arrange(RIGHT, buff=0.08),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT).move_to([-0.55, 2.24, 0])
        k = Integer(0, font_size=24, color=FG)
        kl = VGroup(T("걸음 수", 11, GRAY), M("k =", size=24), k).arrange(RIGHT, buff=0.08).move_to([1.32, 2.3, 0])
        e0 = M(r"e_0", "=", r"\varepsilon\,(t-s)^m", size=22).move_to([1.32, 1.95, 0])
        slot = -0.72

        self.say("s5a")
        self.play(FadeIn(h), Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.5)
        self.play(Create(cs), Create(ct), FadeIn(leg), FadeIn(kl), FadeIn(e0), run_time=0.9)

        self.say("s5b")
        f1 = M(r"(t-s)\,\partial_t\,(t-s)^m", "=", r"m", r"\,(t-s)^m", size=26).move_to([0, slot, 0])
        f1[2].set_color(YEL)
        cap = T("미분이 붙으면 가파를수록(m이 클수록) m배로 커짐", 12, FG).move_to([0, slot - 0.5, 0])
        fitw(cap, 4.1)
        self.play(FadeIn(f1, shift=UP * 0.1), run_time=0.5)
        self.play(FadeIn(cap), Indicate(f1[2], color=YEL, scale_factor=1.5), run_time=0.8)

        self.say("s5c")
        f2 = M(r"e_{k+1}", "=", r"\big(1-\eta\,(m+1)\big)", r"\,e_k", size=26).move_to([0, slot, 0])
        f2[2].set_color(YEL)
        mult = VGroup(T("× 0.7", 12, TEAL), T("× (−1.5)", 12, RED)).arrange(DOWN, buff=0.12).next_to(leg, RIGHT, buff=0.12)
        r1 = T("m = 2 → 매 걸음 × 0.7 → 사라짐", 12, TEAL)
        r2 = T("m = 24 → 매 걸음 × (−1.5) → 뒤집히며 커짐", 12, RED)
        rows = VGroup(r1, r2).arrange(DOWN, buff=0.08).move_to([0, slot - 0.55, 0])
        fitw(rows, 4.1)
        self.play(FadeOut(f1, shift=UP * 0.1), FadeOut(cap), FadeOut(e0), FadeIn(f2, shift=UP * 0.1), FadeIn(rows), run_time=0.45)
        boom = T("폭발", 22, RED, BOLD).move_to(ax.c2p(0.5, 0.7))
        for i in range(1, 9):
            ns = curve(2, A * fs ** i, TEAL)
            nt = curve(24, A * ft ** i, RED)
            anims = [Transform(cs, ns), Transform(ct, nt), k.animate.set_value(i)]
            if i == 8:
                anims.append(FadeIn(boom, scale=1.8))
            self.play(*anims, run_time=0.33)

        self.say("s5d")
        cond = VGroup(M(r"\eta\,(m+1) > 2", size=28, color=YEL), T("이면 발산", 15, FG)).arrange(RIGHT, buff=0.12).move_to([0, slot, 0])
        t1 = VGroup(M(r"\eta = 0.1", size=22), T("→ m ≥ 20인 오차가 터짐", 12, FG)).arrange(RIGHT, buff=0.1)
        t2 = VGroup(M(r"\eta = 0.01", size=22), T("→ m ≥ 200인 오차가 터짐", 12, FG)).arrange(RIGHT, buff=0.1)
        tb = VGroup(t1, t2).arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to([0, slot - 0.6, 0])
        self.play(FadeOut(f2, shift=UP * 0.1), FadeOut(rows), FadeIn(cond, shift=UP * 0.1), run_time=0.45)
        self.play(FadeIn(t1, shift=RIGHT * 0.1), run_time=0.5)
        self.play(FadeIn(t2, shift=RIGHT * 0.1), run_time=0.5)
        self.finish()
