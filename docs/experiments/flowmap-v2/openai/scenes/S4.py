from render_kit import *
from _shared import *
import numpy as np
import math


class S4(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        h = VGroup(fitw(T('연속 학습에서는 왜 수렴할까', 18, FG), 4.1).move_to([0,3.1,0]), T('Theorem 1 · Eq. 13–15', 13, GRAY).move_to([0,2.78,0]))

        def sig(t):
            return math.sqrt((1 - t) ** 2 + 0.36 * (t ** 2))

        def true_pos(x, t):
            return t + sig(t) * x

        def true_flow(x, a, b):
            return b + sig(b) / sig(a) * (x - a)

        def u0(x, s):
            return 0.8 * math.cos(1.3 * x + 2 * s) - 0.2 * s

        def integrate_u0(x_start, a, b, n=150):
            ts = np.linspace(a, b, n)
            xs = [x_start]
            x = x_start
            for i in range(n - 1):
                ti = float(ts[i])
                dt = float(ts[i + 1] - ts[i])
                x = x + dt * u0(x, ti) * dt / dt
                x = xs[-1] + dt * u0(xs[-1], ti)
                xs.append(x)
            return ts, np.array(xs)

        def curve_from(ax, ts, xs, color, sw=3.6):
            pts = [ax.c2p(float(t), float(x)) for t, x in zip(ts, xs)]
            return VMobject(stroke_color=color, stroke_width=sw).set_points_smoothly(pts)

        def gauss_side(ax, side, mu, sd, color):
            yv = np.linspace(-4, 5, 220)
            pdf = np.exp(-0.5 * ((yv - mu) / sd) ** 2)
            pdf = pdf / pdf.max()
            edge = 0 if side < 0 else 1
            sgn = -1 if side < 0 else 1
            pts = [ax.c2p(edge + sgn * 0.12 * float(v), float(y)) for y, v in zip(yv, pdf)]
            spine = [ax.c2p(edge, float(y)) for y in yv[::-1]]
            poly = Polygon(*(pts + spine), stroke_width=0, fill_color=color, fill_opacity=0.18)
            rim = VMobject(stroke_color=color, stroke_width=1.8).set_points_smoothly(pts)
            return VGroup(poly, rim)

        def tau_to_cut(tv):
            return 1 - math.exp(-tv)

        def mf_path(x0, cut, n=210):
            ts_left = np.linspace(0, cut, max(2, int(n * max(cut, 0.08))))
            xs_left = np.array([true_pos(x0, float(t)) for t in ts_left])
            x_cut = true_flow(x0, 0, cut)
            if cut >= 1 - 1e-8:
                return ts_left, xs_left
            ts_right, xs_right = integrate_u0(x_cut, cut, 1, n=max(3, n - len(ts_left) + 2))
            return np.concatenate([ts_left, ts_right[1:]]), np.concatenate([xs_left, xs_right[1:]])

        def lag_path(x0, scut, n=210):
            if scut <= 1e-8:
                ts = np.linspace(0, 1, n)
                xs = np.array([true_flow(x0, 0, float(t)) for t in ts])
                return ts, xs
            ts_left, xs_left = integrate_u0(x0, 0, scut, n=max(3, int(n * max(scut, 0.08))))
            x_cut = float(xs_left[-1])
            ts_right = np.linspace(scut, 1, max(3, n - len(ts_left) + 2))
            xs_right = np.array([true_flow(x_cut, scut, float(t)) for t in ts_right])
            return np.concatenate([ts_left, ts_right[1:]]), np.concatenate([xs_left, xs_right[1:]])

        ax, frame = flow_frame(center=(-0.58, 0.64), xl=2.45, yl=2.3, yr=(-4, 5), labels=True)
        left_den = gauss_side(ax, -1, 0, 1, MGRAY)
        right_den = gauss_side(ax, 1, 1, 0.6, MGRAY)

        x0 = -0.9
        ts_full = np.linspace(0, 1, 220)
        xs_true = np.array([true_pos(x0, float(t)) for t in ts_full])
        t_init, x_init = integrate_u0(x0, 0, 1, n=220)

        true_cv = curve_from(ax, ts_full, xs_true, TEAL, sw=3.7)
        init_cv = curve_from(ax, t_init, x_init, RED, sw=2.7)

        tau = ValueTracker(0.0)

        tau_num = DecimalNumber(0, num_decimal_places=1, font_size=24, color=YEL)
        tau_num.add_updater(lambda m: m.set_value(tau.get_value()))
        tau_lab = VGroup(M(r"\tau =", size=22, color=FG), tau_num).arrange(RIGHT, buff=0.06)
        tau_lab.move_to([1.4, 1.93, 0])

        setup_tag = T("Appendix C.1 Gaussian toy", 10.5, GRAY).move_to([-0.92, 1.92, 0])

        mf_title = T("MeanFlow", 12.5, YEL, weight=BOLD).move_to([1.38, 1.52, 0])
        mf_rule = VGroup(
            T("앞 구간", 10.5, FG),
            M(r"\Phi^\star", size=17, color=TEAL),
            T("뒤 구간", 10.5, FG),
            M(r"\Phi_0", size=17, color=RED),
        ).arrange(RIGHT, buff=0.08).move_to([1.38, 1.22, 0])

        lag_box = RoundedRectangle(
            width=1.5, height=1.04, corner_radius=0.08, stroke_color=MGRAY, stroke_width=1.4
        ).move_to([1.38, 0.33, 0])
        lag_title = T("Lagrangian 비교", 10.5, GRAY).move_to([1.38, 0.77, 0])
        lag_rule = VGroup(
            T("앞", 10, FG),
            M(r"\Phi_0", size=15, color=RED),
            T("뒤", 10, FG),
            M(r"\Phi^\star", size=15, color=TEAL),
        ).arrange(RIGHT, buff=0.07).move_to([1.38, 0.55, 0])

        lag_ax = Axes(
            x_range=[0, 1, 1],
            y_range=[-2.2, 2.7, 1],
            x_length=1.08,
            y_length=0.54,
            tips=False,
            axis_config={"color": DGRAY, "stroke_width": 1.2, "include_ticks": False},
        ).move_to([1.38, 0.15, 0])

        def lag_curve(ts, xs, color, sw):
            pts = [lag_ax.c2p(float(t), float(x)) for t, x in zip(ts, xs)]
            return VMobject(stroke_color=color, stroke_width=sw).set_points_smoothly(pts)

        lag_true = lag_curve(ts_full, xs_true, TEAL, 1.8)
        lag_init = lag_curve(t_init, x_init, RED, 1.5)

        err_box = RoundedRectangle(
            width=1.5, height=1.08, corner_radius=0.08, stroke_color=MGRAY, stroke_width=1.4
        ).move_to([1.38, -0.63, 0])
        err_tag = T("Eq. (15) MeanFlow 오차 상계", 9.6, GRAY).move_to([1.38, -0.18, 0])

        err_ax = Axes(
            x_range=[0, 4.5, 1.5],
            y_range=[0, 1.05, 0.5],
            x_length=1.08,
            y_length=0.5,
            tips=False,
            axis_config={"color": DGRAY, "stroke_width": 1.2, "include_ticks": False},
        ).move_to([1.38, -0.63, 0])

        err_curve = VMobject(stroke_color=YEL, stroke_width=2.2).set_points_smoothly(
            [err_ax.c2p(t, math.exp(-t)) for t in np.linspace(0, 4.5, 100)]
        )
        err_dot = always_redraw(
            lambda: Dot(err_ax.c2p(tau.get_value(), math.exp(-tau.get_value())), radius=0.03, color=YEL)
        )

        err_eq = M(r"\|\Phi^{MF}_{\tau}-\Phi^\star\|_\infty", r"\le", r"2Me^{-\rho_{\min}\tau}", size=12, color=FG)
        err_eq[0].set_color(YEL)
        err_eq[2].set_color(YEL)
        fitw(err_eq, 1.36).move_to([1.38, -0.96, 0])

        foot = T(
            "가정: functional gradient flow · Gaussian 예시",
            12,
            GRAY,
        ).move_to([0, -1.62, 0])
        fitw(foot, 4.08)

        lg = legend(
            [
                ("line", TEAL, "true flow"),
                ("line", RED, "initial map"),
                ("line", YEL, "learned map"),
            ],
            at=[-0.35, -1.0, 0],
            size=9.8,
        )

        def build_mf():
            cut = tau_to_cut(tau.get_value())
            ts, xs = mf_path(x0, cut)
            return curve_from(ax, ts, xs, YEL, sw=4.4)

        def build_mf_true_seg():
            cut = tau_to_cut(tau.get_value())
            ts = np.linspace(0, cut, 120)
            xs = np.array([true_pos(x0, float(t)) for t in ts])
            return curve_from(ax, ts, xs, YEL, sw=4.4)

        def build_mf_dot():
            cut = tau_to_cut(tau.get_value())
            return Dot(ax.c2p(cut, true_flow(x0, 0, cut)), radius=0.046, color=YEL)

        def build_lag():
            cut = tau_to_cut(tau.get_value())
            scut = 1 - cut
            ts, xs = lag_path(x0, scut)
            return lag_curve(ts, xs, YEL, 2.5)

        def build_lag_dot():
            cut = tau_to_cut(tau.get_value())
            scut = 1 - cut
            _, xs_left = integrate_u0(x0, 0, max(scut, 1e-4), n=100)
            x_cut = x0 if scut <= 1e-8 else float(xs_left[-1])
            return Dot(lag_ax.c2p(scut, x_cut), radius=0.028, color=YEL)

        lag_group = VGroup(lag_box, lag_title, lag_rule, lag_ax, lag_true, lag_init)
        lag_group.scale(2.2).move_to([0, 0.55, 0])
        err_group = VGroup(err_box, err_tag, err_ax, err_curve, err_eq)
        err_group.scale(2.2).move_to([0, 0.55, 0])
        err_eq.move_to([0,-1.07,0])
        err_tag.become(T("MeanFlow 오차 상계 · Eq. 15",16,FG).move_to([0,1.55,0]))

        mf_cv = always_redraw(build_mf)
        mf_front = always_redraw(build_mf_true_seg)
        mf_dot = always_redraw(build_mf_dot)
        lag_cv = always_redraw(build_lag)
        lag_dot = always_redraw(build_lag_dot)

        converge_note = T("정리 1: 점별 수렴", 13, FG).move_to([0.7, -1.37, 0])
        fitw(converge_note, 2.85)

        self.say("s4a")
        self.play(
            FadeIn(h),
            FadeIn(frame),
            FadeIn(left_den),
            FadeIn(right_den),
            Create(true_cv),
            Create(init_cv),
            FadeIn(setup_tag),
            FadeIn(tau_lab),
            FadeIn(lg),
            FadeIn(foot),
            FadeIn(converge_note),
            run_time=0.95,
        )
        self.play(
            Create(mf_cv),
            FadeIn(mf_dot),
            tau.animate.set_value(0.8),
            run_time=1.65,
            rate_func=smooth,
        )

        self.say("s4b")
        self.play(
            FadeIn(mf_title),
            FadeIn(mf_rule),
            Indicate(mf_rule[1], color=TEAL, scale_factor=1.08),
            tau.animate.set_value(2.3),
            run_time=1.95,
            rate_func=smooth,
        )

        self.say("s4c")
        self.play(FadeOut(VGroup(frame,left_den,right_den,true_cv,init_cv,mf_cv,mf_dot,mf_title,mf_rule,setup_tag,lg)), run_time=0.25)
        self.play(
            FadeIn(lag_box),
            FadeIn(lag_title),
            FadeIn(lag_rule),
            Create(lag_ax),
            Create(lag_true),
            Create(lag_init),
            Create(lag_cv),
            FadeIn(lag_dot),
            tau.animate.set_value(3.5),
            run_time=1.82,
            rate_func=smooth,
        )

        self.say("s4d")
        self.play(FadeOut(VGroup(lag_box,lag_title,lag_rule,lag_ax,lag_true,lag_init,lag_cv,lag_dot)), run_time=0.25)
        self.play(
            FadeIn(err_box),
            FadeIn(err_tag),
            Create(err_ax),
            Create(err_curve),
            FadeIn(err_eq),
            tau.animate.set_value(4.5),
            run_time=2.02,
            rate_func=smooth,
        )

        self.finish()