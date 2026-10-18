from manim import config

CANVAS = {"preview": (540, 960, 15), "final": (1080, 1920, 30)}
config.frame_height = 8.0
config.frame_width = 4.5

THEMES = {
    "dark": {"BG": "#000000", "FG": "#EFEFEF", "GRAY": "#8E8E8E", "MGRAY": "#5E5E5E", "DGRAY": "#383838",
             "YEL": "#FFE11A", "TEAL": "#4FB8CF", "RED": "#E5534B", "HDR": "#A3A3A3", "SRC": "#787878"},
    "light": {"BG": "#FAFAF7", "FG": "#151515", "GRAY": "#666666", "MGRAY": "#9A9A9A", "DGRAY": "#D6D6D6",
              "YEL": "#C99A00", "TEAL": "#1F7F99", "RED": "#C23B32", "HDR": "#555555", "SRC": "#808080"},
}

FONT = {"ko": "Noto Sans CJK KR", "en": "Noto Sans CJK KR"}

ZONES = {
    "header_y": 2.9,
    "visual_top": 2.45,
    "visual_bottom": -1.0,
    "footnote_y": -1.62,
    "subtitle_y": -2.3,
    "unsafe_below": -2.8,
    "max_width": 4.15,
}

SUBTITLE = {"size": 18, "line_gap": 0.12, "max_lines": 2, "max_units": 21.0, "hangul_unit": 1.0, "other_unit": 0.55}
GAP_SEC = 0.12
