from render_kit import *
from _shared import *


class S8(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        cards = VGroup()
        for name, desc, col in [("stop gradient", "연속 학습에서 진짜 답으로 수렴 (증명)", YEL),
                                ("adaptive normalization", "유한한 걸음에서 폭발을 막는 장치", TEAL)]:
            box = RoundedRectangle(width=4.0, height=0.95, corner_radius=0.1, stroke_color=col, stroke_width=2)
            inner = VGroup(T(name, 17, col, MEDIUM), T(desc, 12.5, FG)).arrange(DOWN, buff=0.1).move_to(box)
            cards.add(VGroup(box, inner))
        cards.arrange(DOWN, buff=0.25).move_to([0, 0.9, 0])

        self.say("s8a")
        self.play(FadeIn(h), FadeIn(cards[0], shift=UP * 0.15), run_time=0.6)

        self.say("s8b")
        self.play(FadeIn(cards[1], shift=UP * 0.15), run_time=0.6)

        self.say("s8c")
        box = RoundedRectangle(width=4.0, height=1.9, corner_radius=0.12, stroke_color=TEAL, stroke_width=2.2)
        inner = VGroup(
            T("arXiv 2610.20674", 16, TEAL),
            VGroup(T("On the Stability and Convergence", 15.5, YEL, MEDIUM), T("of Flow Map Training", 15.5, YEL, MEDIUM)).arrange(DOWN, buff=0.06),
            T("Nath · Stanic · Bose · Gidel · Bertrand", 10.5, GRAY),
            T("Inria · Mila · Imperial College London 외 · 2026.10", 9.5, GRAY),
        ).arrange(DOWN, buff=0.12).move_to(box)
        card = VGroup(box, inner).move_to([0, 0.75, 0])
        self.play(FadeOut(cards, shift=UP * 0.2), FadeOut(h), FadeIn(card, shift=UP * 0.15), run_time=0.6)
        self.finish(extra=1.3)
