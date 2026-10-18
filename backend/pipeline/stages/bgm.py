import numpy as np
import soundfile as sf
import scipy.signal as ss


def soft_pad(path, dur, sr=44100, seed=0):
    rng = np.random.default_rng(seed)
    n = int(sr * dur)
    t = np.arange(n) / sr
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    chords = [[57, 60, 64, 45], [53, 57, 60, 41], [48, 55, 60, 64], [55, 59, 62, 43]]
    seg, out = 4.0, np.zeros(n)
    for ci in range(int(dur / seg) + 2):
        st, en = ci * seg - 1.0, ci * seg + seg + 1.0
        i0, i1 = max(0, int(st * sr)), min(n, int(en * sr))
        if i0 >= i1:
            continue
        tt = t[i0:i1] - st
        env = np.clip(np.minimum(tt / 1.5, (en - st - tt) / 1.5), 0, 1) ** 1.5
        sig = np.zeros(i1 - i0)
        for m in chords[ci % 4]:
            f = hz(m)
            for d in (-0.15, 0.15):
                sig += 0.5 * np.sin(2 * np.pi * (f + d) * tt + rng.random() * 6.28)
            sig += 0.12 * np.sin(2 * np.pi * 2 * f * tt)
        out[i0:i1] += sig * env
    b, a = ss.butter(2, 1400 / (sr / 2))
    out = ss.lfilter(b, a, out) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.07 * t))
    out *= np.clip(np.minimum(t / 2.0, (dur - t) / 2.5), 0, 1)
    sf.write(path, (0.9 * out / np.max(np.abs(out))).astype(np.float32), sr)
