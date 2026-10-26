#!/usr/bin/env python3
"""Crop one figure out of a compiled report PDF as a PNG.

Locates the caption with `pdftotext -bbox-layout`, takes the region between the
caption and the nearest body-text paragraph, trims white margins, and renders it
with `pdftoppm`. Always look at the PNG afterwards; if the box is wrong, rerun
with --page/--top/--bottom/--left/--right (PDF points, origin top-left; the
script prints the box it used).

Example:
  crop_figure.py build/report/main.pdf --caption "รูปที่ 3:" --out assets/figures/fig03.png
"""
import argparse
import html
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

BOX = r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)"'


def norm(s):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", html.unescape(s)))


def parse_layout(pdf):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "bbox.html"
        subprocess.run(["pdftotext", "-bbox-layout", str(pdf), str(out)], check=True)
        doc = out.read_text(encoding="utf-8", errors="replace")
    pages = []
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', doc, re.S):
        blocks = []
        for bm in re.finditer(r"<block " + BOX + r">(.*?)</block>", pm.group(3), re.S):
            lines = []
            for lm in re.finditer(r"<line " + BOX + r">(.*?)</line>", bm.group(5), re.S):
                words = re.findall(r"<word[^>]*>(.*?)</word>", lm.group(5), re.S)
                lines.append({"box": tuple(map(float, lm.groups()[:4])), "text": " ".join(words)})
            blocks.append({"box": tuple(map(float, bm.groups()[:4])), "lines": lines})
        pages.append({"w": float(pm.group(1)), "h": float(pm.group(2)), "blocks": blocks})
    return pages


def find_caption(pages, needle, only_page=None):
    needle = norm(needle)
    hits = []
    for pi, page in enumerate(pages, 1):
        if only_page and pi != only_page:
            continue
        flat, owners, starts = "", [], set()
        for bi, block in enumerate(page["blocks"]):
            for line in block["lines"]:
                starts.add(len(flat))
                t = norm(line["text"])
                flat += t
                owners += [(bi, line)] * len(t)
        for m in re.finditer(re.escape(needle), flat):
            bi, line = owners[m.start()]
            hits.append((m.start() not in starts, pi, bi, line))
    if not hits:
        return None
    hits.sort(key=lambda h: (h[0], h[1]))
    return hits[0][1:]


def guess_box(page, bi, cap_line, side):
    """Figure = region between the caption and the nearest line that starts at the body's left margin."""
    lines = [l for b in page["blocks"] for l in b["lines"]]
    starts = [round(l["box"][0]) for l in lines]
    margin = max(set(starts), key=starts.count)
    left = min(l["box"][0] for l in lines) - 2
    right = max(l["box"][2] for l in lines) + 2
    cap_lines = page["blocks"][bi]["lines"]

    def is_body(line):
        return abs(line["box"][0] - margin) <= 1.5 and line not in cap_lines

    if side == "above":
        bottom = cap_line["box"][1] - 2
        above = sorted((l for l in lines if l["box"][3] <= bottom + 1), key=lambda l: -l["box"][3])
        body = next((l for l in above if is_body(l)), None)
        top = body["box"][3] + 2 if body else page["h"] * 0.05
    else:
        top = max(l["box"][3] for l in cap_lines) + 2
        below = sorted((l for l in lines if l["box"][1] >= top - 1), key=lambda l: l["box"][1])
        body = next((l for l in below if is_body(l)), None)
        bottom = body["box"][1] - 2 if body else page["h"] * 0.95
    return left, top, right, bottom


def read_pgm(path):
    data = Path(path).read_bytes()
    tokens, pos = [], 0
    while len(tokens) < 4:
        m = re.compile(rb"\s*(#[^\n]*\n\s*)*(\S+)").match(data, pos)
        tokens.append(m.group(2))
        pos = m.end()
    w, h = int(tokens[1]), int(tokens[2])
    return w, h, data[pos + 1:pos + 1 + w * h]


def render(pdf, page, box, dpi, out_prefix, gray=False):
    left, top, right, bottom = box
    k = dpi / 72
    cmd = ["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(dpi),
           "-x", str(int(left * k)), "-y", str(int(top * k)),
           "-W", str(int((right - left) * k)), "-H", str(int((bottom - top) * k)), "-singlefile"]
    cmd += ["-gray"] if gray else ["-png"]
    subprocess.run(cmd + [str(pdf), str(out_prefix)], check=True)


def trim(pdf, page, box, pad=4):
    """Shrink box to the non-white content inside it, dropping header/footer rules at the edges."""
    with tempfile.TemporaryDirectory() as tmp:
        render(pdf, page, box, 72, Path(tmp) / "t", gray=True)
        w, h, px = read_pgm(Path(tmp) / "t.pgm")
    rows = [[x for x in range(w) if px[y * w + x] < 245] for y in range(h)]
    ink_rows = [y for y in range(h) if rows[y]]
    if not ink_rows:
        return box
    groups = [[ink_rows[0]]]
    for y in ink_rows[1:]:
        if y - groups[-1][-1] > 6:
            groups.append([])
        groups[-1].append(y)

    def is_rule(g):
        xs = [x for y in g for x in rows[y]]
        return len(g) <= 2 and max(xs) - min(xs) >= 0.9 * w

    while len(groups) > 1 and is_rule(groups[0]):
        groups.pop(0)
    while len(groups) > 1 and is_rule(groups[-1]):
        groups.pop()
    ys = [y for g in groups for y in g]
    xs = [x for y in ys for x in rows[y]]
    left, top = box[0], box[1]
    return (max(box[0], left + min(xs) - pad), max(box[1], top + min(ys) - pad),
            min(box[2], left + max(xs) + 1 + pad), min(box[3], top + max(ys) + 1 + pad))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--caption", help="distinctive plain-text run from the caption, e.g. its label 'รูปที่ 3:'")
    ap.add_argument("--out", required=True, help="output .png path")
    ap.add_argument("--side", choices=["above", "below"], default="above",
                    help="where the figure sits relative to its caption (default: above)")
    ap.add_argument("--page", type=int, help="restrict the caption search / page to crop (1-based)")
    for edge in ("top", "bottom", "left", "right"):
        ap.add_argument(f"--{edge}", type=float, help=f"override {edge} edge in PDF points")
    ap.add_argument("--no-trim", action="store_true")
    ap.add_argument("--dpi", type=int, default=300)
    a = ap.parse_args()

    pdf = Path(a.pdf).resolve()
    pages = parse_layout(pdf)
    box, page = None, a.page
    if a.caption:
        hit = find_caption(pages, a.caption, a.page)
        if not hit:
            sys.exit(f"Caption text not found: {a.caption!r}. Try a shorter plain-text run, or pass --page and all four edges.")
        page, bi, line = hit
        box = guess_box(pages[page - 1], bi, line, a.side)
    if page is None:
        sys.exit("Need --caption, or --page with all four edges.")
    pw, ph = pages[page - 1]["w"], pages[page - 1]["h"]
    box = list(box or (0, 0, pw, ph))
    overrides = [a.left, a.top, a.right, a.bottom]
    for i, v in enumerate(overrides):
        if v is not None:
            box[i] = v
    if not a.no_trim:
        box = list(trim(pdf, page, tuple(box)))

    out = Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    render(pdf, page, box, a.dpi, out.with_suffix(""))
    print(f"page={page} left={box[0]:.1f} top={box[1]:.1f} right={box[2]:.1f} bottom={box[3]:.1f} (page {pw:.0f}x{ph:.0f}pt)")
    print(f"wrote {out} — open it and confirm the crop holds the whole figure and nothing else")


if __name__ == "__main__":
    main()
