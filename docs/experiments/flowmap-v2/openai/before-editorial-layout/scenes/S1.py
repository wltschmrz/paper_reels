from render_kit import *
from _shared import *
import numpy as np
import math


class S1(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        h.scale(1.22).move_to([0, 2.9, 0])

        def picture_icon(center, color=TEAL):
            frame = RoundedRectangle(
                width=0.62, height=0.48, corner_radius=0.05,
                stroke_color=color, stroke_width=2.4
            )
            sun = Circle(radius=0.045, stroke_color=color, stroke_width=2.0).move_to(
                frame.get_center() + np.array([0.16, 0.11, 0])
            )
            tri1 = Polygon(
                frame.get_center() + np.array([-0.22, -0.13, 0]),
                frame.get_center() + np.array([-0.03, 0.06, 0]),
                frame.get_center() + np.array([0.08, -0.13, 0]),
                color=color, stroke_width=2.2
            )
            tri2 = Polygon(
                frame.get_center() + np.array([-0.02, -0.13, 0]),
                frame.get_center() + np.array([0.12, 0.0, 0]),
                frame.get_center() + np.array([0.23, -0.13, 0]),
                color=color, stroke_width=2.2
            )
            return VGroup(frame, sun, tri1, tri2).move_to(center)

        left = np.array([-1.55, 0.58, 0])
        right = np.array([1.55, 0.58, 0])

        noise = Dot(left, radius=0.07, color=RED)
        noise_label = T("노이즈", 13, RED).next_to(noise, DOWN, buff=0.12)

        pic = picture_icon(right, TEAL)
        pic_label = T("종점", 13, TEAL).next_to(pic, DOWN, buff=0.1)

        arc = ArcBetweenPoints(left, right, angle=-PI * 0.57)
        n = 30
        arrows = VGroup()
        for i in range(n):
            a = arc.point_from_proportion(i / n)
            b = arc.point_from_proportion((i + 1) / n)
            seg = Arrow(
                a, b, buff=0.0, color=DGRAY,
                stroke_width=3.0, tip_length=0.075,
                max_tip_length_to_length_ratio=0.45
            )
            arrows.add(seg)

        jump = Arrow(left, right, buff=0.16, color=YEL, stroke_width=6, tip_length=0.18)
        jump_label = T("한 번", 13, YEL, MEDIUM).next_to(jump, DOWN, buff=0.08)

        many_label = T("수백 번 적분", 15, GRAY, MEDIUM).move_to([0, 1.47, 0])
        one_label = T("flow map 한 번", 17, YEL, MEDIUM).move_to([0, 1.47, 0])

        phi = M(r"\Phi(x_0, 0, 1)", size=28, color=YEL).move_to([0, 1.02, 0])

        question = fitw(T("stop gradient, 왜 통할까?", 20, FG, MEDIUM), 3.6).move_to([0, -0.02, 0])

        c1 = card("트릭 ①", ["stop", "gradient"], YEL, width=1.62, height=0.98)
        c2 = card("트릭 ②", ["adaptive", "weighting"], TEAL, width=1.75, height=0.98)
        cards = VGroup(c1, c2).arrange(RIGHT, buff=0.18).move_to([0, -0.88, 0])

        q1 = T("?", 24, FG, BOLD).move_to(c1.get_corner(UR) + np.array([-0.08, 0.05, 0]))
        q2 = T("?", 24, FG, BOLD).move_to(c2.get_corner(UR) + np.array([-0.08, 0.05, 0]))

        foot = T("그림 아이콘은 종점을 뜻하는 개형", 9.5, GRAY).move_to([0, -1.62, 0])

        walker = Dot(left, radius=0.045, color=FG)

        self.say("s1a")
        self.play(
            FadeIn(h),
            FadeIn(noise, scale=1.15),
            FadeIn(noise_label, shift=UP * 0.06),
            FadeIn(pic, scale=1.08),
            FadeIn(pic_label, shift=UP * 0.06),
            FadeIn(question, shift=UP * 0.08),
            FadeIn(foot),
            run_time=1.25
        )

        self.say("s1b")
        self.add(walker)
        self.play(
            FadeIn(many_label, shift=DOWN * 0.08),
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.03),
            MoveAlongPath(walker, arc),
            run_time=1.55,
            rate_func=linear
        )
        self.remove(walker)
        self.play(
            ReplacementTransform(many_label, one_label),
            FadeIn(phi, shift=DOWN * 0.08),
            arrows.animate.set_stroke(opacity=0.28),
            GrowArrow(jump),
            FadeIn(jump_label, shift=UP * 0.06),
            run_time=0.95
        )

        self.say("s1c")
        self.play(
            FadeIn(cards, shift=UP * 0.1),
            run_time=0.72
        )
        self.play(
            FadeIn(q1, scale=1.6),
            FadeIn(q2, scale=1.6),
            question.animate.set_color(MGRAY),
            jump.animate.set_stroke(width=7.5),
            run_time=0.6
        )

        self.finish()