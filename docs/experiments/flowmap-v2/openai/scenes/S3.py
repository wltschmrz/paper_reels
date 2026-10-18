from render_kit import *
from _shared import *
import numpy as np


class S3(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        h = VGroup(fitw(T('stop gradient: 값만 전달', 18, FG), 4.1).move_to([0,3.1,0]), T('Flow Map Training · §2', 13, GRAY).move_to([0,2.78,0]))

        stage = ValueTracker(0)

        def stage_badge():
            lab = T("단계", 12, FG)
            num = DecimalNumber(0, num_decimal_places=0, color=YEL, font_size=28)
            num.add_updater(lambda m: m.set_value(stage.get_value()).next_to(lab, RIGHT, buff=0.08))
            g = VGroup(lab, num)
            g.move_to([1.5, 2.08, 0])
            return g

        badge = stage_badge()

        sg_eq = M(r"\mathrm{sg}(", "z", ")", size=48).move_to([0, 1.0, 0])
        sg_eq[0].set_color(MGRAY)
        sg_eq[1].set_color(YEL)
        sg_eq[2].set_color(MGRAY)

        val_arrow = Arrow(
            sg_eq[1].get_bottom() + DOWN * 0.44,
            sg_eq[1].get_bottom() + DOWN * 0.06,
            buff=0,
            color=TEAL,
            stroke_width=4.5,
            tip_length=0.13,
        )
        val_lab = T("값은 사용", 13, TEAL).next_to(val_arrow, DOWN, buff=0.08)

        grad_arrow = CurvedArrow(
            sg_eq[1].get_top() + UP * 0.06 + LEFT * 0.06,
            sg_eq[1].get_top() + UP * 0.05 + RIGHT * 1.02,
            angle=-1.15,
            color=RED,
            stroke_width=3.6,
            tip_length=0.1,
        )
        grad_arrow.set_stroke(opacity=0.95)
        mid = grad_arrow.point_from_proportion(0.56)
        cut1 = Line(mid + UL * 0.085, mid + DR * 0.085).set_stroke(RED, 4.2)
        cut2 = Line(mid + UR * 0.085, mid + DL * 0.085).set_stroke(RED, 4.2)
        grad_cut = VGroup(cut1, cut2)
        grad_lab = T("안쪽 기울기 = 0", 13, RED).next_to(grad_arrow, UP, buff=0.35)

        target = M(
            r"u^{MF}_{\mathrm{tgt}}", "=",
            "v", "+", r"(t-s)", r"\big(",
            r"\nabla_x", "u", r"\,v", "+", r"\partial_s", "u", r"\big)",
            size=27
        )
        target[0].set_color(YEL)
        target[2].set_color(TEAL)
        target[7].set_color(TEAL)
        target[11].set_color(TEAL)
        fitw(target, 4.05).move_to([0, 1.28, 0])

        u_left = M("u", size=38, color=TEAL).move_to([-1.55, 0.35, 0])

        sg_wrap = M(r"\mathrm{sg}\!\left(", r"u^{MF}_{\mathrm{tgt}}", r"\right)", size=33)
        sg_wrap[0].set_color(MGRAY)
        sg_wrap[1].set_color(YEL)
        sg_wrap[2].set_color(MGRAY)
        sg_wrap.move_to([0.72, 0.34, 0])

        reg_arrow = Arrow(
            u_left.get_right() + RIGHT * 0.1,
            sg_wrap.get_left() + LEFT * 0.1,
            buff=0,
            color=TEAL,
            stroke_width=4,
            tip_length=0.13,
        )
        reg_lab = T("자기 타깃으로 회귀", 13, TEAL).next_to(reg_arrow, DOWN, buff=0.1)

        mirror_card = card(
            "비유",
            ["정답지는 보이지만", "안쪽엔 손 못 댐"],
            YEL,
            width=2.35,
            height=1.12,
            body_size=14.5,
            tag=None,
        ).move_to([0.95, -0.78, 0])
        map_txt = T("거울 = sg 타깃", 14, FG).next_to(mirror_card, DOWN, buff=0.1)

        loss_ax = Axes(
            x_range=[0, 1, 1],
            y_range=[0, 1, 1],
            x_length=2.2,
            y_length=1.15,
            axis_config={"include_ticks": False, "stroke_color": DGRAY, "stroke_width": 2.2},
            tips=False,
        ).move_to([0, -0.52, 0])
        loss_curve = loss_ax.plot(
            lambda x: 0.62 - 0.23 * x + 0.06 * np.sin(8 * x),
            x_range=[0, 1],
            color=RED,
            stroke_width=3.4,
        )
        zero_line = Line(loss_ax.c2p(0, 0), loss_ax.c2p(1, 0)).set_stroke(GRAY, 2.2)
        loss_t = M(r"\mathcal{L}", size=24, color=FG).next_to(loss_ax, LEFT, buff=0.1)
        zero_t = T("0", 12, GRAY).next_to(loss_ax.c2p(0, 0), LEFT, buff=0.08)
        no_dec = T("꼭 감소 아님", 13, RED).next_to(loss_ax, UP, buff=0.05)
        no_zero = T("0으로 수렴 아님", 13, RED).next_to(loss_ax, DOWN, buff=0.06)

        foot = T("개념도 · 감소와 0 수렴은 보장되지 않음", 12.5, GRAY).move_to([0, -1.62, 0])

        self.say("s3a")
        self.play(FadeIn(h), FadeIn(badge), Write(sg_eq), run_time=0.5)
        self.play(Create(val_arrow), FadeIn(val_lab), run_time=0.35)
        self.play(Create(grad_arrow), FadeIn(grad_cut), FadeIn(grad_lab), stage.animate.set_value(1), run_time=0.55)

        self.say("s3b")
        self.play(
            FadeOut(val_arrow), FadeOut(val_lab),
            FadeOut(grad_arrow), FadeOut(grad_cut), FadeOut(grad_lab),
            sg_eq.animate.scale(0.68).move_to([0, 2.0, 0]),
            Write(target),
            stage.animate.set_value(2),
            run_time=0.9,
        )
        self.play(
            FadeIn(u_left),
            FadeIn(sg_wrap),
            Create(reg_arrow),
            FadeIn(reg_lab),
            run_time=1.05,
        )

        self.say("s3c")
        self.play(
            FadeIn(mirror_card, shift=LEFT * 0.08),
            FadeIn(map_txt),
            stage.animate.set_value(3),
            run_time=0.8,
        )
        box1 = SurroundingRectangle(sg_wrap, color=YEL, buff=0.08, corner_radius=0.08)
        box2 = SurroundingRectangle(mirror_card[1], color=YEL, buff=0.06, corner_radius=0.06)
        self.play(
            Create(box1),
            Create(box2),
            Indicate(sg_wrap[1], color=YEL, scale_factor=1.08),
            run_time=0.95,
        )
        self.play(
            FadeOut(box1),
            FadeOut(box2),
            ShowPassingFlash(reg_arrow.copy().set_stroke(YEL, 4), time_width=0.6),
            run_time=0.7,
        )

        self.say("s3d")
        self.play(
            FadeOut(target),
            FadeOut(sg_wrap),
            FadeOut(reg_arrow),
            FadeOut(reg_lab),
            FadeOut(mirror_card),
            FadeOut(map_txt),
            FadeOut(u_left), FadeOut(sg_eq),
            FadeIn(loss_ax),
            Create(zero_line),
            Create(loss_curve),
            FadeIn(loss_t), FadeIn(zero_t),
            run_time=1.0,
        )
        self.play(
            FadeIn(no_dec),
            FadeIn(no_zero),
            FadeIn(foot),
            Indicate(loss_curve, color=RED, scale_factor=1.02),
            run_time=1.05,
        )

        self.finish()