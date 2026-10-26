#!/usr/bin/env python3
"""Compile the slides and report every problem by page and frame title.

Builds <slides>/main.tex into <slides>/build/, copies the PDF to
<slides>/main.pdf, and renders every page to <slides>/build/pages/page-NN.png
for visual review.

Exit codes: 0 clean | 1 warnings to fix | 2 compile error
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from _tex import latexmk, log_errors, strip_comments

MAX_BULLETS = 4
CLOSING_TITLE = "Key Takeaways"
WARNINGS = [
    (r"(Overfull \\[hv]box \([\d.]+pt too (?:wide|high)\))", "overflow"),
    (r"Missing character: There is no (.+?) in font", "missing glyph"),
    (r"LaTeX Warning: (Citation `[^']+' [^\n]*undefined)", "undefined"),
    (r"LaTeX Warning: (Reference `[^']+' [^\n]*undefined)", "undefined"),
]


def frames(tex):
    text = strip_comments(tex.read_text(encoding="utf-8", errors="replace"))
    out = []
    for m in re.finditer(r"\\begin\{frame\}(.*?)\\end\{frame\}", text, re.S):
        head = re.match(r"\s*(?:<[^>]*>)?\s*(?:\[[^\]]*\])?\s*(?:\{([^}]*)\})?", m.group(1))
        title = head.group(1) if head and head.group(1) else None
        if not title:
            t = re.search(r"\\frametitle\{([^}]*)\}", m.group(1))
            title = t.group(1) if t else "(untitled)"
        body = re.sub(r"\\note\{.*", "", m.group(1), flags=re.S)
        lists = re.findall(r"\\begin\{(?:itemize|enumerate)\}(.*?)\\end\{(?:itemize|enumerate)\}", body, re.S)
        out.append({"title": title.strip(), "bullets": max((len(re.findall(r"\\item\b", l)) for l in lists), default=0)})
    return out


def warnings_by_page(log):
    text = log.read_text(encoding="utf-8", errors="replace")
    events = []
    for pat, kind in WARNINGS:
        events += [(m.start(), kind, m.group(1).replace("\n", "")) for m in re.finditer(pat, text, re.S)]
    shipped, page_at = 0, []
    for m in re.finditer(r"\[(\d+)(?=[\s\]<{])", text):
        if int(m.group(1)) == shipped + 1:
            shipped += 1
            page_at.append(m.start())
    found = []
    for pos, kind, msg in sorted(events):
        page = next((i + 1 for i, p in enumerate(page_at) if p > pos), shipped + 1)
        found.append((page, kind, msg))
    return found


def contact_sheets(pngs, out_dir, per_sheet=6):
    """Tile pages 2x3 per sheet when ImageMagick is available; returns the sheet paths."""
    tool = shutil.which("magick") or shutil.which("montage")
    if not tool:
        return []
    cmd = [tool, "montage"] if tool.endswith("magick") else [tool]
    sheets = []
    for i in range(0, len(pngs), per_sheet):
        out = out_dir / f"sheet-{i // per_sheet + 1:02d}.png"
        subprocess.run(cmd + [str(p) for p in pngs[i:i + per_sheet]] +
                       ["-tile", "2x3", "-geometry", "+6+6", "-background", "#888888", str(out)],
                       capture_output=True)
        if out.exists():
            sheets.append(out)
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slides_tex", help="<slides>/main.tex")
    ap.add_argument("--dpi", type=int, default=100, help="PNG resolution for review (default 100)")
    a = ap.parse_args()

    tex = Path(a.slides_tex).resolve()
    slides = tex.parent
    build = slides / "build" / "slides"
    ok, pdf, log = latexmk(tex, build)
    if not ok:
        print(f"COMPILE ERROR. Log: {log}")
        for e in log_errors(log):
            print(f"  {e}")
        sys.exit(2)

    shutil.copy2(pdf, slides / tex.with_suffix(".pdf").name)
    pages_dir = slides / "build" / "pages"
    shutil.rmtree(pages_dir, ignore_errors=True)
    pages_dir.mkdir(parents=True)
    subprocess.run(["pdftoppm", "-r", str(a.dpi), "-png", str(pdf), str(pages_dir / "page")], check=True)
    pngs = sorted(pages_dir.glob("page-*.png"))
    sheets = contact_sheets(pngs, pages_dir)

    fr = frames(tex)
    if len(fr) != len(pngs):
        print(f"note: {len(fr)} frames in source but {len(pngs)} pages; page→frame titles may be offset")

    def label(page):
        return f"page {page}: {fr[page - 1]['title']}" if page <= len(fr) else f"page {page}"

    problems = [(p, k, m) for p, k, m in warnings_by_page(log)]
    problems += [(i + 1, "text-heavy", f"a list has {f['bullets']} bullets (max {MAX_BULLETS}); split the frame")
                 for i, f in enumerate(fr) if f["bullets"] > MAX_BULLETS]
    problems += [(i + 1, "structure", "remove the References frame; per-frame source lines are the only citations")
                 for i, f in enumerate(fr) if f["title"].lower().startswith("references")]
    if fr and fr[-1]["title"] != CLOSING_TITLE:
        problems.append((len(fr), "structure", f"the last frame must be titled '{CLOSING_TITLE}'"))

    print(f"PDF: {slides / tex.with_suffix('.pdf').name}  ({len(pngs)} pages)")
    if sheets:
        print(f"Contact sheets for visual review (6 pages each): {pages_dir}/sheet-*.png")
    else:
        print(f"Page images for visual review: {pages_dir}/page-*.png")
    if not problems:
        print("CLEAN: no overflow, missing glyph, undefined citation/reference, text-heavy frame, or structure problem.")
        sys.exit(0)
    print("FIX:")
    for page, kind, msg in sorted(problems):
        print(f"  [{kind}] {label(page)} — {msg}")
    sys.exit(1)


if __name__ == "__main__":
    main()
