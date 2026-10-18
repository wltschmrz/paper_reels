import json
import os
from pathlib import Path

from manim import *

from . import primitives as P
from . import theme as th

JOB = Path(os.environ.get("SS_JOB_DIR", "."))


class Reel(Scene):
    scene_id = None

    def setup(self):
        self.sb = json.loads((JOB / "storyboard.json").read_text())
        self.nar = json.loads((JOB / "narration.json").read_text())
        flags = self.sb.get("render", {})
        P.use_theme(flags.get("theme", "dark"), self.sb["language"])
        P.ONSCREEN.clear()
        self.C = P.C
        self.flags = flags
        self.camera.background_color = P.C["BG"]
        sid = self.scene_id or type(self).__name__
        self.sid = sid
        self.spec = next(s for s in self.sb["scenes"] if s["scene_id"] == sid)
        self.lines = {l["line_id"]: l for l in self.spec["lines"]}
        self.sub = None
        self.t_end = 0.0
        self.timeline = []
        self.overrun = 0.0

    def now(self):
        return self.renderer.time

    def scene_header(self):
        h = self.spec["header"]
        g = VGroup()
        if self.flags.get("term_header", True):
            a = P.fitw(P.T(h["definition"], 12.5, P.C["HDR"]), th.ZONES["max_width"]).move_to([0, th.ZONES["header_y"], 0])
            g.add(a)
        if self.flags.get("source_line", True):
            b = P.fitw(P.T(h["source"], 10, P.C["SRC"]), th.ZONES["max_width"])
            if len(g):
                b.next_to(g[0], DOWN, buff=0.08)
                if b.width < g[0].width:
                    b.align_to(g[0], RIGHT)
            else:
                b.move_to([0, th.ZONES["header_y"], 0])
            g.add(b)
        return g

    def dur(self, line_id):
        return self.nar["lines"][line_id]["duration_sec"]

    def say(self, line_id):
        if self.t_end > 0 and self.now() > self.t_end + 0.05:
            self.overrun += self.now() - self.t_end
        self.hold()
        ln = self.lines[line_id]
        self.add_sound(str(JOB / self.nar["lines"][line_id]["path"]))
        if self.sub is not None:
            self.remove(self.sub)
            self.sub = None
        if self.flags.get("subtitles", True):
            g = VGroup(*[P.T(l, th.SUBTITLE["size"]) for l in ln["subtitle"].split("\n")])
            g.arrange(DOWN, buff=th.SUBTITLE["line_gap"]).move_to([0, th.ZONES["subtitle_y"], 0])
            self.add(g)
            self.sub = g
        d = self.dur(line_id)
        self.timeline.append({"scene_id": self.sid, "line_id": line_id, "start": round(self.now(), 3),
                              "end": round(self.now() + d, 3), "subtitle": ln["subtitle"], "claims": ln.get("claims", [])})
        self.t_end = self.now() + d + th.GAP_SEC

    def hold(self):
        r = self.t_end - self.now()
        if r > 1 / 60:
            self.wait(r)

    def finish(self, extra=0.0):
        if self.now() > self.t_end + 0.05:
            self.overrun += self.now() - self.t_end
        self.hold()
        if extra > 0:
            self.wait(extra)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.3)
        out = JOB / "render"
        out.mkdir(exist_ok=True)
        (out / f"report_{self.sid}.json").write_text(json.dumps(
            {"scene_id": self.sid, "overrun_sec": round(self.overrun, 3), "duration_sec": round(self.now(), 3),
             "timeline": self.timeline, "onscreen_text": P.ONSCREEN}, ensure_ascii=False, indent=1))
