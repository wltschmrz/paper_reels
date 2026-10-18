from render_kit import *
from _shared import *


def make_card(y, title, sub, col, GRAY):
    box = RoundedRectangle(width=4.0, height=0.74, corner_radius=0.1,
                           stroke_color=col, stroke_width=2).move_to([0, y, 0])
    tt = T(title, 14, col, MEDIUM)
    ss = T(sub, 10.5, GRAY)
    txt = VGroup(tt, ss).arrange(DOWN, buff=0.07, aligned_edge=LEFT)
    fitw(txt, 2.75)
    txt.move_to([0.42, y, 0])
    return VGroup(box, txt)


class S8(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()

        y1, y2, y3 = 1.85, 0.98, 0.11

        # card 1: gradient flow converges (Theorem 1, Theorem 3)
        c1 = make_card(y1, "경사 흐름: 수렴",
                       "Theorem 1 · functional gradient flow 가정", TEAL, GRAY)
        l1 = Line([-1.78, y1, 0], [-1.22, y1, 0], color=DGRAY, stroke_width=2)
        tgt1 = Dot([-1.25, y1, 0], radius=0.06, color=TEAL)
        d1 = Dot([-1.75, y1, 0], radius=0.05, color=RED)

        # card 2: finite step size may diverge (Proposition 1)
        c2 = make_card(y2, "유한 보폭: 발산 가능",
                       "Proposition 1 · 모든 η, 아주 작은 초기 오차로도", RED, GRAY)
        tgt2 = Dot([-1.5, y2, 0], radius=0.05, color=TEAL)
        amps = [0.0, 0.04, -0.08, 0.14, -0.22, 0.29]
        ys = np.linspace(0.2, -0.2, len(amps))
        pts = [np.array([-1.5 + a, y2 + yy, 0]) for a, yy in zip(amps, ys)]
        zig = VMobject(stroke_color=RED, stroke_width=2).set_points_as_corners(pts)
        d2 = Dot(pts[0], radius=0.05, color=RED)

        # card 3: moderate p gives best result (Abstract, Table 1)
        c3 = make_card(y3, "적당한 p: 최고 성능",
                       "CIFAR-10 FID 5.46 · NFE 1, p = 0.75", YEL, GRAY)
        x0, x1 = -1.8, -1.2
        sl = Line([x0, y3 - 0.12, 0], [x1, y3 - 0.12, 0], color=DGRAY, stroke_width=2)
        pt = ValueTracker(0.0)
        knob = always_redraw(lambda: Dot([x0 + (x1 - x0) * pt.get_value(), y3 - 0.12, 0],
                                         radius=0.05, color=YEL))
        plab = always_redraw(lambda: T(f"p = {pt.get_value():.2f}", 10.5, YEL)
                             .move_to([(x0 + x1) / 2, y3 + 0.14, 0]))

        # closing card
        abox = RoundedRectangle(width=2.7, height=0.56, corner_radius=0.1,
                                stroke_color=FG, stroke_width=2).move_to([0, -0.7, 0])
        atxt = T("arXiv 2610.20674", 15, FG, MEDIUM).move_to(abox)
        foot = fitw(T("아이콘은 개념 개형 · FID: Table 1, mean of 3 runs, 200K steps",
                      9.5, GRAY), 4.1).move_to([0, -1.62, 0])

        self.say("s8a")
        self.play(FadeIn(h), FadeIn(c1, shift=UP * 0.15), FadeIn(l1), FadeIn(tgt1), FadeIn(d1),
                  run_time=0.6)
        self.play(d1.animate.move_to(tgt1.get_center()), run_time=1.2)
        self.play(d1.animate.set_color(TEAL).scale(1.3), run_time=0.4)

        self.say("s8b")
        self.play(FadeIn(c2, shift=UP * 0.15), FadeIn(tgt2), FadeIn(d2), run_time=0.4)
        self.play(Create(zig), MoveAlongPath(d2, zig.copy()), run_time=1.0, rate_func=rate_functions.ease_in_quad)

        self.say("s8c")
        self.play(FadeIn(c3, shift=UP * 0.15), FadeIn(sl), FadeIn(knob), FadeIn(plab), run_time=0.4)
        self.play(pt.animate.set_value(0.75), run_time=0.9)
        self.play(FadeIn(abox), FadeIn(atxt, scale=1.1), FadeIn(foot), run_time=0.5)

        self.finish(extra=1.0)
