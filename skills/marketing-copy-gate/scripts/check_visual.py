#!/usr/bin/env python3
"""Visual check for LinkedIn carousels against the approved benchmark (Brad, 17 Nov 2026).

The look of ERMOS LinkedIn posts is set by Post 1 and Post 2 (marketing-linkedin-posts
SOP, step 5b), not by the website palette. This script runs before Brad sees any
carousel and fails it when it drifts from that look:

  FAIL  page size is not 1080 x 1350, or fewer than 5 / more than 15 slides
  FAIL  a font other than Sora or Inter is used
  FAIL  more than one slide is not on the paper background (#EFEEEA); Post 2 uses
        paper on every slide except one closing photo slide
  FAIL  website electric blue (#2563FF / #1D4ED8 family) used as an accent; LinkedIn
        accents are teal (#2F8A80)
  WARN  no photo on any slide, when the benchmark has photo bands (cover, a middle
        slide, close); Brad decides
  WARN  teal accent not used anywhere

It also writes a side-by-side sheet (benchmark on top, draft below) that is shown to
Brad with the draft, so the comparison is visible, not asserted.

  python3 check_visual.py draft.pdf [--benchmark benchmarks/linkedin-post-2.pdf]
                          [--sheet out.png]
Exit 0 = pass (warnings allowed), 1 = fail.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BENCH = os.path.join(HERE, "..", "benchmarks", "linkedin-post-2.pdf")
PAPER = (0xEF, 0xEE, 0xEA)
TEAL = (0x2F, 0x8A, 0x80)
BLUES = [(0x25, 0x63, 0xFF), (0x1D, 0x4E, 0xD8), (0x7F, 0xA6, 0xFF)]
FONT_OK = re.compile(r"(?i)\+?(sora|inter)[-a-z]*")
FONT_TOLERATED = re.compile(r"(?i)lucidagrande")  # tick glyph in the Post 2 benchmark


def near(a, b, tol):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def render(pdf, outdir, prefix):
    subprocess.run(["pdftoppm", "-r", "48", "-png", pdf, os.path.join(outdir, prefix)], check=True)
    return sorted(glob.glob(os.path.join(outdir, prefix + "*.png")))


def page_facts(png):
    im = Image.open(png).convert("RGB")
    w, h = im.size
    px = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())
    top = [im.getpixel((x, y)) for y in range(int(h * 0.02), int(h * 0.12)) for x in range(w)]
    paper_top = sum(near(p, PAPER, 10) for p in top) / len(top)
    blue = sum(any(near(p, b, 28) for b in BLUES) for p in px) / len(px)
    teal = sum(near(p, TEAL, 40) for p in px)
    # a photo shows as many distinct, non-paper colours
    distinct = len({(r // 8, g // 8, b // 8) for r, g, b in px if not near((r, g, b), PAPER, 10)})
    return {"paper_top": round(paper_top, 2), "blue": round(blue, 4), "teal": teal,
            "photo": distinct > 300}


def fonts(pdf):
    out = subprocess.run(["pdffonts", pdf], capture_output=True, text=True).stdout.splitlines()[2:]
    return sorted({line.split()[0].split("+")[-1] for line in out if line.strip()})


def sizes(pdf):
    out = subprocess.run(["pdfinfo", "-f", "1", "-l", "999", pdf], capture_output=True, text=True).stdout
    return re.findall(r"Page\s+\d+ size:\s+([\d.]+) x ([\d.]+) pts", out)


def sheet(bench_pngs, draft_pngs, path):
    cw, ch = 216, 270
    cols = max(len(bench_pngs), len(draft_pngs))
    s = Image.new("RGB", (cols * (cw + 8), 2 * ch + 16), "white")
    for row, pngs in enumerate([bench_pngs, draft_pngs]):
        for i, p in enumerate(pngs):
            s.paste(Image.open(p).convert("RGB").resize((cw, ch)), (i * (cw + 8), row * (ch + 16)))
    s.save(path)


def check(pdf, bench, sheet_path=None):
    fails, warns = [], []
    sz = sizes(pdf)
    n = len(sz)
    if not 5 <= n <= 15:
        fails.append(f"{n} slides; LinkedIn carousels use 5 to 15")
    bad = [i + 1 for i, (w, h) in enumerate(sz) if abs(float(w) - 810) > 2 or abs(float(h) - 1012.5) > 2]
    if bad:
        fails.append(f"slides {bad} are not 1080 x 1350 px")
    odd = [f for f in fonts(pdf) if not FONT_OK.fullmatch(f) and not FONT_TOLERATED.search(f)]
    if odd:
        fails.append(f"fonts other than Sora/Inter: {odd}")
    with tempfile.TemporaryDirectory() as t:
        draft = render(pdf, t, "d")
        facts = [page_facts(p) for p in draft]
        off_paper = [i + 1 for i, f in enumerate(facts) if f["paper_top"] < 0.6 and not f["photo"]]
        dark_or_photo = [i + 1 for i, f in enumerate(facts) if f["paper_top"] < 0.6]
        if len(dark_or_photo) > 1 or off_paper:
            fails.append(f"slides {dark_or_photo} are not on the paper background (#EFEEEA); "
                         "the benchmark keeps every slide on paper except one closing photo slide")
        blue = [i + 1 for i, f in enumerate(facts) if f["blue"] > 0.002]
        if blue:
            fails.append(f"slides {blue} use website electric blue; LinkedIn accents are teal #2F8A80")
        if not any(f["teal"] > 50 for f in facts):
            warns.append("teal accent (#2F8A80) not used on any slide")
        bench_pngs = render(bench, t, "b") if bench and os.path.exists(bench) else []
        bench_photos = [i + 1 for i, p in enumerate(bench_pngs) if page_facts(p)["photo"]]
        if bench_photos and not any(f["photo"] for f in facts):
            warns.append(f"no photo on any slide; the benchmark has photo bands on slides {bench_photos}")
        if sheet_path:
            sheet(bench_pngs, draft, sheet_path)
    return {"pass": not fails, "slides": n, "fails": fails, "warnings": warns, "pages": facts,
            "sheet": sheet_path}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("pdf")
    p.add_argument("--benchmark", default=DEFAULT_BENCH)
    p.add_argument("--sheet")
    a = p.parse_args(argv)
    r = check(a.pdf, a.benchmark, a.sheet)
    print(json.dumps(r, indent=2))
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
