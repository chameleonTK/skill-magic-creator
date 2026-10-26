---
name: report-to-slides
description: Turn a LaTeX report into a LaTeX Beamer slide deck styled by a reference slide-guideline .tex, using only the report's content and illustrations. Use when asked to make slides or a presentation from a LaTeX report, or to convert a report into Beamer following a slide template or guideline.
---

# Report to slides

You are the **orchestrator**. You run the gate, the user checkpoint and the hand-over yourself, and delegate the three heavy steps to sub-agents, each running at a fixed effort.

**Inputs**
- `REPORT`: the report's main `.tex`.
- `GUIDE`: the guideline's main `.tex`.

If either is missing, ask for it.

**Paths**
- `<skill>` is the directory containing this file (use its absolute path in every brief).
- Output goes to `SLIDES = <REPORT dir>/../slides/` unless the user names another directory.
- Every step follows [references/ground-rules.md](references/ground-rules.md).

## Delegation

| Step | Sub-agent | Effort | Instructions |
|---|---|---|---|
| Outline | `report-to-slides-outliner` | high | `references/step-outline.md` |
| Build | `report-to-slides-builder` | medium | `references/step-build.md` |
| Check | `report-to-slides-checker` | high | `references/step-check.md` |

Spawn each step's sub-agent **by its name**; its definition pins the effort.
- Claude Code: the Agent tool with `subagent_type` set to the name.
- Codex: ask Codex to spawn the custom agent with that name.

If the named agent is not installed, spawn a general-purpose sub-agent with the effort from the table: the Agent tool's `effort` parameter in Claude Code. If no way to set a sub-agent's effort exists, run the step yourself and tell the user it ran at your own effort.

**Brief** for every dispatch, as absolute paths: `<skill>`, `REPORT`, `GUIDE`, `SLIDES`, `SLIDES/build/manifest.json`, and the step file. Add the user's requested changes when re-dispatching. Wait for the sub-agent to finish before the next step: the files on disk are the hand-off.

## 1. Gate (you)

```
python3 <skill>/scripts/preflight.py REPORT GUIDE [--slides SLIDES]
```

It checks every file both documents reference, then compiles both into `SLIDES/build/` and writes `SLIDES/build/manifest.json`.

- **Exit 1 (missing files):** show the user the list, ask them to supply the files, and rerun. The process starts only after the gate passes.
- **Exit 2 (compile error):** show the error lines and ask the user.
- **Exit 3 (`SLIDES/main.tex` exists):** ask the user whether to overwrite it or use another `--slides` directory.

**Done when** the script exits 0.

## 2. Outline (outliner, high)

Dispatch `report-to-slides-outliner`. **Done when** `SLIDES/outline.md` exists and the sub-agent has reported its summary.

## 3. Checkpoint (you, with the user)

Give the user the outline path and the sub-agent's summary: slide count, skipped topics, unused illustrations, open questions. Ask them to approve or edit.
- Small edits the user dictates (a cell, a skip toggle): apply them to `outline.md` yourself.
- Structural changes (re-plan a section, different skip criteria): re-dispatch the outliner with the request.

Continue only on explicit approval. Then set the outline's status line to approved.

## 4. Build (builder, medium)

Dispatch `report-to-slides-builder`. **Done when** the sub-agent reports `build_check.py` exit 0.

## 5. Check (checker, high)

Dispatch `report-to-slides-checker`. **Done when** the sub-agent reports `build_check.py` exit 0 and every page passed its visual review.

## 6. Hand over (you)

Report:
- the paths of `SLIDES/main.tex` and `SLIDES/main.pdf`;
- the page count;
- the skipped topics;
- which figures were cropped instead of copied as TikZ;
- any outline rows that were split or changed during building or checking.
