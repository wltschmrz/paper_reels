from render_kit import *
from _shared import *


def sig(t):
    # Appendix C.1: p0 = N(0,1), p1 = N(1, 0.6^2), linear interpolant
    return np.sqrt((1 - t) ** 2 + 0.36 * t ** 2)


def traj(t, x):
    return t + sig(t) * x


def U0(y, s, t):
    # Appendix C.1 initialization u0(x, s, t) = 0.8 cos(1.3x + 2s) - 0.2t
    return 0.8 * np.cos(1.3 * y + 2 * s) - 0.2 * t


class S4(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        RHO = 1.0  # Appendix C.1 setup
        ax, frame = flow_frame(center=(-0.05, 0.62), yl=2.35, labels=False)
        d0 = density(ax, -1, 0.0, 1.0, color=DGRAY)
        d1 = density(ax, 1, 1.0, 0.6, color=DGRAY)
        zs = np.linspace(-2.0, 2.0, 11)
        trs = VGroup(*[ParametricFunction(lambda t, z=z: ax.c2p(t, traj(t, z)), t_range=[0, 1],
                                          color=DGRAY, stroke_width=1.6) for z in zs])
        xs = [-1.6, -0.2, 1.3]
        stars = VGroup(*[Circle(radius=0.08, color=YEL, stroke_width=2.8).move_to(ax.c2p(1, traj(1, x))) for x in xs])
        starts = VGroup(*[Dot(ax.c2p(0, x), radius=0.055, color=FG) for x in xs])
        tau = ValueTracker(0.0)

        # larger axis labels (replacing the small built-in ones)
        yb = ax.c2p(0, -2.8)[1]
        lab_s = T("s = 0", 12.5, GRAY).move_to([ax.c2p(0, 0)[0], yb - 0.17, 0])
        lab_t = T("t = 1", 12.5, GRAY).move_to([ax.c2p(1, 0)[0], yb - 0.17, 0])
        lab_time = T("시간 →", 12.5, GRAY).move_to([ax.c2p(0.5, 0)[0], yb - 0.17, 0])
        axlabels = VGroup(lab_s, lab_t, lab_time)

        def tsw():
            # s = 0, t = 1, rho = 1: switch point t_tau moves from s to t
            return 1 - np.exp(-RHO * tau.get_value())

        def build():
            sw = tsw()
            g = VGroup()
            for x in xs:
                y = traj(sw, x)
                end = y + (1 - sw) * U0(y, sw, 1)
                if sw > 0.004:
                    g.add(ParametricFunction(lambda r, x=x: ax.c2p(r, traj(r, x)), t_range=[0, sw],
                                             color=FG, stroke_width=3.4))
                if sw < 0.996:
                    g.add(DashedLine(ax.c2p(sw, y), ax.c2p(1, end), color=RED, stroke_width=3.2, dash_length=0.06))
                g.add(Dot(ax.c2p(sw, y), radius=0.045, color=YEL))
                g.add(Square(side_length=0.11, color=RED, fill_color=FG, fill_opacity=1, stroke_width=2)
                      .rotate(PI / 4).move_to(ax.c2p(1, end)))
            xx = ax.c2p(sw, 0)[0]
            g.add(DashedLine([xx, ax.c2p(0, -2.8)[1], 0], [xx, ax.c2p(0, 2.8)[1], 0], color=YEL,
                             stroke_width=1.4, dash_length=0.05).set_stroke(opacity=0.55))
            return g

        paths = always_redraw(build)

        tlabel = VGroup(T("학습 시간", 13, GRAY), M(r"\tau =", size=30, color=FG),
                        DecimalNumber(0, num_decimal_places=1, font_size=30, color=FG))
        tlabel.arrange(RIGHT, buff=0.08)
        tlabel.move_to([-2.05 + tlabel.width / 2, 2.22, 0])
        tlabel[2].add_updater(lambda m: m.set_value(tau.get_value()))
        swlabel = VGroup(M(r"t_\tau =", size=30, color=YEL),
                         DecimalNumber(0, num_decimal_places=2, font_size=30, color=YEL))
        swlabel.arrange(RIGHT, buff=0.08).next_to(tlabel, DOWN, buff=0.08).align_to(tlabel, LEFT)
        swlabel[1].add_updater(lambda m: m.set_value(tsw()))

        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.32, color=FG, stroke_width=3.4), T("진짜 흐름", 12.5, FG)).arrange(RIGHT, buff=0.08),
            VGroup(DashedLine(ORIGIN, RIGHT * 0.32, color=RED, stroke_width=3.2, dash_length=0.06),
                   T("초기 맵", 12.5, RED)).arrange(RIGHT, buff=0.08),
            VGroup(Circle(radius=0.07, color=YEL, stroke_width=2.8), T("진짜 도착점", 12.5, YEL)).arrange(RIGHT, buff=0.08),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        leg.move_to([2.08 - leg.width / 2, 2.12, 0])

        foot = T("가정: 이상적 gradient flow · 신경망 학습은 미포함 (§6)", 10.5, GRAY)
        fitw(foot, 4.15).move_to([0, -1.62, 0])
        slot_y = -1.17

        # s4a: setting
        self.say("s4a")
        self.play(FadeIn(h), FadeIn(frame), FadeIn(axlabels), FadeIn(d0), FadeIn(d1), FadeIn(trs),
                  FadeIn(starts), run_time=0.5)
        self.play(FadeIn(paths), FadeIn(tlabel), FadeIn(swlabel), FadeIn(leg), run_time=0.6)
        badge = VGroup(T("Theorem 1", 14, YEL, MEDIUM), T("functional gradient flow 가정", 13, GRAY)).arrange(RIGHT, buff=0.15)
        fitw(badge, 4.1).move_to([0, slot_y, 0])
        self.play(FadeIn(badge, shift=UP * 0.1), FadeIn(foot),
                  LaggedStart(*[FadeIn(s, scale=1.8) for s in stars], lag_ratio=0.3), run_time=0.6)
        self.play(tau.animate.set_value(0.3), run_time=0.45, rate_func=smooth)

        # s4b: convergence despite stop gradient, closed form Eq. (13)
        self.say("s4b")
        eqm = M(r"\Phi_\tau", "=", r"\Phi_0", r"\big(", r"\Phi^\star", r"(x,s,", r"t_\tau", r")", r",\,", r"t_\tau",
                r",\,t", r"\big)", size=28)
        eqm[2].set_color(RED)
        eqm[4].set_color(FG)
        eqm[6].set_color(YEL)
        eqm[9].set_color(YEL)
        fitw(eqm, 4.1).move_to([0, slot_y, 0])
        self.play(FadeOut(badge, shift=UP * 0.1), FadeIn(eqm, shift=UP * 0.1), run_time=0.4)
        self.play(tau.animate.set_value(1.2), run_time=1.7, rate_func=smooth)

        # s4c: front part becomes true path, exponential error bound Eq. (15)
        self.say("s4c")
        self.play(tau.animate.set_value(2.4), run_time=1.3, rate_func=linear)
        bnd = M(r"\|\Phi_\tau-\Phi^\star\|_\infty", r"\le", r"2M\,e^{-\rho_{\min}\tau}", size=30)
        bnd[2].set_color(YEL)
        fitw(bnd, 4.1).move_to([0, slot_y, 0])
        self.play(FadeOut(eqm, shift=UP * 0.1), FadeIn(bnd, shift=UP * 0.1), run_time=0.4)
        self.play(tau.animate.set_value(4.0), run_time=1.5, rate_func=linear)
        self.finish(extra=1.0)
