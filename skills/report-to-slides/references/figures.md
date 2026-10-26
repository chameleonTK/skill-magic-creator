# Report illustrations on slides

Run through these in order for each illustration the outline uses.

## 1. Images (`\includegraphics`)

Copy the file (its path is in `build/manifest.json` → `report.images`) to `assets/figures/` and include it with
`\includegraphics[width=<w>,height=<h>,keepaspectratio]{assets/figures/<file>}`.

If text inside the image is unreadable at the planned size, give each image a larger slot (e.g. one frame per image beside its facts from the report) rather than tiling several small ones. An image with a white background reads better framed: `{\setlength\fboxsep{0pt}\color{<guideline rule color>}\fbox{\includegraphics[width=\dimexpr\linewidth-2\fboxrule\relax]{…}}}`.

## 2. TikZ figures: copy the source

- Copy the `tikzpicture`, and any `\resizebox`/`adjustbox` wrapper, verbatim. Drop the `figure` float and `\caption`. Caption wording may become the frame title or a `\takeaway`.
- Into the `% report-to-slides additions` block, copy everything the code depends on: macros (`\newcommand`), `\tikzset` styles, `\usetikzlibrary` libraries, packages (e.g. `pgfplots` + `\pgfplotsset{compat=…}`), column types. They live in the report preamble or the local `.sty` files listed in `manifest.json` → `report.local_styles`.
- Colors: alias every report color the copied code uses to a guideline color by role, e.g. `\colorlet{aieprimary}{WDTeal}`. If the report and the guideline both define a color name, keep the guideline's definition. Record the mapping in the outline.
- A copied figure that contains `#` (e.g. a parameterised style such as `bar/.style={draw=#1}`) needs `\begin{frame}[fragile]`. Otherwise Beamer doubles the `#` and the compile fails with "Illegal parameter number".
- Fit: the frame body is about `\textwidth` × `0.72\textheight` under the title. If the figure is too wide, wrap it in `\resizebox{\linewidth}{!}{…}` (or `{!}{<height>}` when it's too tall).

## 3. Crop fallback

Crop the figure from the compiled report instead when any of these hold:
- it still overflows after resizing;
- the scale factor would put its smallest text below about 7pt (scale × the figure's font size, e.g. `\small` ≈ 10.95pt at 12pt base);
- it fails to compile inside Beamer;
- on the rendered page, its boxes re-wrap or hyphenate differently from the report (the slide font's metrics differ, so fixed `text width` nodes break lines in new places), or its text reads clearly smaller than the report's version.

Wide or tall figures read best given the whole frame, or a ≈ .58 column beside a single card.

```
python3 <skill>/scripts/crop_figure.py <manifest report.pdf> --caption "<plain-text run from the caption>" --out <slides>/assets/figures/<name>.png
```

- Caption label text (e.g. `รูปที่ 9:`) or a stretch of plain words matches best. Avoid math and cited text.
- Use `--side below` for illustrations whose caption sits above them (tables).
- **Open the PNG.** It must hold the whole figure and nothing else. If it doesn't, rerun with `--page` and `--top/--bottom/--left/--right` (points, as printed by the script).
- Include it like an image (step 1) and list it as "cropped" in the outline.

## Tables

Copy the `tabular`/`tabularx` with only the report's rows and columns. Set widths against `\linewidth`, keep the guideline's table style (e.g. booktabs, `\arraystretch`), and split long tables across frames with the header repeated.

## Equations and code

- Equations: copy the display verbatim, 1–2 lines.
- Code: copy the listing verbatim, ≤ 12 lines, inside `\begin{frame}[fragile]`, using the guideline's `lstset`.
