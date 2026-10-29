"""Calm synthesized music bed (same as the first test video). Usage: music.py <seconds> <out.wav> [seed]"""
import sys
import numpy as np, soundfile as sf
from scipy.signal import lfilter

SR = 48000


def make(dur, path, seed=7):
    n = int(SR * dur)
    t = np.arange(n) / SR
    mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
    # Fmaj7 - Am7 - Cmaj7 - G6, 4.8 s each
    chords = [[53, 57, 60, 64], [57, 60, 64, 67], [48, 55, 59, 64], [55, 59, 62, 64]]
    bass = [41, 45, 48, 43]
    L = 4.8
    out = np.zeros(n)
    rng = np.random.default_rng(seed)

    def env(length, a, r):
        e = np.ones(length)
        ai, ri = int(a * SR), int(r * SR)
        e[:ai] = np.linspace(0, 1, ai) ** 2
        e[-ri:] *= np.linspace(1, 0, ri) ** 2
        return e

    i = 0
    while i * L < dur:
        c = chords[i % 4]
        s0 = int(i * L * SR); seg = int((L + 1.6) * SR)
        s1 = min(n, s0 + seg); ln = s1 - s0
        tt = np.arange(ln) / SR
        e = env(seg, 1.4, 1.8)[:ln]
        pad = np.zeros(ln)
        for m in c:
            for det in (-0.06, 0.06):
                f = mtof(m + det)
                pad += np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)
        b = 0.9 * np.sin(2 * np.pi * mtof(bass[i % 4] - 12) * tt)
        out[s0:s1] += (pad * 0.06 + b * 0.12) * e
        for k in range(8):  # soft plucks every 0.6 s
            p0 = s0 + int(k * 0.6 * SR)
            if p0 >= n:
                break
            m = c[(k * 2 + i) % 4] + 12
            p1 = min(n, p0 + int(1.6 * SR)); tl = np.arange(p1 - p0) / SR
            f = mtof(m)
            out[p0:p1] += 0.05 * (np.sin(2 * np.pi * f * tl) + 0.3 * np.sin(4 * np.pi * f * tl)) * np.exp(-tl * 3.2) * np.minimum(1, tl / 0.01)
        i += 1

    a = 0.12  # gentle one-pole low-pass
    y = lfilter([a], [1, -(1 - a)], out)
    y *= 0.85 + 0.15 * np.sin(2 * np.pi * t / 9.6)
    fade = int(1.5 * SR); y[-fade:] *= np.linspace(1, 0, fade)
    y /= np.max(np.abs(y)) * 1.12
    st = np.stack([y, np.roll(y, int(0.011 * SR))], 1)
    sf.write(path, st, SR)


if __name__ == "__main__":
    make(float(sys.argv[1]), sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 7)
