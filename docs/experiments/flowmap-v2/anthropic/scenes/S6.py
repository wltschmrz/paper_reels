from render_kit import *
from _shared import *


class S6(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()

        # Eq. (20): normalized update; the exponent p (the knob) in YEL
        eq = M(r"u_{k+1}", "=", r"u_k", "-", r"\eta\rho\,",
               r"{r_k \over (\|r_k\|^2+c)^{p}}", size=30)
        fitw(eq, 3.9).move_to([0, 2.02, 0])
        eq[5].set_color(YEL)
        eq[5][0:2].set_color(FG)
        rdef = T("r = 잔차 (Eq. 20의 정규화 업데이트)", 11, GRAY).move_to([0, 1.5, 0])

        # Frame: residual size vs update size
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 2.5, 1], x_length=3.3, y_length=1.8, tips=False,
                  axis_config={"color": MGRAY, "stroke_width": 2, "include_ticks": False})
        ax.move_to([0.1, -0.05, 0])
        xl = T("잔차 크기 ‖r‖", 10.5, GRAY).next_to(ax.x_axis.get_end(), DOWN, buff=0.08).align_to(ax.x_axis.get_end(), RIGHT)
        yl = T("업데이트 크기", 10.5, GRAY).next_to(ax.y_axis.get_end(), RIGHT, buff=0.1).shift(DOWN * 0.02)

        c = 0.25
        p = ValueTracker(0.0)
        rs_all = np.linspace(0, 4, 300)

        def fp(r, pv):
            return r / (r * r + c) ** pv

        def sup_val():
            return float(np.max(fp(rs_all, p.get_value())))

        def build():
            pv = p.get_value()
            rs = rs_all
            ys = fp(rs, pv)
            keep = ys <= 2.5
            if not keep.all():
                i = int(np.argmax(~keep))
                rs, ys = rs[:i + 1], np.minimum(ys[:i + 1], 2.5)
            col = RED if pv < 0.5 - 1e-3 else TEAL
            return VMobject(stroke_color=col, stroke_width=3.4).set_points_smoothly(
                [ax.c2p(r, y) for r, y in zip(rs, ys)])

        def build_bound():
            if p.get_value() < 0.5 - 1e-3:
                return VMobject()
            s = min(sup_val(), 2.5)
            return DashedLine(ax.c2p(0, s), ax.c2p(4, s), color=TEAL,
                              stroke_width=1.8, dash_length=0.06).set_stroke(opacity=0.8)

        cv = always_redraw(build)
        bound = always_redraw(build_bound)

        ul = T("상한", 10.5, TEAL)
        ul.add_updater(lambda m: m.move_to(ax.c2p(4, min(sup_val(), 2.5)) + LEFT * 0.25 + UP * 0.16))

        pd = DecimalNumber(0, num_decimal_places=2, font_size=26, color=YEL)
        pd.add_updater(lambda m: m.set_value(p.get_value()))
        pl = VGroup(M("p =", size=26, color=YEL), pd).arrange(RIGHT, buff=0.08).move_to([-0.75, 1.12, 0])
        bad = T("상한 없음 ✗", 12, RED).next_to(pl, RIGHT, buff=0.3)
        good = T("p ≥ 0.5: 상한 있음 ✓", 12, TEAL).next_to(pl, RIGHT, buff=0.3)

        foot = T("Theorem 4 (논문의 가정 하) · c = 0.25로 그린 개형", 9.5, GRAY).move_to([0, -1.62, 0])
        fitw(foot, 4.1)

        # s6a: divide the update by residual size (p = 0: plain update, unbounded)
        self.say("s6a")
        self.play(FadeIn(h), FadeIn(eq), FadeIn(rdef), Create(ax), FadeIn(xl), FadeIn(yl),
                  FadeIn(foot), run_time=0.5)
        self.add(bound)
        self.play(Create(cv), FadeIn(pl), FadeIn(bad), run_time=0.8)
        self.play(Indicate(eq[5][2:], color=YEL, scale_factor=1.12), run_time=0.5)

        # s6b: p from 0 to 0.5 -> bounded update norm; bound line appears and is held
        self.say("s6b")
        bl = T("Theorem 4: p ≥ 0.5이면 보폭 유계", 11.5, TEAL)
        fitw(bl, 4.1).move_to([0, -1.36, 0])
        self.play(p.animate.set_value(0.5), run_time=1.2, rate_func=smooth)
        self.add(ul)
        self.play(FadeOut(bad), FadeIn(good, scale=1.2), FadeIn(ul), FadeIn(bl, shift=UP * 0.1),
                  run_time=0.45)
        self.play(Indicate(good, color=TEAL, scale_factor=1.08), run_time=0.5)

        # s6c: p = 1 -> convergence to an O(eta^1/2) neighborhood
        self.say("s6c")
        conv = VGroup(T("p = 1:", 12, YEL), M(r"O(\eta^{1/2})", size=24, color=TEAL),
                      T("근방으로 수렴 (Theorem 4)", 12, TEAL)).arrange(RIGHT, buff=0.08)
        fitw(conv, 4.1).move_to([0, -1.36, 0])
        self.play(p.animate.set_value(1.0), FadeOut(bl), run_time=1.0, rate_func=smooth)
        self.play(FadeIn(conv, shift=UP * 0.1), run_time=0.4)

        # s6d: continue sweep to 1.5, pose the practical question
        self.say("s6d")
        q = T("좋은 성능은 특정 reweighting 범위에서만 (Abstract)", 11, YEL)
        fitw(q, 4.1).move_to([0, -1.36, 0])
        self.play(p.animate.set_value(1.5), run_time=1.2, rate_func=smooth)
        self.play(FadeOut(conv), FadeIn(q, shift=UP * 0.1), run_time=0.45)
        self.finish()
