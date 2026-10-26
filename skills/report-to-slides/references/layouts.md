# Layouts

The guideline is the only source of styling. Use its colors, fonts, component macros (e.g. `\card`, `\takeaway`, `\smalllabel`, `\source`) and frame patterns. Any color or size you write must be one of the guideline's own tokens.

## Build the catalog

Read every frame of the guideline and name each distinct pattern. Typical patterns include cover, section divider, bullets + card in two columns, side-by-side cards, three cards, full-width TikZ diagram, code + expected output, table, chart, block/activity, and source line. Record the exact LaTeX skeleton of each one: column widths, spacing, which macros it uses. Copy the skeleton only. The guideline's demo text never reaches the deck.

## Match content to a pattern

| Report content | Pattern |
|---|---|
| One figure or image | full-width figure, optionally with one `\takeaway` sentence taken from the report |
| Figure + 2–3 points about it | two columns: figure ≈ .58, bullets ≈ .38 |
| Table | table pattern; split rows across frames rather than shrinking |
| 2–3 parallel concepts in prose | side-by-side cards holding report phrases |
| Code (≤ 12 lines) | code pattern, `[fragile]` frame |
| Short equation (≤ 2 lines) | centered display + ≤ 2 bullets |
| Prose only | bullets: ≤ 4 per list, one line each; split into more frames when needed |
| Major report `\section` change | section divider (only at major transitions) |

Diagrams, cards and charts hold the report's own illustrations and words. Bullets stay as bullets.

## Branding slots

Find the guideline's hardcoded identity strings:
- text inside the footline template;
- labels drawn by cover decoration macros (e.g. a cover footer);
- `\title` / `\subtitle`;
- `pdftitle` / `pdfauthor` in `\hypersetup`;
- the cover frame's title, subtitle and tagline lines.

Replace each with its value from the approved outline. Delete cover lines that only describe the guideline itself (e.g. "LaTeX Beamer / 16:9").

## Sections

`\section{NN / <report \section title>}`, numbered in report order, so the guideline's frame-title template shows it as the section label.

## Citations

When a frame's content carries a `\cite{key}` in the report, put one source line on that frame using the guideline's source component (e.g. `\source{url}{Publisher, Title (year)}`), built from `refs.bib`. Join multiple keys on one line with ` • `. An entry without a URL gets the same line as plain text. When the guideline's component takes exactly one link, add a plain-text twin to the additions block that copies its font and color, e.g. `\newcommand{\sourcetext}[1]{\vfill{\fontsize{7}{9}\selectfont\color{WDMuted}Source: #1\par}}`, and use `\href` inside it for the entries that have URLs. The per-frame source lines are the only citations: the deck has no References frame.

## Closing frame

The deck always ends with one frame titled exactly `Key Takeaways`, placed after the last report section's frames.
- Content: the report's conclusion/summary section and its key-takeaway boxes, condensed in report wording. When the report has a conclusion section, its content lives here rather than in a separate summary frame.
- Layout: bullets, ≤ 4 per list; use two columns (or two stacked lists) when more points are needed, one line per bullet.
- Nothing follows it.
