# Slide outline: <report title>

Report: `<path>` · Guideline: `<path>`
Status: **DRAFT, awaiting approval** (edit any cell; LaTeX is written only after approval)

## Branding

Values come from the report. Write `TODO` when the report has none.

| Slot | Value | Taken from |
|---|---|---|
| Cover title | | report title |
| Cover subtitle | | report subtitle |
| Cover tagline | | report keywords |
| Cover footer label | | unit + number, e.g. `WEEK 01` |
| Footline left | | report title, uppercase |
| Footline right | | unit + number, e.g. `WEEK 01` |
| PDF title / author | | report title / report author |

## Color mapping

Report colors used by copied figures, aliased to guideline colors by role.

| Report color | Role in report | Guideline color |
|---|---|---|
| `aieprimary` | primary / structure | `WDTeal` |

## Slides

Every report `\section` and `\subsection` appears here as *keep* or *skip*. The last row is always Key Takeaways; there is no References row.
Layout = a pattern from the guideline. Illustration = the report's figure, table, image, equation or listing (by caption or label), or `bullets`.

| # | Section | Frame title | Layout | Illustration | Keep / Skip | Skip reason |
|---|---|---|---|---|---|---|
| 1 | | Cover | cover | | keep | |
| 2 | 01 / … | … | figure-full | Fig. "ขั้น Embedding…" (TikZ copy) | keep | |
| 3 | 01 / … | … | bullets | bullets | skip | math derivation |
| N | (last section) | Key Takeaways | key takeaways | bullets from the conclusion and key-takeaway boxes | keep | |

## Unused illustrations

- `<caption or label>` (§x.y): reason it is left out
