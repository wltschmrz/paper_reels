from render_kit import *
from _shared import *


class S2(Reel):
    def construct(self):
        FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()
        h = self.scene_header()
        ax, frame = flow_frame()
        d0 = density(ax, -1, 0, 1, color=GRAY)
        d1 = density(ax, 1, 1, 0.6, color=TEAL)
        zs = np.linspace(-2.0, 2.0, 11)
        trs = VGroup(*[ParametricFunction(lambda t, z=z: ax.c2p(t, traj(t, z)), t_range=[0, 1],
                                          color=DGRAY, stroke_width=1.8) for z in zs])
        parts = VGroup(*[Dot(ax.c2p(0, z), radius=0.045, color=FG) for z in zs])

        self.say("s2a")
        self.play(FadeIn(h), FadeIn(frame), FadeIn(d0), FadeIn(parts), run_time=0.5)
        self.play(Create(trs), *[MoveAlongPath(p, tr) for p, tr in zip(parts, trs)], run_time=1.5)
        self.play(FadeIn(d1), parts.animate.set_color(TEAL), run_time=0.35)

        self.say("s2b")
        z0 = -1.0
        i0 = 2
        hl = trs[i0].copy().set_stroke(FG, 2.6)
        n = 14
        pts = [ax.c2p(i / n, traj(i / n, zs[i0])) for i in range(n + 1)]
        steps = VGroup(*[Arrow(pts[i], pts[i + 1], buff=0, stroke_width=2.4, color=YEL, tip_length=0.06,
                               max_tip_length_to_length_ratio=0.5) for i in range(n)])
        note = T("작은 화살표 × 수백 번", 12, YEL).move_to([ax.c2p(0.5, 0)[0], ax.c2p(0, 2.8)[1] + 0.2, 0])
        self.play(trs.animate.set_stroke(opacity=0.45), parts.animate.set_opacity(0.35), FadeIn(hl), run_time=0.35)
        self.play(LaggedStart(*[GrowArrow(s) for s in steps], lag_ratio=0.85), FadeIn(note), run_time=1.6, rate_func=linear)

        self.say("s2c")
        s, t = 0.22, 0.8
        x = zs[i0]
        P = ax.c2p(s, traj(s, x))
        Q = ax.c2p(t, traj(t, x))
        base = ax.c2p(0, -2.8)[1]
        vs = DashedLine([P[0], base, 0], P, color=MGRAY, stroke_width=1.5, dash_length=0.05)
        vt = DashedLine([Q[0], base, 0], Q, color=MGRAY, stroke_width=1.5, dash_length=0.05)
        ls = M("s", size=22, color=FG).move_to([P[0], base - 0.27, 0])
        lt = M("t", size=22, color=FG).move_to([Q[0], base - 0.27, 0])
        dp = Dot(P, radius=0.06, color=FG)
        dq = Dot(Q, radius=0.06, color=TEAL)
        lp = M("x_s", size=22).next_to(dp, DOWN + RIGHT * 0.4, buff=0.06)
        lq = M("x_t", size=22, color=TEAL).next_to(dq, DOWN + RIGHT * 0.3, buff=0.05)
        jp = CurvedArrow(P, Q, angle=-1.0, color=YEL, stroke_width=4, tip_length=0.13)
        eq = M(r"\Phi", r"(x_s,\,s,\,t)", "=", "x_t", size=32)
        eq[0].set_color(YEL)
        eq[3].set_color(TEAL)
        eq.move_to([0, 2.28, 0])
        self.play(FadeOut(steps), FadeOut(note), FadeIn(vs), FadeIn(vt), FadeIn(ls), FadeIn(lt), FadeIn(dp), FadeIn(lp), run_time=0.4)
        self.play(Create(jp), FadeIn(dq, scale=1.5), FadeIn(lq), FadeIn(eq, shift=DOWN * 0.1), run_time=0.9)
        P2 = ax.c2p(0, x)
        Q2 = ax.c2p(1, traj(1, x))
        jp2 = CurvedArrow(P2, Q2, angle=-1.3, color=YEL, stroke_width=3, tip_length=0.12)
        cap = T("s = 0, t = 1 이면 한 번에 생성", 12, YEL).move_to([0.05, -1.2, 0])
        self.play(Create(jp2), FadeIn(cap), run_time=0.9)
        self.finish()
