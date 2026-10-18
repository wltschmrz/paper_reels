from render_kit import *
from _shared import *


class S3(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        Y = 1.45
        e1 = M(r"\mathcal{L}", "=", r"\big\|", "u", "-", "?", r"\big\|^2", size=42).move_to([0, Y, 0])
        e1[3].set_color(TEAL)
        e1[5].set_color(GRAY)
        lu = T("모델의 답", 12, TEAL).next_to(e1[3], DOWN, buff=0.18).shift(LEFT * 0.3)
        lq = T("정답은 모름", 12, GRAY).next_to(e1[5], DOWN, buff=0.18).shift(RIGHT * 0.35)

        self.say("s3a")
        self.play(FadeIn(h), Write(e1), run_time=0.8)
        self.play(FadeIn(lu), FadeIn(lq), run_time=0.35)

        self.say("s3b")
        e2 = M(r"\mathcal{L}", "=", r"\big\|", "u", "-", r"u_{\text{tgt}}", r"\big\|^2", size=42).move_to([0, Y, 0])
        e2[3].set_color(TEAL)
        e2[5].set_color(YEL)
        lt = T("정답지", 12, YEL).next_to(e2[5], DOWN, buff=0.18)
        dfn = M(r"u_{\text{tgt}}", "=", "v", "+", "(t-s)", r"\big(", r"\nabla_x", "u", r"\,v", "+", r"\partial_s", "u", r"\big)",
                size=27).move_to([0, 0.15, 0])
        dfn[0].set_color(YEL)
        dfn[7].set_color(TEAL)
        dfn[11].set_color(TEAL)
        vn = T("v: 이미 주어진 속도장", 10, GRAY).next_to(dfn, DOWN, buff=0.14)
        self.play(TransformMatchingTex(e1, e2), FadeOut(lq), lu.animate.next_to(e2[3], DOWN, buff=0.18), run_time=0.55)
        self.play(FadeIn(lt), FadeIn(dfn, shift=DOWN * 0.1), FadeIn(vn), run_time=0.5)
        a1 = CurvedArrow(lu.get_bottom() + DOWN * 0.04, dfn[7].get_top() + UP * 0.04, angle=0.5, color=TEAL, stroke_width=2.5, tip_length=0.1)
        a2 = CurvedArrow(lu.get_bottom() + DOWN * 0.04, dfn[11].get_top() + UP * 0.04, angle=0.7, color=TEAL, stroke_width=2.5, tip_length=0.1)
        self.play(Create(a1), Create(a2), run_time=0.6)

        self.say("s3c")
        e3 = M(r"\mathcal{L}", "=", r"\big\|", "u", "-", r"\mathrm{sg}", r"\big(", r"u_{\text{tgt}}", r"\big)", r"\big\|^2",
               size=42).move_to([0, Y, 0])
        e3[3].set_color(TEAL)
        e3[5].set_color(RED)
        e3[7].set_color(YEL)
        self.play(TransformMatchingTex(e2, e3), lu.animate.next_to(e3[3], DOWN, buff=0.18),
                  lt.animate.next_to(e3[7], DOWN, buff=0.18), run_time=0.55)
        L = e3[0].get_top() + UP * 0.06
        g1 = CurvedArrow(L, e3[3].get_top() + UP * 0.06, angle=-1.6, color=TEAL, stroke_width=2.5, tip_length=0.1)
        g2 = CurvedArrow(L, e3[7].get_top() + UP * 0.06, angle=-1.0, color=RED, stroke_width=2.5, tip_length=0.1)
        g2.set_stroke(opacity=0.8)
        mid = g2.point_from_proportion(0.6)
        cut = VGroup(Line(mid + UL * 0.09, mid + DR * 0.09), Line(mid + UR * 0.09, mid + DL * 0.09)).set_stroke(RED, 4)
        tg1 = T("학습 신호", 10.5, TEAL).next_to(g1, UP, buff=0.03)
        tg2 = T("끊음", 10.5, RED).next_to(cut, UP, buff=0.04)
        self.play(Create(g1), FadeIn(tg1), run_time=0.5)
        self.play(Create(g2), run_time=0.4)
        self.play(FadeIn(cut, scale=1.8), FadeIn(tg2), Indicate(e3[5], color=RED, scale_factor=1.3), run_time=0.5)

        self.say("s3d")
        cu = M("u", size=34, color=TEAL).move_to([-0.85, -0.85, 0])
        ct = M(r"u_{\text{tgt}}", size=34, color=YEL).move_to([0.85, -0.85, 0])
        c1 = CurvedArrow(cu.get_top() + UP * 0.05, ct.get_top() + UP * 0.05, angle=-1.2, color=GRAY, stroke_width=2.2, tip_length=0.1)
        c2 = CurvedArrow(ct.get_bottom() + DOWN * 0.05, cu.get_bottom() + DOWN * 0.05, angle=-1.2, color=GRAY, stroke_width=2.2, tip_length=0.1)
        k1 = T("정답지 만들기", 10, GRAY).next_to(c1, UP, buff=0.03)
        k2 = T("채점", 10, GRAY).next_to(c2, DOWN, buff=0.03)
        q = VGroup(T("수렴 보장", 20, FG, MEDIUM), T("?", 24, RED, BOLD)).arrange(RIGHT, buff=0.08).move_to([0, -1.62, 0])
        self.play(dfn.animate.set_opacity(0.3), FadeOut(vn), FadeOut(a1), FadeOut(a2), FadeIn(cu), FadeIn(ct), run_time=0.4)
        self.play(Create(c1), Create(c2), FadeIn(k1), FadeIn(k2), run_time=0.9)
        self.play(ShowPassingFlash(c1.copy().set_stroke(YEL, 4), time_width=0.6), ShowPassingFlash(c2.copy().set_stroke(YEL, 4), time_width=0.6),
                  FadeIn(q, shift=UP * 0.1), run_time=1.0)
        self.finish()
