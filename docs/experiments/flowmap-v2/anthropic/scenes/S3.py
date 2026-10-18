from render_kit import *
from _shared import *


def lock_icon(color, at):
    body = Rectangle(width=0.22, height=0.17).set_fill(color, 1).set_stroke(color, 1.5)
    shackle = Arc(radius=0.075, start_angle=0, angle=PI).set_stroke(color, 2.5)
    shackle.next_to(body, UP, buff=0)
    g = VGroup(body, shackle)
    g.move_to(at)
    return g


class S3(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()

        # ---------- primary object: the target u_tgt (Eq. 5) ----------
        Y = 0.85
        dfn = M(r"u_{\text{tgt}}", "=", "v", "+", "(t-s)", r"\big(", r"\nabla_x", "u", r"\,v", "+",
                r"\partial_s", "u", r"\big)", size=28)
        fitw(dfn, 4.0)
        dfn.move_to([0, Y, 0])
        dfn[0].set_color(YEL)
        dfn[2].set_color(MGRAY)
        dfn[8].set_color(MGRAY)
        dfn[7].set_color(TEAL)
        dfn[11].set_color(TEAL)
        g1 = VGroup(*dfn[0:3])
        g2 = VGroup(*dfn[3:9])
        g3 = VGroup(*dfn[9:13])

        lv = T("v: 순간 속도", 10.5, MGRAY).next_to(dfn[2], DOWN, buff=0.22)
        lu = T("u: 평균 속도 (모델)", 10.5, TEAL).next_to(dfn[7], DOWN, buff=0.22).shift(RIGHT * 0.35)

        # term counter (moving quantity)
        kt = ValueTracker(0)
        num = DecimalNumber(0, num_decimal_places=0, font_size=26, color=YEL)
        num.add_updater(lambda m: m.set_value(round(kt.get_value())))
        lab = T("항", 12, YEL)
        tot = M(r"/\,3", size=26, color=YEL)
        cnt = VGroup(lab, num, tot).arrange(RIGHT, buff=0.08).move_to([1.45, 2.2, 0])
        num.add_updater(lambda m: m.next_to(lab, RIGHT, buff=0.08))

        self.say("s3a")
        self.play(FadeIn(h), FadeIn(g1, shift=DOWN * 0.1), FadeIn(lv), FadeIn(cnt),
                  kt.animate.set_value(1), run_time=0.6)
        self.play(FadeIn(g2, shift=DOWN * 0.1), kt.animate.set_value(2), run_time=0.5)
        self.play(FadeIn(g3, shift=DOWN * 0.1), FadeIn(lu), kt.animate.set_value(3), run_time=0.55)

        # ---------- s3b: wrap in sg (gray box + lock) ----------
        self.say("s3b")
        rhs = VGroup(*dfn[2:13])
        box = SurroundingRectangle(rhs, color=GRAY, buff=0.08, corner_radius=0.06, stroke_width=2.5)
        sgt = M(r"\mathrm{sg}", size=24, color=GRAY).next_to(box, LEFT, buff=0.04).shift(UP * 0.22)
        lk = lock_icon(GRAY, box.get_corner(UR) + RIGHT * 0.02 + UP * 0.12)
        loss = M(r"\mathcal{L}", "=", r"\big\|", "u", "-", r"\mathrm{sg}", r"\big(", r"u_{\text{tgt}}",
                 r"\big)", r"\big\|^2", size=34).move_to([-0.25, 1.75, 0])
        loss[3].set_color(TEAL)
        loss[5].set_color(GRAY)
        loss[7].set_color(YEL)
        self.play(Create(box), FadeOut(cnt), run_time=0.6)
        self.play(FadeIn(sgt), FadeIn(lk, scale=1.6), run_time=0.4)
        self.play(Write(loss), run_time=0.75)

        # ---------- s3c: analogy (student grading with own answer sheet) ----------
        self.say("s3c")
        st = VGroup(T("학생", 13, TEAL, MEDIUM), M("=", "u", size=26)).arrange(RIGHT, buff=0.08)
        st[1][1].set_color(TEAL)
        st.move_to([-1.25, -0.45, 0])
        sh = VGroup(T("답안지", 13, YEL, MEDIUM), M("=", r"u_{\text{tgt}}", size=26)).arrange(RIGHT, buff=0.08)
        sh[1][1].set_color(YEL)
        sh.move_to([1.2, -0.45, 0])
        a1 = Arrow(st.get_right() + UP * 0.12, sh.get_left() + UP * 0.12, buff=0.1, color=GRAY,
                   stroke_width=2.5, max_tip_length_to_length_ratio=0.12)
        a2 = Arrow(sh.get_left() + DOWN * 0.12, st.get_right() + DOWN * 0.12, buff=0.1, color=GRAY,
                   stroke_width=2.5, max_tip_length_to_length_ratio=0.12)
        k1 = T("직접 작성", 10.5, GRAY).next_to(a1, UP, buff=0.05)
        k2 = T("채점", 10.5, GRAY).next_to(a2, DOWN, buff=0.05)
        self.play(FadeOut(lv), FadeOut(lu), FadeIn(st, shift=UP * 0.1), FadeIn(sh, shift=UP * 0.1), run_time=0.7)
        self.play(GrowArrow(a1), FadeIn(k1), run_time=0.6)
        self.play(GrowArrow(a2), FadeIn(k2), run_time=0.6)
        self.play(Indicate(loss[7], color=YEL, scale_factor=1.25),
                  ShowPassingFlash(box.copy().set_stroke(YEL, 4), time_width=0.5), run_time=1.0)

        # ---------- s3d: no guarantee ----------
        self.say("s3d")
        q = VGroup(T("손실 감소 보장", 18, FG, MEDIUM), T("?", 24, RED, BOLD)).arrange(RIGHT, buff=0.08)
        q.move_to([0, -0.3, 0])
        sub = T("실제로 MeanFlow 손실은 0으로 수렴하지 않음", 12, RED)
        fitw(sub, 4.1)
        sub.move_to([0, -0.78, 0])
        fn = T("출처 §2: sg가 손실 감소를 막을 수 있음", 10.5, GRAY)
        fitw(fn, 4.1)
        fn.move_to([0, -1.62, 0])
        self.play(FadeOut(VGroup(st, sh, a1, a2, k1, k2)), FadeIn(q, shift=UP * 0.1),
                  FadeIn(sub, shift=UP * 0.1), FadeIn(fn), run_time=0.6)
        self.play(Indicate(lk, color=RED, scale_factor=1.4), Indicate(loss[5], color=RED, scale_factor=1.25),
                  run_time=0.7)
        self.finish()
