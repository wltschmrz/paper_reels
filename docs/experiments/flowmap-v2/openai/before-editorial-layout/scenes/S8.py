from render_kit import *
from _shared import *
import numpy as np
import math


class S8(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        h.scale(1.18)
        fitw(h, 4.2)

        def make_card(title, body_lines, color, tag):
            c = card(title, body_lines, color=color, width=1.3, height=1.78, tag=tag)
            c[0].set_fill(self.C["BG"], opacity=0.98)
            c[0].set_stroke(color, width=2.2)
            return c

        c1 = make_card(
            "왜 통하나",
            ["functional", "gradient flow", "pointwise", "true flow map"],
            TEAL,
            "Theorem 1",
        )
        c2 = make_card(
            "왜 실패하나",
            ["GD", "every eta, every epsilon", "some init error < epsilon", "MeanFlow / Lagrangian v = 0"],
            RED,
            "Proposition 1",
        )
        c3 = make_card(
            "무엇이 고치나",
            ["normalized updates", "p >= 0.5", "uniformly", "bounded norms"],
            YEL,
            "Theorem 4",
        )

        cards = VGroup(c1, c2, c3).arrange(RIGHT, buff=0.14)
        fitw(cards, 4.08)
        cards.move_to([0, 0.3, 0])

        for c in cards:
            c.set_opacity(0.3)

        top_tag = T("세 결론", 13, GRAY).move_to([0, 1.55, 0])

        q1 = T("수렴", 12, TEAL, MEDIUM).next_to(c1, DOWN, buff=0.12)
        q2 = T("발산 가능", 12, RED, MEDIUM).next_to(c2, DOWN, buff=0.12)
        q3 = T("p >= 0.5", 12, YEL, MEDIUM).next_to(c3, DOWN, buff=0.12)

        hi1 = SurroundingRectangle(c1, color=TEAL, buff=0.045, corner_radius=0.08)
        hi2 = SurroundingRectangle(c2, color=RED, buff=0.045, corner_radius=0.08)
        hi3 = SurroundingRectangle(c3, color=YEL, buff=0.045, corner_radius=0.08)
        for box in [hi1, hi2, hi3]:
            box.set_stroke(width=2.4)

        lim1 = T("한계: 이 이론은 idealized functional gradient-flow setting의 결과", 10.4, GRAY)
        lim2 = T("neural network parametrization과 stochasticity는 다루지 않음", 10.4, GRAY)
        lim = VGroup(lim1, lim2).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
        fitw(lim, 4.08)
        lim.move_to([0, -1.62, 0])

        self.say("s8a")
        self.play(
            FadeIn(h),
            FadeIn(top_tag, shift=DOWN * 0.08),
            LaggedStart(
                FadeIn(c1, shift=UP * 0.12),
                FadeIn(c2, shift=UP * 0.12),
                FadeIn(c3, shift=UP * 0.12),
                lag_ratio=0.13,
            ),
            run_time=0.95,
        )
        self.play(
            c1.animate.set_opacity(1.0),
            c2.animate.set_opacity(0.18),
            c3.animate.set_opacity(0.18),
            Create(hi1),
            FadeIn(q1, shift=UP * 0.04),
            run_time=0.82,
        )

        self.say("s8b")
        self.play(
            FadeOut(hi1),
            q1.animate.set_opacity(0.28),
            c1.animate.set_opacity(0.18),
            c2.animate.set_opacity(1.0),
            Create(hi2),
            FadeIn(q2, shift=UP * 0.04),
            run_time=0.82,
        )
        self.play(c2.animate.shift(LEFT * 0.04), run_time=0.18)
        self.play(c2.animate.shift(RIGHT * 0.08), run_time=0.18)
        self.play(c2.animate.shift(LEFT * 0.04), run_time=0.18)

        self.say("s8c")
        self.play(
            FadeOut(hi2),
            q2.animate.set_opacity(0.28),
            c2.animate.set_opacity(0.18),
            c3.animate.set_opacity(1.0),
            Create(hi3),
            FadeIn(q3, shift=UP * 0.04),
            run_time=0.78,
        )
        self.play(
            Indicate(c3[1][-2], color=YEL, scale_factor=1.07),
            run_time=0.42,
        )

        self.say("s8d")
        self.play(
            cards.animate.shift(UP * 0.18).scale(0.965),
            FadeIn(lim, shift=UP * 0.08),
            run_time=0.96,
        )
        self.play(
            FadeOut(hi3),
            c1.animate.set_opacity(0.8),
            c2.animate.set_opacity(0.8),
            c3.animate.set_opacity(0.8),
            q1.animate.set_opacity(0.72),
            q2.animate.set_opacity(0.72),
            q3.animate.set_opacity(0.72),
            run_time=0.7,
        )

        self.finish()