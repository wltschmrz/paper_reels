import numpy as np
from manim import *

from . import theme as th

C = dict(th.THEMES["dark"])
LANG = {"v": "ko"}
ONSCREEN = []


def use_theme(name, lang):
    C.clear()
    C.update(th.THEMES[name])
    LANG["v"] = lang


def T(s, size=14, color=None, weight=NORMAL):
    ONSCREEN.append(s)
    return Text(s, font=th.FONT[LANG["v"]], font_size=size, color=color or C["FG"], weight=weight)


def M(*s, size=28, color=None):
    ONSCREEN.append(" ".join(s))
    return MathTex(*s, font_size=size, color=color or C["FG"])


def fitw(m, w=None):
    w = w or th.ZONES["max_width"]
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


def legend(rows, at, size=10.5):
    g = VGroup()
    for kind, color, label in rows:
        if kind == "line":
            mark = Line(ORIGIN, RIGHT * 0.3, color=color, stroke_width=3)
        elif kind == "dashed":
            mark = DashedLine(ORIGIN, RIGHT * 0.3, color=color, stroke_width=3, dash_length=0.06)
        else:
            mark = Circle(radius=0.06, color=color, stroke_width=2.5)
        g.add(VGroup(mark, T(label, size, color)).arrange(RIGHT, buff=0.08))
    return g.arrange(DOWN, buff=0.05, aligned_edge=LEFT).move_to(at)


def card(title, body_lines, color, width=1.95, height=1.12, tag=None, title_size=15, body_size=12.5):
    box = RoundedRectangle(width=width, height=height, corner_radius=0.1, stroke_color=color, stroke_width=2)
    parts = VGroup()
    if tag:
        parts.add(T(tag, 11, C["GRAY"]))
    parts.add(VGroup(*[T(l, title_size, color, MEDIUM) for l in ([title] if isinstance(title, str) else title)]).arrange(DOWN, buff=0.05))
    for b in body_lines:
        parts.add(T(b, body_size, C["FG"]))
    parts.arrange(DOWN, buff=0.1).move_to(box)
    return VGroup(box, parts)


def flow_frame(center=(-0.05, 0.6), xl=3.0, yl=2.4, yr=(-2.8, 2.8), labels=True):
    ax = Axes(x_range=[0, 1, 1], y_range=[yr[0], yr[1], 1], x_length=xl, y_length=yl, tips=False)
    ax.move_to([center[0], center[1], 0])
    v0 = Line(ax.c2p(0, yr[0]), ax.c2p(0, yr[1]), color=C["DGRAY"], stroke_width=1.5)
    v1 = Line(ax.c2p(1, yr[0]), ax.c2p(1, yr[1]), color=C["DGRAY"], stroke_width=1.5)
    base = ax.c2p(0, yr[0])[1] - 0.1
    tax = Arrow([ax.c2p(0, 0)[0], base, 0], [ax.c2p(1, 0)[0] + 0.28, base, 0], buff=0, stroke_width=2,
                color=C["MGRAY"], tip_length=0.1, max_tip_length_to_length_ratio=0.1)
    g = VGroup(v0, v1, tax)
    if labels:
        g.add(T("t = 0", 10.5, C["GRAY"]).move_to([ax.c2p(0, 0)[0], base - 0.17, 0]))
        g.add(T("t = 1", 10.5, C["GRAY"]).move_to([ax.c2p(1, 0)[0], base - 0.17, 0]))
        g.add(T("시간" if LANG["v"] == "ko" else "time", 10, C["MGRAY"]).next_to(tax, RIGHT, buff=0.06))
    return ax, g


def npdf(y, m, s):
    return np.exp(-0.5 * ((y - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))


def density(ax, side, m, s, k=0.9, color=None, yr=(-2.8, 2.8)):
    color = color or C["GRAY"]
    ys = np.linspace(yr[0], yr[1], 140)
    t0 = 0 if side < 0 else 1
    pts = [ax.c2p(t0, y) + np.array([side * k * npdf(y, m, s), 0, 0]) for y in ys]
    curve = VMobject(stroke_color=color, stroke_width=1.5).set_points_smoothly(pts)
    fill = Polygon(ax.c2p(t0, ys[0]), *pts, ax.c2p(t0, ys[-1]), stroke_width=0, fill_color=color, fill_opacity=0.22)
    return VGroup(fill, curve)


class BarChart(VGroup):
    def __init__(self, values, labels, colors, ymax, x0=-1.42, dx=0.545, bw=0.36, y0=-0.75, height=2.35, fmt="{:.2f}",
                 label_size=11.5, value_size=11):
        super().__init__()
        self.base = Line([x0 - 0.3, y0, 0], [x0 + (len(values) - 1) * dx + 0.3, y0, 0], color=C["MGRAY"], stroke_width=2)
        self.bars, self.vals, self.labels = VGroup(), VGroup(), VGroup()
        for i, (v, lab, col) in enumerate(zip(values, labels, colors)):
            h = v / ymax * height
            b = Rectangle(width=bw, height=h, stroke_width=0, fill_color=col, fill_opacity=0.85).move_to([x0 + i * dx, y0 + h / 2, 0])
            self.bars.add(b)
            self.vals.add(T(fmt.format(v), value_size).next_to(b, UP, buff=0.06))
            self.labels.add(T(lab, label_size, C["GRAY"]).move_to([x0 + i * dx, y0 - 0.17, 0]))
        self.x0, self.dx, self.y0 = x0, dx, y0
        self.add(self.base, self.bars, self.vals, self.labels)

    def x(self, i):
        return self.x0 + i * self.dx

    def row(self, texts, colors, dy=-0.45, size=13):
        return VGroup(*[T(t, size, c).move_to([self.x(i), self.y0 + dy, 0]) for i, (t, c) in enumerate(zip(texts, colors))])
