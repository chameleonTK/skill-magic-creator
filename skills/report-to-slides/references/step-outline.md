# Step: Outline

Your brief gives `<skill>`, `REPORT`, `GUIDE`, `SLIDES` and the manifest path. Follow [ground-rules.md](ground-rules.md).

## 1. Read

Read the following in full:
- `REPORT`, including `\input` files;
- its `.bib`;
- the report's local styles (`manifest.json` → `report.local_styles`);
- `GUIDE`, and [layouts.md](layouts.md) for how its frames become a layout catalog.

**Done when** you can list every report `\section`/`\subsection`, every figure, table, image, listing and equation with its location, and every guideline layout pattern and component macro.

## 2. Write the outline

Write `SLIDES/outline.md` from [outline-template.md](outline-template.md):
- branding values from the report (`TODO` where none exists);
- the color mapping, by role, for every report color a planned figure uses;
- one row per planned frame, covering every `\section` and `\subsection`, ending with the Key Takeaways row ([layouts.md](layouts.md#closing-frame)) and no References row;
- the unused illustrations, each with its reason.

Propose **skip** for a topic whose message cannot be shown with one report illustration or ≤ 4 short bullets. Typical cases: multi-step math derivations, long code or configuration walk-throughs, dense implementation detail.

If the brief carries user-requested changes, apply them to the existing outline instead of starting over.

**Done when** the file exists, every `\section`/`\subsection` has a row, and the status line reads "DRAFT, awaiting approval".

## 3. Report back

Return: the outline path, the frame count, the skipped topics with reasons, the unused illustrations, and any open question for the user (e.g. a report color with no guideline equivalent). Write no LaTeX.
