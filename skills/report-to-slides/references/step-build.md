# Step: Build

Your brief gives `<skill>`, `REPORT`, `GUIDE`, `SLIDES` and the manifest path. Follow [ground-rules.md](ground-rules.md). The approved `SLIDES/outline.md` is your plan; read it first, then the report sections and guideline frames each row needs.

## 1. Assets

- Copy each guideline asset directory (`manifest.json` → `guideline.asset_roots`, e.g. `assets/`) into `SLIDES/` whole, so fonts travel with their licenses.
- Put report images and crops in `SLIDES/assets/figures/`.
- `SLIDES/` must compile on its own and upload to Overleaf as is.

## 2. Preamble

Copy the guideline preamble verbatim, then replace only the branding slots with the approved outline values ([layouts.md](layouts.md#branding-slots)). After it, add a block headed `% report-to-slides additions` containing:
- the `\skipcross` macro ([skipped-slide.md](skipped-slide.md));
- the report macros, styles and packages that copied figures need;
- the color aliases from the outline.

## 3. Frames

Write one frame per outline row, in order.
- Cover: the guideline's cover pattern.
- Sections: `\section{NN / <title>}`.
- Illustrations: follow [figures.md](figures.md).
- Skipped topics: follow [skipped-slide.md](skipped-slide.md).
- Citations: follow [layouts.md](layouts.md#citations).
- Closing: the Key Takeaways frame is the last frame ([layouts.md](layouts.md#closing-frame)).
- Notes: every kept frame gets a `\note{}` holding the report detail cut from the slide, condensed in report wording.

## 4. Compile clean

```
python3 <skill>/scripts/build_check.py SLIDES/main.tex
```

Fix every listed problem and rerun. **Done when** it exits 0.

## 5. Report back

Return: the page count, the `build_check.py` result, figures cropped instead of copied, and any outline row you split or changed (also record it in `outline.md`).
