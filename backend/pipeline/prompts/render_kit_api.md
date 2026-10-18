from render_kit import *   (also re-exports everything from manim)

class Reel(Scene)
  self.scene_header() -> VGroup            header (term definition + source line) from the storyboard; FadeIn it in the first play
  self.say(line_id)                        starts the line's audio and subtitle; waits for the previous line to finish first
  self.dur(line_id) -> float               duration of a line in seconds
  self.finish(extra=0.0)                   waits for the last line, holds `extra` seconds, fades out, writes the render report
  self.C                                   dict of theme colors: BG FG GRAY MGRAY DGRAY YEL TEAL RED HDR SRC

T(text, size=14, color=None, weight=NORMAL) -> Text     all non-math text (Korean or English)
M(*tex_parts, size=28, color=None) -> MathTex           math; index parts to color terms, e.g. eq[2].set_color(YEL)
fitw(mobject, w=4.15) -> mobject                         shrink to fit width
legend(rows, at, size=10.5) -> VGroup                    rows = [("line"|"dashed"|"circle", color, label), ...]
card(title, body_lines, color, width=1.95, height=1.12, tag=None) -> VGroup
flow_frame(center=(-0.05, 0.6), xl=3.0, yl=2.4, yr=(-2.8, 2.8), labels=True) -> (Axes, VGroup)
    time-position frame: use ax.c2p(t, x); the returned VGroup holds the edge lines, time arrow and labels
density(ax, side, mean, std, k=0.9, color=None, yr=(-2.8, 2.8)) -> VGroup   side=-1 at t=0 (left), +1 at t=1 (right)
BarChart(values, labels, colors, ymax, x0=-1.42, dx=0.545, bw=0.36, y0=-0.75, height=2.35, fmt="{:.2f}")
    .base .bars .vals .labels, .x(i), .row(texts, colors, dy=-0.45)
ZONES                                    layout constants (header_y, visual_top, visual_bottom, footnote_y, subtitle_y, max_width)
