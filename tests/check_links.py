#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_links.py — every internal link on the built site points at a file that exists, and
every citation superscript points at an anchor the sources page actually carries."""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "build" / "site"
BASE = (SITE / ".basepath").read_text(encoding="utf-8").strip() if (SITE / ".basepath").exists() else "/"


def target(href):
    """Map an in-site href to the file on disk it should resolve to."""
    href = href.split("#", 1)[0]
    if not href.startswith(BASE):
        return None
    rel = href[len(BASE):]
    if rel == "" or rel.endswith("/"):
        return SITE / rel / "index.html"
    return SITE / rel


def anchors(path):
    txt = path.read_text(encoding="utf-8")
    return set(re.findall(r'id="([^"]+)"', txt))


def main():
    pages = list(SITE.rglob("*.html"))
    src_anchors = anchors(SITE / "sources" / "index.html")
    bad = []
    for p in pages:
        txt = p.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', txt):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if "#" in href and href.split("#", 1)[0].rstrip("/") == (BASE + "sources").rstrip("/"):
                anc = href.split("#", 1)[1]
                if anc not in src_anchors:
                    bad.append((p.relative_to(SITE), href, "missing sources anchor"))
                continue
            t = target(href)
            if t is None:
                continue
            if not t.exists():
                bad.append((p.relative_to(SITE), href, "no such file"))
    if bad:
        for page, href, why in bad:
            print(f"  BROKEN  {page}  →  {href}  ({why})")
        print(f"{len(bad)} broken link(s).")
        sys.exit(1)
    print(f"links ok · {len(pages)} pages checked, {len(src_anchors)} source anchors")


if __name__ == "__main__":
    main()
