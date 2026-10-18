from render_kit import *
from _shared import *


class S1(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        A = np.array([-1.5, 0.55, 0])
        B = np.array([1.5, 0.55, 0])
        na = Dot(A, radius=0.075, color=FG)
        nb = Dot(B, radius=0.085, color=TEAL)
        la = T("노이즈", 13, GRAY).next_to(na, DOWN, buff=0.15)
        lb = T("그림", 13, TEAL).next_to(nb, DOWN, buff=0.15)
        arc = ArcBetweenPoints(A, B, angle=-PI * 0.6)
        n = 46
        dots = VGroup(*[Dot(arc.point_from_proportion(i / n), radius=0.022, color=GRAY) for i in range(1, n)])
        t1 = T("계산 수백 번", 34, FG, MEDIUM).move_to([0, 1.95, 0])

        self.say("s1a")
        self.play(FadeIn(h), FadeIn(t1, shift=DOWN * 0.1), FadeIn(na), FadeIn(la), run_time=0.45)
        walker = Dot(A, radius=0.05, color=FG)
        self.add(walker)
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.9),
                  MoveAlongPath(walker, arc), run_time=1.6, rate_func=linear)
        self.remove(walker)
        self.play(FadeIn(nb, scale=1.6), FadeIn(lb), run_time=0.3)

        self.say("s1b")
        t2 = VGroup(T("계산", 34, FG, MEDIUM), T("수백 번", 34, GRAY, MEDIUM), T("→", 34, FG),
                    T("1번", 34, YEL, MEDIUM)).arrange(RIGHT, buff=0.16)
        fitw(t2, 4.1).move_to([0, 1.95, 0])
        jump = Arrow(A, B, buff=0.1, color=YEL, stroke_width=5, tip_length=0.16)
        lj = T("한 번", 13, YEL).next_to(jump, DOWN, buff=0.1)
        self.play(ReplacementTransform(t1, VGroup(t2[0], t2[1])), FadeIn(t2[2:], shift=LEFT * 0.2),
                  dots.animate.set_opacity(0.3), run_time=0.5)
        self.play(GrowArrow(jump), FadeIn(lj), run_time=0.5)

        self.say("s1c")
        cards = VGroup()
        for tag, lines, col in [("트릭 ①", ["stop gradient"], YEL), ("트릭 ②", ["adaptive", "normalization"], TEAL)]:
            box = RoundedRectangle(width=1.95, height=1.12, corner_radius=0.1, stroke_color=col, stroke_width=2)
            tg = T(tag, 11, GRAY)
            body = VGroup(*[T(l, 15, col, MEDIUM) for l in lines]).arrange(DOWN, buff=0.05)
            inner = VGroup(tg, body).arrange(DOWN, buff=0.1).move_to(box)
            cards.add(VGroup(box, inner))
        cards.arrange(RIGHT, buff=0.18).move_to([0, -0.75, 0])
        qs = VGroup(*[T("?", 30, FG, BOLD).move_to(c[0].get_corner(UR) + np.array([-0.05, 0.05, 0])) for c in cards])
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.35), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(q, scale=2.2) for q in qs], lag_ratio=0.3), run_time=0.6)
        self.finish()
