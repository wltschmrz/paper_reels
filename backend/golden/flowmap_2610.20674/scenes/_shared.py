import numpy as np

from render_kit import C


def pal():
    return C["FG"], C["GRAY"], C["MGRAY"], C["DGRAY"], C["YEL"], C["TEAL"], C["RED"]


def sig(t):
    return np.sqrt((1 - t) ** 2 + 0.36 * t ** 2)


def traj(t, x):
    return t + sig(t) * x


def flow(y, a, b):
    return b + sig(b) / sig(a) * (y - a)


def U0(y, s, t):
    return 0.8 * np.cos(1.3 * y + 2 * s) - 0.2 * t
