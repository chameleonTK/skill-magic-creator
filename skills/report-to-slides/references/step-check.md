# Step: Check

Your brief gives `<skill>`, `REPORT`, `GUIDE`, `SLIDES` and the manifest path. Follow [ground-rules.md](ground-rules.md). `SLIDES/main.tex` compiles clean; your job is the review a script cannot do.

## 1. Render

```
python3 <skill>/scripts/build_check.py SLIDES/main.tex
```

## 2. Review every page

Open every contact sheet `SLIDES/build/pages/sheet-*.png` (or every `page-*.png` when no sheets are produced). Check each page:
- content clear of the footline, nothing clipped or overlapping;
- Thai and other combining marks intact;
- figure text legible, boxes wrapping as in the report;
- the frame reads as visual-first;
- every word and number traceable to the report (spot-check against `REPORT`).

Fix problems in `main.tex` (see [figures.md](figures.md) for the crop fallback and image sizing) and rerun the script. Splitting an outline row into several frames to make it readable is fine; record it in `outline.md`.

**Done when** the script exits 0 and every page passes on a fresh render.

## 3. Report back

Return: the page count, what you changed and why (per page), figures cropped instead of copied, and outline rows split or changed.
