from render_kit import *
from _shared import *


class S4(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        ax, frame = flow_frame(center=(-0.05, 0.62), yl=2.35, labels=True)
        zs = np.linspace(-2.0, 2.0, 11)
        trs = VGroup(*[ParametricFunction(lambda t, z=z: ax.c2p(t, traj(t, z)), t_range=[0, 1], color=DGRAY, stroke_width=1.6)
                       for z in zs])
        xs = [-1.6, -0.2, 1.3]
        stars = VGroup(*[Circle(radius=0.07, color=YEL, stroke_width=2.5).move_to(ax.c2p(1, traj(1, x))) for x in xs])
        starts = VGroup(*[Dot(ax.c2p(0, x), radius=0.05, color=FG) for x in xs])
        tau = ValueTracker(0.0)
        self.mode = "MF"

        def build():
            tv = tau.get_value()
            g = VGroup()
            if self.mode == "MF":
                sw = 1 - np.exp(-tv)
            else:
                sw = np.exp(-tv)
            for x in xs:
                if self.mode == "MF":
                    y = traj(sw, x)
                    end = y + (1 - sw) * U0(y, sw, 1)
                    if sw > 0.004:
                        g.add(ParametricFunction(lambda r, x=x: ax.c2p(r, traj(r, x)), t_range=[0, sw], color=FG, stroke_width=3.2))
                    if sw < 0.996:
                        g.add(DashedLine(ax.c2p(sw, y), ax.c2p(1, end), color=RED, stroke_width=3, dash_length=0.06))
                    g.add(Dot(ax.c2p(sw, y), radius=0.04, color=YEL))
                else:
                    y = x + sw * U0(x, 0, sw)
                    end = flow(y, sw, 1)
                    if sw > 0.004:
                        g.add(DashedLine(ax.c2p(0, x), ax.c2p(sw, y), color=RED, stroke_width=3, dash_length=0.06))
                    if sw < 0.996:
                        g.add(ParametricFunction(lambda r, y=y, sw=sw: ax.c2p(r, flow(y, sw, r)), t_range=[sw, 1], color=FG, stroke_width=3.2))
                    g.add(Dot(ax.c2p(sw, y), radius=0.04, color=YEL))
                g.add(Square(side_length=0.1, color=RED, fill_color=FG, fill_opacity=1, stroke_width=2).rotate(PI / 4).move_to(ax.c2p(1, end)))
            base = ax.c2p(0, -2.8)[1]
            g.add(DashedLine([ax.c2p(sw, 0)[0], base, 0], [ax.c2p(sw, 0)[0], ax.c2p(0, 2.8)[1], 0], color=YEL, stroke_width=1.3,
                             dash_length=0.05).set_opacity(0.55))
            return g

        paths = always_redraw(build)
        tlabel = VGroup(T("학습 시간", 11, GRAY), M(r"\tau =", size=24, color=FG), DecimalNumber(0, num_decimal_places=1, font_size=24))
        tlabel.arrange(RIGHT, buff=0.08).move_to([-1.15, 2.2, 0])
        tlabel[2].add_updater(lambda m: m.set_value(tau.get_value()))
        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.3, color=FG, stroke_width=3), T("진짜 흐름", 10.5, FG)).arrange(RIGHT, buff=0.08),
            VGroup(DashedLine(ORIGIN, RIGHT * 0.3, color=RED, stroke_width=3, dash_length=0.06), T("처음 모델", 10.5, RED)).arrange(RIGHT, buff=0.08),
            VGroup(Circle(radius=0.06, color=YEL, stroke_width=2.5), T("진짜 도착점", 10.5, YEL)).arrange(RIGHT, buff=0.08),
        ).arrange(DOWN, buff=0.05, aligned_edge=LEFT).move_to([1.28, 2.17, 0])
        foot = T("가정: 함수 공간에서의 연속 학습 · 합성 데이터 실험에서 실제 학습이 이 공식과 일치 (Fig. 2)", 9, GRAY).move_to([0, -1.62, 0])
        fitw(foot, 4.2)
        slot_y = -1.18

        self.say("s4a")
        self.play(FadeIn(h), FadeIn(frame), FadeIn(trs), FadeIn(starts), run_time=0.5)
        self.play(FadeIn(paths), FadeIn(tlabel), FadeIn(leg), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(s, scale=1.8) for s in stars], lag_ratio=0.3), FadeIn(foot), run_time=0.7)

        self.say("s4b")
        badge = VGroup(T("Theorem 1", 14, YEL, MEDIUM), T("진짜 플로우 맵으로 수렴", 14, FG)).arrange(RIGHT, buff=0.15).move_to([0, slot_y, 0])
        self.play(tau.animate.set_value(1.2), FadeIn(badge, shift=UP * 0.1), run_time=1.6, rate_func=smooth)

        self.say("s4c")
        eqm = M(r"\Phi_\tau", "=", r"\Phi_0", r"\big(", r"\Phi^\star", r"(x,s,t_\tau)", r",\,t_\tau,\,t", r"\big)", size=27)
        eqm[2].set_color(RED)
        eqm[4].set_color(FG)
        eqm.move_to([0, slot_y, 0])
        lab = T("MeanFlow", 12, YEL, MEDIUM).next_to(tlabel, DOWN, buff=0.08).align_to(tlabel, LEFT)
        self.play(FadeOut(badge, shift=UP * 0.1), FadeIn(eqm, shift=UP * 0.1), FadeIn(lab), run_time=0.45)
        self.play(tau.animate.set_value(2.3), run_time=1.7, rate_func=linear)

        self.say("s4d")
        bnd = M(r"\|\Phi_\tau-\Phi^\star\|_\infty", r"\le", r"2M\,e^{-\rho_{\min}\tau}", size=27)
        bnd[2].set_color(YEL)
        bnd.move_to([0, slot_y, 0])
        self.play(FadeOut(eqm, shift=UP * 0.1), FadeIn(bnd, shift=UP * 0.1), run_time=0.4)
        self.play(tau.animate.set_value(4.5), run_time=0.95, rate_func=linear)

        self.say("s4e")
        eql = M(r"\Phi_\tau", "=", r"\Phi^\star", r"\big(", r"\Phi_0", r"(x,s,s_\tau)", r",\,s_\tau,\,t", r"\big)", size=27)
        eql[4].set_color(RED)
        eql.move_to([0, slot_y, 0])
        lab2 = T("Lagrangian", 12, TEAL, MEDIUM).move_to(lab).align_to(lab, LEFT)
        self.play(FadeOut(paths), run_time=0.2)
        self.mode = "L"
        tau.set_value(0.0)
        paths = always_redraw(build)
        self.play(FadeIn(paths), FadeOut(bnd, shift=UP * 0.1), FadeIn(eql, shift=UP * 0.1), FadeOut(lab), FadeIn(lab2), run_time=0.35)
        self.play(tau.animate.set_value(3.8), run_time=1.8, rate_func=smooth)
        self.finish()
