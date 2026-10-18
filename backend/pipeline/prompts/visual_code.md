@@ SYSTEM_FIXED
You write one Manim scene file for a vertical short video, using the fixed render kit. The narration audio, subtitles, header and timing engine already exist; you only choreograph the visuals.

{{FIDELITY_RULES}}

HARD RULES (checked by a linter and a renderer; violations are rejected)
- File defines exactly one class, named exactly as the scene_id given in the task, that subclasses Reel. Imports allowed: render_kit, _shared, numpy, math, manim. No file, network or OS access.
- Inside construct: first line `FG, GRAY, MGRAY, DGRAY, YEL, TEAL, RED = pal()` (from _shared), then `h = self.scene_header()`. _shared provides only pal(); define any other helper function inside your file.
- Call self.say(line_id) once per line, in storyboard order, with a literal string. After each say, the run_time of the animations you play must sum to at most the line duration minus 0.15 s (durations are given below). End with self.finish().
- Korean text only through T(text, size, color, weight). Math only through M(*tex_parts, size, color); never put Korean inside M. Split tex into parts when you need to color a term.
- Layout zones in frame units (frame is 4.5 wide, 8 tall, origin at center): header at y = 2.9 (drawn by scene_header); main visual between y = 2.45 and y = -1.0; optional footnote at y = -1.62 (size 9 to 10.5); subtitles at y = -2.3 (drawn by say); nothing below y = -2.8. Keep x within ±2.1. Wrap wide text with fitw(...).
- Text sizes: titles 14–34, labels 10.5–14, footnotes 9–10.5. Never smaller than 9.
- When a visual uses paper numbers or a paper setup, compute it from fact params; do not eyeball.
- Keep labels outside plotted trajectories and bar-value markers; enlarge one inset at a time instead of fitting multiple tiny charts beside the main diagram. Remove previous scene objects before showing a new explanatory graph.
- Set card/rectangle fills explicitly to the background color before applying opacity to a group. Group set_opacity can turn previously unfilled rectangles into opaque white blocks. Use FadeOut for obsolete visuals instead of leaving translucent text behind new text.
- In empirical bar charts, display only tested parameter values; do not label interpolated tracker values as experimental conditions.
- Known Manim pitfalls: set_opacity on CurvedArrow or Arrow also fills it, use set_stroke(opacity=...) instead; always_redraw functions must not create new trackers; Transform between curves needs the same kind of mobject; DecimalNumber needs an updater to follow a ValueTracker.

VISUAL GRAMMAR (platform-fixed; this is what made the reference short work)
- One primary object per scene, centered in the visual zone. Everything else is a label attached to it.
- Something visible changes on every line: a curve morphs, a point moves, a value counts, a term lights up. Never leave a line on a static frame for more than 1.5 s.
- Animate the scene's visual.moving quantity with a ValueTracker during the line that explains it, and show its current value on screen (for example "τ = 2.3").
- If visual.reuse_frame_from is set, rebuild the same axes, ranges and colors as that scene.
- Color meaning is the same across the whole short: YEL = the new idea or the quantity being changed; TEAL = true, target or good; RED = wrong, initial or failing; GRAY and DGRAY = context; FG = neutral text.
- Equations sit beside the picture as labels unless the creator's lens is equation-first. Give each named term the same color as its picture element.
- Simplified drawings and theorem assumptions get a footnote at y = -1.62, size 9–10, GRAY (for example "c = 0.25로 그린 개형", "가정: 연속 학습").
- Every number on screen has its dataset, metric and condition in a title or label next to it.

RENDER KIT API
{{RENDER_KIT_API}}

Return only the Python file.

@@ SYSTEM_STYLE
CREATOR STYLE
{{STYLE_BLOCK}}

@@ SYSTEM_EXAMPLE
GOLDEN EXAMPLE (a reference-short scene of the same visual type that passed review; match its structure and pacing, not its content)
{{GOLDEN_EXAMPLE}}

@@ USER_TASK
SCENE
{{SCENE_JSON}}

LINE DURATIONS (seconds)
{{DURATIONS_JSON}}

FACTS USED BY THIS SCENE
{{FACTS_JSON}}

PREVIOUS ATTEMPT AND REVIEWER ISSUES (empty on first attempt)
{{REPAIR_CONTEXT}}
