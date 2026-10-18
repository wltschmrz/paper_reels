from render_kit import *
from _shared import *


def sig(t):
    # Appendix C.1: N(0,1) -> N(1, 0.6^2), linear interpolant
    return np.sqrt((1 - t) ** 2 + 0.36 * t ** 2)


def traj(t, x):
    return t + sig(t) * x


class S2(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()

        ax, frame = flow_frame(center=(-0.05, 0.62), yl=2.35, labels=True)
        zs = np.linspace(-2.0, 2.0, 11)
        trs = VGroup(*[ParametricFunction(lambda t, z=z: ax.c2p(t, traj(t, z)), t_range=[0, 1],
                                          color=FG, stroke_width=1.5).set_stroke(opacity=0.45)
                       for z in zs])
        d0 = density(ax, -1, 0.0, 1.0, color=GRAY)
        d1 = density(ax, 1, 1.0, 0.6, color=TEAL)
        lab0 = M(r"p_0=N(0,1)", size=19, color=GRAY).move_to([-1.5, 2.2, 0])
        lab1 = M(r"p_1=N(1,0.6^2)", size=19, color=TEAL).move_to([1.42, 2.2, 0])

        z0 = 1.0
        ss = ValueTracker(0.25)
        tt = ValueTracker(0.3)

        def build():
            s = ss.get_value()
            t = tt.get_value()
            g = VGroup()
            g.add(ParametricFunction(lambda r: ax.c2p(r, traj(r, z0)), t_range=[s, t],
                                     color=FG, stroke_width=3.4))
            p = ax.c2p(s, traj(s, z0))
            q = ax.c2p(t, traj(t, z0))
            g.add(Arrow(p, q, buff=0, color=YEL, stroke_width=4,
                        max_tip_length_to_length_ratio=0.18, max_stroke_width_to_length_ratio=12))
            g.add(Dot(p, radius=0.055, color=FG))
            g.add(Circle(radius=0.07, color=TEAL, stroke_width=2.5).move_to(q))
            return g

        pic = always_redraw(build)

        sv = DecimalNumber(0.25, num_decimal_places=2, font_size=22, color=YEL)
        tv = DecimalNumber(0.30, num_decimal_places=2, font_size=22, color=YEL)
        readout = VGroup(M(r"s=", size=22, color=FG), sv, M(r"\;t=", size=22, color=FG), tv)
        readout.arrange(RIGHT, buff=0.06).move_to([0.0, 2.2, 0])
        sv.add_updater(lambda m: m.set_value(ss.get_value()))
        tv.add_updater(lambda m: m.set_value(tt.get_value()))

        slot_y = -1.18
        eq1 = M(r"\Phi", r"(x_s,s,t)", size=28)
        eq1[0].set_color(YEL)
        eq1.move_to([0, slot_y, 0])

        foot = T("궤적: 부록 C.1 설정(선형 보간)으로 계산한 실제 플로우", 9.5, GRAY).move_to([0, -1.62, 0])
        fitw(foot, 4.15)

        # s2a: generic s -> t map
        self.say("s2a")
        self.play(FadeIn(h), FadeIn(frame), FadeIn(trs), FadeIn(d0), FadeIn(d1),
                  FadeIn(lab0), FadeIn(lab1), run_time=0.7)
        self.play(FadeIn(pic), FadeIn(readout), FadeIn(eq1, shift=UP * 0.1), FadeIn(foot), run_time=0.5)
        self.play(tt.animate.set_value(0.75), run_time=1.4, rate_func=smooth)

        # s2b: s = 0, t = 1, one jump from noise to data
        self.say("s2b")
        eq2m = M(r"\Phi", r"(x_0,0,1)", r"\;\,(s=0,\ t=1)", size=26)
        eq2m[0].set_color(YEL)
        eq2m[2].set_color(YEL)
        eq2t = T("= 신경망 1회 평가", 12, FG)
        eq2 = VGroup(eq2m, eq2t).arrange(RIGHT, buff=0.12).move_to([0, slot_y, 0])
        fitw(eq2, 4.15)
        p0 = np.array(ax.c2p(0.0, traj(0.0, z0)))
        p1 = np.array(ax.c2p(1.0, traj(1.0, z0)))
        jump = Arrow(p0, p1, buff=0, color=YEL, stroke_width=6,
                     max_tip_length_to_length_ratio=0.1, max_stroke_width_to_length_ratio=12)
        jlab = T("0 → 1 한 번 점프", 11, YEL)
        jlab.move_to((p0 + p1) / 2 + np.array([0.0, 0.42, 0]))
        nlab = T("노이즈", 10.5, GRAY).next_to(Dot(p0), DOWN, buff=0.12)
        dlab = T("데이터", 10.5, TEAL).next_to(Dot(p1), DOWN, buff=0.12)
        self.play(ss.animate.set_value(0.0), tt.animate.set_value(1.0),
                  FadeOut(eq1, shift=UP * 0.1), FadeIn(eq2m, shift=UP * 0.1),
                  run_time=1.1, rate_func=smooth)
        self.play(GrowArrow(jump), FadeIn(jlab), FadeIn(nlab), FadeIn(dlab),
                  FadeIn(eq2t, shift=LEFT * 0.1), run_time=0.6)
        self.play(Flash(p1, color=TEAL, line_length=0.12, flash_radius=0.15), run_time=0.5)

        # s2c: MeanFlow learns it through the average velocity u
        self.say("s2c")
        eq3 = M(r"\Phi(x_s,s,t)", "=", "x_s", "+", "(t-s)", r"\,u(x_s,s,t)", size=25)
        eq3[5].set_color(YEL)
        eq3.move_to([0, slot_y, 0])
        fitw(eq3, 4.15)
        mid_s, mid_t = 0.3, 0.85
        pm = (np.array(ax.c2p(mid_s, traj(mid_s, z0))) + np.array(ax.c2p(mid_t, traj(mid_t, z0)))) / 2
        slope = VGroup(T("평균 속도", 11, YEL), M(r"u", size=22, color=YEL)).arrange(RIGHT, buff=0.06)
        slope.move_to(pm + np.array([0.05, 0.38, 0]))
        self.play(FadeOut(eq2, shift=UP * 0.1), FadeIn(eq3, shift=UP * 0.1),
                  FadeOut(jump), FadeOut(jlab), FadeOut(nlab), FadeOut(dlab),
                  ss.animate.set_value(mid_s), tt.animate.set_value(mid_t),
                  run_time=1.0, rate_func=smooth)
        self.play(FadeIn(slope, shift=DOWN * 0.08), run_time=0.5)

        # s2d: where does the target come from?
        self.say("s2d")
        q = VGroup(T("정답", 11, YEL), M(r"u", size=22, color=YEL), T("는?", 11, YEL)).arrange(RIGHT, buff=0.05)
        q.move_to(slope)
        self.play(FadeOut(slope), FadeIn(q), Indicate(eq3[5], color=YEL, scale_factor=1.15), run_time=0.9)

        self.finish()
