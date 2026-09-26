# -*- coding: utf-8 -*-
"""figures.py — every picture on the site, drawn from the equation that makes it.

Nothing here is a stock image or a sketch. Each figure is a small computation — a map
iterated, a differential equation stepped, a million coin tosses averaged — and then
turned into an SVG by the little plotting kit at the top. Run this file on its own to
print the numbers it found:

    python3 tools/figures.py

The same numbers land in build/facts.json, and the site quotes them from there, so the
copy can never drift from the arithmetic.
"""
from __future__ import annotations

import base64
import io
import json
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image

# ---- the palette, matched to the stylesheet so the plots sit in the same dark
INK = "#f3efe6"; MUTE = "#b3ac9e"; LINE = "#2a2a38"; GRID = "#1c1c28"
HOT = "#ffb347"; BLUE = "#8fd0ff"; RED = "#ff6a5e"; GOLD = "#ffd27a"; VIOLET = "#c8a6ff"; GREEN = "#8fe0a8"


# ====================================================================== the plotting kit
class Plot:
    """A framed set of axes in an SVG. Data coordinates go in; pixels come out. The frame,
    the ticks and the labels are drawn once; then you add lines, dots and rules on top."""

    def __init__(self, w=920, h=560, pad=(64, 26, 52, 66), xlim=(0, 1), ylim=(0, 1),
                 xlabel="", ylabel="", title="", xticks=None, yticks=None,
                 xfmt=None, yfmt=None, logy=False):
        self.w, self.h = w, h
        self.l, self.t, self.b, self.rp = pad  # left, top, bottom, right padding
        self.x0, self.x1 = xlim
        self.logy = logy
        self.y0, self.y1 = (math.log10(ylim[0]), math.log10(ylim[1])) if logy else ylim
        self.xlabel, self.ylabel, self.title = xlabel, ylabel, title
        self.xticks, self.yticks = xticks, yticks
        self.xfmt = xfmt or (lambda v: f"{v:g}")
        self.yfmt = yfmt or (lambda v: f"{v:g}")
        self.body = []
        self.ix0, self.ix1 = self.l, self.w - self.rp
        self.iy0, self.iy1 = self.h - self.b, self.t  # y grows downward

    def px(self, x):
        return self.ix0 + (x - self.x0) / (self.x1 - self.x0) * (self.ix1 - self.ix0)

    def py(self, y):
        yv = math.log10(y) if self.logy else y
        return self.iy0 + (yv - self.y0) / (self.y1 - self.y0) * (self.iy1 - self.iy0)

    def _n(self, v):  # short number for path data
        return f"{v:.2f}".rstrip("0").rstrip(".")

    def polyline(self, pts, stroke=HOT, w=2.0, opacity=1.0, dash=""):
        d = " ".join(f"{self._n(self.px(x))},{self._n(self.py(y))}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.body.append(f'<polyline points="{d}" fill="none" stroke="{stroke}" '
                          f'stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round" '
                          f'opacity="{opacity}"{da}/>')

    def dots(self, pts, fill=HOT, r=1.0, opacity=1.0):
        # drawn as a single path of tiny squares — thousands of points stay one element
        seg = []
        for x, y in pts:
            X, Y = self.px(x), self.py(y)
            seg.append(f"M{self._n(X-r)},{self._n(Y)}h{self._n(2*r)}")
        self.body.append(f'<path d="{"".join(seg)}" stroke="{fill}" stroke-width="{2*r}" '
                         f'opacity="{opacity}"/>')

    def raster_path(self, pts, rgb=(255, 179, 71), scale=2.0, width=1, alpha=210):
        """A long, dense curve drawn once into a small anti-aliased PNG over the plot area —
        the Lorenz butterfly is thousands of segments, and a raster keeps the page light."""
        from PIL import ImageDraw
        iw = int(round((self.ix1 - self.ix0) * scale))
        ih = int(round((self.iy0 - self.iy1) * scale))
        im = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        xy = []
        for x, y in pts:
            X = (x - self.x0) / (self.x1 - self.x0) * (iw - 1)
            yy = math.log10(y) if self.logy else y
            Y = ih - 1 - (yy - self.y0) / (self.y1 - self.y0) * (ih - 1)
            xy.append((X, Y))
        dr.line(xy, fill=(rgb[0], rgb[1], rgb[2], alpha), width=max(1, int(width * scale)), joint="curve")
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        self.body.append(
            f'<image x="{self.ix0}" y="{self.iy1}" width="{self.ix1-self.ix0}" '
            f'height="{self.iy0-self.iy1}" preserveAspectRatio="none" '
            f'href="data:image/png;base64,{b64}"/>')

    def raster_scatter(self, xs, ys, rgb=(255, 179, 71), scale=1.6, gain=90):
        """A dense point cloud drawn once into a small PNG, embedded exactly over the plot
        area. The axes and labels stay crisp SVG; only the hundred thousand points become a
        raster, so a bifurcation figure is tens of kilobytes instead of megabytes. Brighter
        where points pile up."""
        iw = int(round((self.ix1 - self.ix0) * scale))
        ih = int(round((self.iy0 - self.iy1) * scale))
        xs = np.asarray(xs, dtype=float)
        ys = np.asarray(ys, dtype=float)
        px = ((xs - self.x0) / (self.x1 - self.x0) * (iw - 1)).astype(np.int64)
        if self.logy:
            ys = np.log10(np.clip(ys, 1e-300, None))
        py = ((ys - self.y0) / (self.y1 - self.y0) * (ih - 1))
        py = (ih - 1 - py).astype(np.int64)  # image y grows downward
        keep = (px >= 0) & (px < iw) & (py >= 0) & (py < ih)
        flat = py[keep] * iw + px[keep]
        counts = np.bincount(flat, minlength=iw * ih).reshape(ih, iw)
        alpha = np.clip(counts.astype(np.float64) * gain, 0, 255).astype(np.uint8)
        img = np.zeros((ih, iw, 4), dtype=np.uint8)
        img[..., 0] = rgb[0]; img[..., 1] = rgb[1]; img[..., 2] = rgb[2]
        img[..., 3] = alpha
        buf = io.BytesIO()
        Image.fromarray(img, "RGBA").save(buf, format="PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        self.body.append(
            f'<image x="{self.ix0}" y="{self.iy1}" width="{self.ix1-self.ix0}" '
            f'height="{self.iy0-self.iy1}" preserveAspectRatio="none" '
            f'image-rendering="pixelated" href="data:image/png;base64,{b64}"/>')

    def circle(self, x, y, r=3.5, fill=HOT, stroke="none", sw=0):
        self.body.append(f'<circle cx="{self._n(self.px(x))}" cy="{self._n(self.py(y))}" '
                         f'r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def hline(self, y, stroke=MUTE, w=1.2, dash="5 5", opacity=1.0):
        Y = self._n(self.py(y))
        self.body.append(f'<line x1="{self.ix0}" y1="{Y}" x2="{self.ix1}" y2="{Y}" '
                         f'stroke="{stroke}" stroke-width="{w}" stroke-dasharray="{dash}" opacity="{opacity}"/>')

    def vline(self, x, stroke=MUTE, w=1.2, dash="5 5", opacity=1.0):
        X = self._n(self.px(x))
        self.body.append(f'<line x1="{X}" y1="{self.iy1}" x2="{X}" y2="{self.iy0}" '
                         f'stroke="{stroke}" stroke-width="{w}" stroke-dasharray="{dash}" opacity="{opacity}"/>')

    def rect(self, x, y, w, h, fill=HOT, opacity=1.0):
        X, Y = self.px(x), self.py(y + h)
        W, H = self.px(x + w) - X, self.py(y) - self.py(y + h)
        self.body.append(f'<rect x="{self._n(X)}" y="{self._n(Y)}" width="{self._n(W)}" '
                         f'height="{self._n(H)}" fill="{fill}" opacity="{opacity}"/>')

    def text(self, x, y, s, fill=INK, size=15, anchor="middle", px=False, weight="400", italic=False):
        X, Y = (x, y) if px else (self.px(x), self.py(y))
        it = ' font-style="italic"' if italic else ""
        self.body.append(f'<text x="{self._n(X)}" y="{self._n(Y)}" fill="{fill}" '
                         f'font-size="{size}" text-anchor="{anchor}" font-weight="{weight}"{it} '
                         f'font-family="Avenir Next,system-ui,sans-serif">{s}</text>')

    def label(self, x, y, s, fill=HOT, size=15, anchor="start", dx=6, dy=-6, weight="700"):
        self.text(self.px(x) + dx, self.py(y) + dy, s, fill=fill, size=size, anchor=anchor, px=True, weight=weight)

    def _ticks(self, lo, hi, n=5):
        if self.logy is False:
            step = _nice((hi - lo) / n)
            start = math.ceil(lo / step) * step
            out, v = [], start
            while v <= hi + step * 1e-9:
                out.append(round(v, 10)); v += step
            return out
        decs = range(int(math.floor(lo)), int(math.ceil(hi)) + 1)
        return [10 ** d for d in decs]

    def frame(self):
        pre = []
        pre.append(f'<rect x="{self.ix0}" y="{self.iy1}" width="{self.ix1-self.ix0}" '
                   f'height="{self.iy0-self.iy1}" fill="#050507"/>')
        # gridlines + ticks
        xs = self.xticks if self.xticks is not None else self._ticks(self.x0, self.x1)
        for xv in xs:
            if xv < self.x0 - 1e-9 or xv > self.x1 + 1e-9:
                continue
            X = self._n(self.px(xv))
            pre.append(f'<line x1="{X}" y1="{self.iy1}" x2="{X}" y2="{self.iy0}" stroke="{GRID}" stroke-width="1"/>')
            pre.append(f'<line x1="{X}" y1="{self.iy0}" x2="{X}" y2="{self.iy0+5}" stroke="{MUTE}" stroke-width="1"/>')
            pre.append(f'<text x="{X}" y="{self.iy0+20}" fill="{MUTE}" font-size="13" text-anchor="middle" '
                       f'font-family="Avenir Next,system-ui,sans-serif">{self.xfmt(xv)}</text>')
        if self.logy:
            ys = self.yticks if self.yticks is not None else self._ticks(self.y0, self.y1)
        else:
            ys = self.yticks if self.yticks is not None else self._ticks(self.y0, self.y1)
        for yv in ys:
            Y = self._n(self.py(yv))
            pre.append(f'<line x1="{self.ix0}" y1="{Y}" x2="{self.ix1}" y2="{Y}" stroke="{GRID}" stroke-width="1"/>')
            pre.append(f'<line x1="{self.ix0-5}" y1="{Y}" x2="{self.ix0}" y2="{Y}" stroke="{MUTE}" stroke-width="1"/>')
            pre.append(f'<text x="{self.ix0-9}" y="{float(Y)+4:.1f}" fill="{MUTE}" font-size="13" text-anchor="end" '
                       f'font-family="Avenir Next,system-ui,sans-serif">{self.yfmt(yv)}</text>')
        # frame border
        pre.append(f'<rect x="{self.ix0}" y="{self.iy1}" width="{self.ix1-self.ix0}" '
                   f'height="{self.iy0-self.iy1}" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
        # axis titles
        if self.xlabel:
            pre.append(f'<text x="{(self.ix0+self.ix1)/2}" y="{self.h-14}" fill="{INK}" font-size="15" '
                       f'text-anchor="middle" font-family="Avenir Next,system-ui,sans-serif">{self.xlabel}</text>')
        if self.ylabel:
            cy = (self.iy0 + self.iy1) / 2
            pre.append(f'<text x="18" y="{cy}" fill="{INK}" font-size="15" text-anchor="middle" '
                       f'font-family="Avenir Next,system-ui,sans-serif" transform="rotate(-90 18 {cy})">{self.ylabel}</text>')
        if self.title:
            pre.append(f'<text x="{self.ix0}" y="{self.iy1-9}" fill="{INK}" font-size="15" text-anchor="start" '
                       f'font-weight="700" font-family="Avenir Next,system-ui,sans-serif">{self.title}</text>')
        return pre

    def svg(self):
        parts = [f'<svg viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg" '
                 f'role="img" preserveAspectRatio="xMidYMid meet" style="background:#050507">']
        parts += self.frame()
        parts += self.body
        parts.append("</svg>")
        return "".join(parts)


def _nice(x):
    """A round-ish step near x: 1, 2, 2.5 or 5 times a power of ten."""
    if x <= 0:
        return 1
    e = math.floor(math.log10(x))
    f = x / 10 ** e
    nf = 1 if f < 1.5 else 2 if f < 3 else 2.5 if f < 4 else 5 if f < 7 else 10
    return nf * 10 ** e


# ====================================================================== the mathematics
def logistic_series(r, x0, n):
    xs, x = [x0], x0
    for _ in range(n):
        x = r * x * (1 - x)
        xs.append(x)
    return xs


def period_of(r, settle=2000, keep=600, tol=1.5e-4):
    """Iterate the logistic map until it settles, then find the length of the cycle it
    fell into: 1 (a fixed point), 2, 4 … or 0 for none found up to 64 (chaos)."""
    x = 0.5
    for _ in range(settle):
        x = r * x * (1 - x)
    tail = []
    for _ in range(keep):
        x = r * x * (1 - x)
        tail.append(x)
    x0 = tail[-1]
    for p in (1, 2, 3, 4, 5, 6, 8, 12, 16, 24, 32, 48, 64):
        if all(abs(tail[-1 - k * p] - x0) < tol for k in range(1, min(4, keep // p))):
            # confirm it is not a shorter period masquerading
            if abs(tail[-1 - p] - x0) < tol:
                return p
    return 0


def find_doublings():
    """Walk r upward and record where the period first doubles 1→2→4→8→16, refining each
    threshold by bisection. From the spacings comes an estimate of Feigenbaum's number."""
    targets = [1, 2, 4, 8, 16]
    thresh = {}
    prev_r, prev_p = 2.6, 1
    r = 2.6
    while r < 3.5700 and len(thresh) < 4:
        p = period_of(r)
        if p in targets and prev_p in targets and p == prev_p * 2 and (prev_p, p) not in thresh:
            lo, hi = prev_r, r
            for _ in range(40):
                mid = (lo + hi) / 2
                if period_of(mid) >= p:
                    hi = mid
                else:
                    lo = mid
            thresh[(prev_p, p)] = hi
            prev_p = p
        elif p in (1, 2, 4, 8, 16, 32):
            prev_p = p
        prev_r = r
        r += 0.0006
    rs = [thresh.get((1, 2)), thresh.get((2, 4)), thresh.get((4, 8)), thresh.get((8, 16))]
    rs = [v for v in rs if v]
    deltas = []
    for i in range(1, len(rs) - 1):
        deltas.append((rs[i] - rs[i - 1]) / (rs[i + 1] - rs[i]))
    return rs, deltas


def _lz(st, s, rho, beta):
    x, y, z = st
    return (s * (y - x), x * (rho - z) - y, x * y - beta * z)


def _step(st, dt, s, rho, beta):
    """One Runge–Kutta 4 step of the Lorenz system."""
    def add(a, b, k):
        return (a[0] + k * b[0], a[1] + k * b[1], a[2] + k * b[2])
    k1 = _lz(st, s, rho, beta)
    k2 = _lz(add(st, k1, dt / 2), s, rho, beta)
    k3 = _lz(add(st, k2, dt / 2), s, rho, beta)
    k4 = _lz(add(st, k3, dt), s, rho, beta)
    return (st[0] + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
            st[1] + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]),
            st[2] + dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]))


def lorenz(n=16000, dt=0.006, s=10.0, rho=28.0, beta=8.0 / 3.0, start=(0.0, 1.0, 1.05)):
    """The Lorenz system, stepped with classic Runge–Kutta 4."""
    st = start
    out = [st]
    for _ in range(n):
        st = _step(st, dt, s, rho, beta)
        out.append(st)
    return out


def lyapunov_benettin(dt=0.006, n=60000, d0=1e-9, s=10.0, rho=28.0, beta=8.0 / 3.0):
    """Benettin's method for the largest Lyapunov exponent: run a reference point and a
    twin a hair away, and every step measure how much the gap grew, then pull the twin
    back to distance d0 so it never saturates. The average log-growth per unit time is the
    exponent. Converges to the textbook 0.906 for these parameters."""
    a = lorenz(4000, dt, s, rho, beta, (1.0, 1.0, 1.0))[-1]
    b = (a[0] + d0, a[1], a[2])
    total = 0.0
    for _ in range(n):
        a = _step(a, dt, s, rho, beta)
        b = _step(b, dt, s, rho, beta)
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        d = math.sqrt(dx * dx + dy * dy + dz * dz)
        total += math.log(d / d0)
        f = d0 / d
        b = (a[0] + dx * f, a[1] + dy * f, a[2] + dz * f)
    return total / (n * dt)


# ====================================================================== the figures
def fig_two_creeks():
    """Sensitive dependence: two starts a hair apart, the same rule, and the split."""
    r, n = 3.9, 55
    a = logistic_series(r, 0.4000, n)
    b = logistic_series(r, 0.4001, n)
    split = next((i for i in range(n) if abs(a[i] - b[i]) > 0.25), n)
    p = Plot(xlim=(0, n), ylim=(0, 1), xlabel="step  n", ylabel="value  xₙ",
             title=f"Two starts a ten-thousandth apart · r = {r}")
    p.polyline(list(enumerate(a)), stroke=BLUE, w=2.2)
    p.polyline(list(enumerate(b)), stroke=HOT, w=2.2)
    p.vline(split, stroke=MUTE, dash="4 5")
    p.label(split, 0.96, f"they part ways by step {split}", fill=MUTE, size=13, dx=8)
    p.label(2, a[2], "start 0.4000", fill=BLUE, dx=6, dy=-8)
    p.label(2, b[6] + 0.12, "start 0.4001", fill=HOT, dx=6, dy=-8)
    return p.svg(), {"split_step": split, "r_creek": r}


def fig_cobweb(r, x0=0.2, steps=60, title=""):
    """The map as a picture: the hill y = r x (1−x), the mirror y = x, and the staircase
    the iteration climbs between them."""
    p = Plot(w=560, h=520, xlim=(0, 1), ylim=(0, 1), xlabel="xₙ", ylabel="xₙ₊₁", title=title)
    hill = [(i / 200, r * (i / 200) * (1 - i / 200)) for i in range(201)]
    p.polyline(hill, stroke=HOT, w=2.4)
    p.polyline([(0, 0), (1, 1)], stroke=MUTE, w=1.4, dash="5 5")
    x = x0
    web = [(x, 0)]
    for _ in range(steps):
        y = r * x * (1 - x)
        web.append((x, y))
        web.append((y, y))
        x = y
    p.polyline(web, stroke=BLUE, w=1.1, opacity=0.9)
    return p.svg()


def fig_bifurcation():
    """The whole family at once: for each growth rate r, the values the map settles onto.
    One line, then two, then four, then a smear — the road into chaos."""
    p = Plot(w=960, h=600, xlim=(2.5, 4.0), ylim=(0, 1), xlabel="growth rate  r",
             ylabel="values it settles on", title="The logistic map, every r at once")
    xs, ys = [], []
    R = 1100
    for i in range(R):
        r = 2.5 + (4.0 - 2.5) * i / (R - 1)
        x = 0.5
        for _ in range(500):
            x = r * x * (1 - x)
        for _ in range(180):
            x = r * x * (1 - x)
            xs.append(r); ys.append(x)
    p.raster_scatter(xs, ys, rgb=(255, 179, 71), gain=70)
    for rv, lab in [(3.0, "2"), (3.449, "4"), (3.544, "8")]:
        p.vline(rv, stroke=BLUE, dash="3 5", w=1, opacity=0.7)
    p.vline(3.5699, stroke=VIOLET, dash="3 5", w=1.2, opacity=0.9)
    p.label(3.5699, 0.02, "chaos begins", fill=VIOLET, size=12, dx=-4, dy=-4, anchor="end")
    p.label(3.0, 0.9, "period 2", fill=BLUE, size=12, dx=6)
    return p.svg()


def fig_bifurcation_zoom():
    """The same tree, zoomed into a window high in the chaos where order comes back — the
    period-3 band that Li and Yorke built their proof on."""
    p = Plot(w=960, h=460, xlim=(3.82, 3.87), ylim=(0, 1), xlabel="growth rate  r",
             ylabel="values it settles on", title="A window of calm inside the chaos · the period-3 band")
    xs, ys = [], []
    R = 1100
    for i in range(R):
        r = 3.82 + (3.87 - 3.82) * i / (R - 1)
        x = 0.5
        for _ in range(800):
            x = r * x * (1 - x)
        for _ in range(200):
            x = r * x * (1 - x)
            xs.append(r); ys.append(x)
    p.raster_scatter(xs, ys, rgb=(255, 210, 122), gain=55)
    p.vline(3.8284, stroke=BLUE, dash="3 5", w=1.2)
    p.label(3.8284, 0.9, "period 3 opens", fill=BLUE, size=12, dx=6)
    return p.svg()


def fig_lorenz(traj):
    """The butterfly: the Lorenz path, seen from the side (x across, z up). Two wings, and
    the line never crosses itself and never repeats."""
    p = Plot(w=760, h=620, xlim=(-22, 22), ylim=(0, 52), xlabel="x", ylabel="z",
             title="The Lorenz attractor · σ=10, ρ=28, β=8/3")
    p.raster_path([(s[0], s[2]) for s in traj], rgb=(255, 179, 71), width=1, alpha=150)
    return p.svg()


def fig_forecast(p0, dt):
    """Two Lorenz runs a hair apart in x, drawn together. They lie on top of each other,
    then one day they don't."""
    T = 5200
    seed = 1e-5
    a = lorenz(T, dt, start=p0)
    b = lorenz(T, dt, start=(p0[0] + seed, p0[1], p0[2]))
    ts = [i * dt for i in range(T + 1)]
    p = Plot(w=960, h=440, xlim=(0, ts[-1]), ylim=(-24, 24), xlabel="time",
             ylabel="x (the state)", title="Same rule, two starts 0.00001 apart",
             yticks=[-20, -10, 0, 10, 20])
    p.polyline([(ts[i], a[i][0]) for i in range(T + 1)], stroke=BLUE, w=1.3)
    p.polyline([(ts[i], b[i][0]) for i in range(T + 1)], stroke=HOT, w=1.3, opacity=0.9)
    sep = next((i for i in range(T + 1) if abs(a[i][0] - b[i][0]) > 6), T)
    p.vline(ts[sep], stroke=MUTE, dash="4 5")
    p.label(ts[sep], 21, "the two forecasts part", fill=MUTE, size=13, dx=8)
    return p.svg(), sep * dt


def fig_lyapunov(p0, dt, lam):
    """The gap between nearby starts, averaged over many pairs, on a log scale. A straight
    climb means it grows by a fixed multiplier every second — that slope is the Lyapunov
    exponent, and its reciprocal is how far ahead a forecast can see."""
    K, T, d0 = 24, 3600, 1e-8
    # spread K reference starts along a long run so the pairs sample the whole attractor
    ref = lorenz(K * 220, dt, start=p0)
    logmean = [0.0] * (T + 1)
    for k in range(K):
        s0 = ref[k * 220]
        a = s0
        b = (s0[0] + d0, s0[1], s0[2])
        logmean[0] += math.log(d0)
        for i in range(1, T + 1):
            a = _step(a, dt, 10.0, 28.0, 8.0 / 3.0)
            b = _step(b, dt, 10.0, 28.0, 8.0 / 3.0)
            logmean[i] += math.log(math.dist(a, b))
    logmean = [v / K for v in logmean]
    ts = [i * dt for i in range(T + 1)]
    p = Plot(w=960, h=440, xlim=(0, ts[-1]), ylim=(d0 / 3, 60), logy=True,
             xlabel="time", ylabel="typical gap", title="The gap grows by a fixed factor each second",
             yfmt=lambda v: ("1" if abs(v - 1) < 1e-9 else f"{v:g}"))
    p.polyline([(ts[i], math.exp(logmean[i])) for i in range(T + 1)], stroke=HOT, w=1.9)
    # the straight climb this exponent predicts, from the first point
    p.polyline([(ts[i], min(60, d0 * math.exp(lam * ts[i]))) for i in range(T + 1)
                if d0 * math.exp(lam * ts[i]) < 60], stroke=BLUE, w=1.6, dash="6 5")
    horizon = 1.0 / lam
    p.label(9, d0 * math.exp(lam * 9) * 3, f"slope λ ≈ {lam:.2f} per second", fill=BLUE, size=13)
    p.hline(30, stroke=MUTE, dash="3 6", w=1)
    p.label(1, 34, "the size of the whole butterfly — the gap can't grow past it", fill=MUTE, size=12, dx=0, anchor="start")
    return p.svg(), {"horizon": round(horizon, 1)}


def fig_dice():
    """The law of large numbers, one figure. Roll a fair die again and again; the running
    average wanders at first, then is reeled in to 3.5. The shaded funnel is 1/√N wide."""
    rng = random.Random(70118)
    N = 3000
    run = []
    s = 0
    for i in range(1, N + 1):
        s += rng.randint(1, 6)
        run.append((i, s / i))
    mu = 3.5
    sig = math.sqrt(sum((k - mu) ** 2 for k in range(1, 7)) / 6)
    p = Plot(w=960, h=440, xlim=(1, N), ylim=(1, 6), xlabel="number of rolls  N",
             ylabel="average so far", title="One fair die, rolled 3,000 times",
             xticks=[1, 500, 1000, 1500, 2000, 2500, 3000])
    # 1/sqrt(N) funnel around 3.5
    up = [(i, min(6, mu + 2 * sig / math.sqrt(i))) for i in range(1, N + 1)]
    dn = [(i, max(1, mu - 2 * sig / math.sqrt(i))) for i in range(1, N + 1)]
    band = up + dn[::-1]
    d = " ".join(f"{p._n(p.px(x))},{p._n(p.py(y))}" for x, y in band)
    p.body.insert(0, f'<polygon points="{d}" fill="{BLUE}" opacity="0.12"/>')
    p.hline(mu, stroke=GOLD, dash="6 5", w=1.6)
    p.label(N * 0.62, mu, "the true average, 3.5", fill=GOLD, size=13, dy=-8)
    p.polyline(run, stroke=HOT, w=1.7)
    p.label(N * 0.3, 5.4, "±2·σ/√N", fill=BLUE, size=12)
    return p.svg(), {"dice_final": round(run[-1][1], 3)}


def fig_invariant():
    """Chaos and order in one picture. The r=4 map never repeats — but drop 300,000 of its
    values into bins and the pile is always this exact curve, 1/(π√(x(1−x)))."""
    N, burn, bins = 300000, 1000, 60
    x = 0.31415926
    for _ in range(burn):
        x = 4 * x * (1 - x)
    counts = [0] * bins
    for _ in range(N):
        x = 4 * x * (1 - x)
        b = min(bins - 1, int(x * bins))
        counts[b] += 1
    dens = [c / N * bins for c in counts]  # normalised to a density
    p = Plot(w=960, h=460, xlim=(0, 1), ylim=(0, max(dens[3:-3]) * 1.15),
             xlabel="value  x", ylabel="how often", title="300,000 values of a map that never repeats")
    for i, dv in enumerate(dens):
        p.rect(i / bins, 0, 1 / bins, dv, fill=HOT, opacity=0.55)
    theory = [((i + 0.5) / 400, 1.0 / (math.pi * math.sqrt(max((i + 0.5) / 400 * (1 - (i + 0.5) / 400), 1e-9))))
              for i in range(400)]
    theory = [(xx, yy) for xx, yy in theory if yy < max(dens[3:-3]) * 1.15]
    p.polyline(theory, stroke=BLUE, w=2.4)
    p.label(0.5, 0.66, "the curve 1 / (π √(x(1−x)))", fill=BLUE, size=13, anchor="middle", dx=0)
    return p.svg()


def fig_governor():
    """Resilience as negative feedback. Two tanks take the same run of random shocks. One
    just accumulates them and drifts off; the other pulls a fraction of its error back every
    step and stays near the line."""
    rng = random.Random(4669)
    N = 240
    shocks = [rng.gauss(0, 1) for _ in range(N)]
    drift = 0.0
    held = 0.0
    k = 0.28  # how hard the governor pulls back
    a, b = [], []
    for i in range(N):
        drift += shocks[i] * 0.5
        held += shocks[i] * 0.5
        held -= k * held  # negative feedback
        a.append((i, drift)); b.append((i, held))
    lim = max(abs(v) for _, v in a) * 1.1
    p = Plot(w=960, h=420, xlim=(0, N), ylim=(-lim, lim), xlabel="step",
             ylabel="distance from where it should be", title="Same shocks, two tanks")
    p.hline(0, stroke=MUTE, dash="4 6", w=1)
    p.polyline(a, stroke=RED, w=1.8)
    p.polyline(b, stroke=GREEN, w=1.9)
    p.label(N * 0.5, a[int(N * 0.5)][1], "no feedback — it wanders off", fill=RED, size=13, dy=-8)
    p.label(N * 0.5, lim * 0.55, "pulls back 28% each step — it holds", fill=GREEN, size=13)
    rms_drift = math.sqrt(sum(v * v for _, v in a) / N)
    rms_held = math.sqrt(sum(v * v for _, v in b) / N)
    return p.svg(), {"rms_drift": round(rms_drift, 2), "rms_held": round(rms_held, 2)}


def fig_redundancy():
    """Redundancy, and the trap in it. If one part fails one time in ten, N parts that fail
    on their own all fail together only 0.1^N of the time — but let their failures move
    together and that floor rises fast."""
    p = Plot(w=960, h=440, xlim=(1, 6), ylim=(1e-6, 1), logy=True, xlabel="number of parts  N",
             ylabel="chance all of them fail", title="One part fails 1 in 10 · what N parts do",
             xticks=[1, 2, 3, 4, 5, 6])
    pp = 0.1
    indep = [(n, pp ** n) for n in range(1, 7)]
    p.polyline(indep, stroke=GREEN, w=2.2)
    for n, y in indep:
        p.circle(n, y, r=3, fill=GREEN)
    # correlated: a shared cause fires with prob c; otherwise independent
    for c, col, lab in [(0.01, BLUE, "1% shared cause"), (0.03, HOT, "3% shared cause")]:
        cor = [(n, c + (1 - c) * pp ** n) for n in range(1, 7)]
        p.polyline(cor, stroke=col, w=1.9, dash="6 5")
        for n, y in cor:
            p.circle(n, y, r=2.6, fill=col)
    p.label(4, pp ** 4, "independent — 0.1ᴺ", fill=GREEN, size=13, dy=-10)
    p.label(5, 0.03, "a shared cause sets the floor", fill=HOT, size=12, dy=-8, anchor="end")
    return p.svg()


def fig_portfolio():
    """Spreading a bet is the law of large numbers put to work. Split the same stake over N
    independent bets and the swing shrinks as 1/√N — but only as far as they stay
    independent; shared risk leaves a floor nothing diversifies away."""
    p = Plot(w=960, h=420, xlim=(1, 40), ylim=(0, 1.05), xlabel="number of independent bets  N",
             ylabel="size of the swing", title="Spread the stake · the swing falls as 1/√N")
    indep = [(n, 1 / math.sqrt(n)) for n in range(1, 41)]
    p.polyline(indep, stroke=HOT, w=2.4)
    # with a shared (undiversifiable) part rho of the variance
    rho = 0.2
    withmkt = [(n, math.sqrt(rho + (1 - rho) / n)) for n in range(1, 41)]
    p.polyline(withmkt, stroke=BLUE, w=2.0, dash="6 5")
    p.hline(math.sqrt(rho), stroke=MUTE, dash="3 6", w=1.2)
    p.label(24, 1 / math.sqrt(24), "all independent — keeps falling", fill=HOT, size=13, dy=-10)
    p.label(24, math.sqrt(rho + (1 - rho) / 24), "20% shared — stops at a floor", fill=BLUE, size=12, dy=-8)
    return p.svg()


# ====================================================================== build all
def build(out_dir: Path):
    facts = {}
    figs = {}

    figs["creeks"], f = fig_two_creeks(); facts.update(f)
    figs["cobweb_calm"] = fig_cobweb(2.8, title="r = 2.8 · it settles to one value")
    figs["cobweb_two"] = fig_cobweb(3.3, title="r = 3.3 · it locks to a two-step swing")
    figs["cobweb_chaos"] = fig_cobweb(3.9, x0=0.2, title="r = 3.9 · it never settles")
    figs["bifurcation"] = fig_bifurcation()
    figs["bifurcation_zoom"] = fig_bifurcation_zoom()

    rs, deltas = find_doublings()
    facts["doublings"] = [round(v, 4) for v in rs]
    facts["feigenbaum"] = round(deltas[-1], 3) if deltas else None
    facts["feigenbaum_all"] = [round(d, 3) for d in deltas]

    dt = 0.006
    p0 = lorenz(4000, dt, start=(1.0, 1.0, 1.0))[-1]  # a point already on the attractor
    traj = lorenz(n=16000, dt=dt, start=p0)
    figs["lorenz"] = fig_lorenz(traj)
    lam = lyapunov_benettin(dt=dt, n=60000)
    facts["lyapunov"] = round(lam, 3)
    figs["forecast"], sep_t = fig_forecast(p0, dt)
    facts["forecast_sep_time"] = round(sep_t, 1)
    figs["lyapunov_fig"], f = fig_lyapunov(p0, dt, lam); facts.update(f)

    figs["dice"], f = fig_dice(); facts.update(f)
    figs["invariant"] = fig_invariant()
    figs["governor"], f = fig_governor(); facts.update(f)
    figs["redundancy"] = fig_redundancy()
    figs["portfolio"] = fig_portfolio()

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "facts.json").write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8")
    (out_dir / "figs.json").write_text(json.dumps(figs) + "\n", encoding="utf-8")
    return facts, figs


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    facts, figs = build(root / "build")
    print(json.dumps(facts, indent=2))
    print(f"\n{len(figs)} figures drawn.")
