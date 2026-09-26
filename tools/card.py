#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""card.py — the share card, 1200×630, drawn from the mathematics like everything else.

The Lorenz butterfly, computed here, under the title. Written to build/site/card.jpg and
referenced by the pages' og:image / twitter:image.

    python3 tools/card.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figures as F  # noqa: E402

SITE = Path(__file__).resolve().parent.parent / "build" / "site"
W, H = 1200, 630
BG = (7, 7, 11)
INK = (243, 239, 230)
HOT = (255, 179, 71)
MUTE = (179, 172, 158)

COND = "/System/Library/Fonts/Avenir Next Condensed.ttc"
BODY = "/System/Library/Fonts/Avenir Next.ttc"


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()


def build():
    img = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(img, "RGBA")

    # the butterfly, computed, placed to the right and drawn large at 2x then downscaled
    scale = 2
    lay = Image.new("RGBA", (W * scale, H * scale), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    p0 = F.lorenz(4000, 0.006, start=(1.0, 1.0, 1.0))[-1]
    traj = F.lorenz(20000, 0.006, start=p0)
    xs = [s[0] for s in traj]; zs = [s[2] for s in traj]
    xmin, xmax = -21, 21
    zmin, zmax = 2, 50
    # frame the butterfly on the right two-thirds, bleeding off the top
    ox, oy, bw, bh = int(W * 0.30) * scale, int(-40) * scale, int(W * 0.72) * scale, int(H * 1.05) * scale
    pts = []
    for x, z in zip(xs, zs):
        X = ox + (x - xmin) / (xmax - xmin) * bw
        Y = oy + (zmax - z) / (zmax - zmin) * bh
        pts.append((X, Y))
    ld.line(pts, fill=(255, 179, 71, 120), width=2, joint="curve")
    lay = lay.resize((W, H), Image.LANCZOS)
    img.paste(Image.new("RGB", (W, H), BG), (0, 0))  # keep bg
    img = Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")
    dr = ImageDraw.Draw(img, "RGBA")

    # a scrim from the left so the text sits clean
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    for x in range(W):
        a = int(235 * max(0, 1 - x / (W * 0.72)))
        sd.line([(x, 0), (x, H)], fill=(7, 7, 11, a))
    sd.rectangle([0, H - 150, W, H], fill=(7, 7, 11, 150))
    img = Image.alpha_composite(img.convert("RGBA"), scrim).convert("RGB")
    dr = ImageDraw.Draw(img, "RGBA")

    # an eclipse mark, like the brand dot
    cx, cy, r = 92, 96, 26
    dr.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6], fill=(255, 179, 71, 70))
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 0, 0), outline=HOT, width=5)

    kick = font(COND, 30, index=2)
    title = font(COND, 150, index=2)
    sub = font(BODY, 34, index=0)
    tiny = font(BODY, 26, index=0)

    dr.text((140, 78), "CHAOS THEORY, DRAWN FROM THE EQUATIONS", font=kick, fill=HOT)
    dr.text((66, 150), "CHAOS,", font=title, fill=INK)
    dr.text((66, 300), "DRAWN", font=title, fill=HOT)
    dr.text((70, 476),
            "Every picture from the math — and the two tools",
            font=sub, fill=INK)
    dr.text((70, 516),
            "that hold up under it: large numbers, resilience.",
            font=sub, fill=INK)
    dr.text((70, H - 54), "hongdam.net · Chiang Rai", font=tiny, fill=MUTE)

    out = SITE / "card.jpg"
    img.save(out, format="JPEG", quality=86, optimize=True)
    print(f"card → {out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
