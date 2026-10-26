# skill-magic-creator

## report-to-slides

Turns a LaTeX report into a Beamer deck styled by a LaTeX slide guideline. Source: `skills/report-to-slides/`.

Requirements: Python 3.9+, TeX Live with `latexmk`, and poppler (`pdftoppm`, `pdftotext`).

### Use in this project

These are already linked:
- Claude Code: `.claude/skills/report-to-slides`
- Codex: `.agents/skills/report-to-slides`

Ask either agent for something like: "make slides from `examples/week01-llm-agentic-fundamentals/report/main.tex` using the guideline `examples/slide-guideline-latex/main.tex`".

### Install for all projects

```sh
S="$PWD/skills/report-to-slides"
ln -s "$S" ~/.claude/skills/report-to-slides   # Claude Code
ln -s "$S" ~/.codex/skills/report-to-slides    # Codex
mkdir -p ~/.claude/agents ~/.codex/agents
for r in outliner builder checker; do
  ln -s "$S/agents/claude/report-to-slides-$r.md"   ~/.claude/agents/
  ln -s "$S/agents/codex/report-to-slides-$r.toml"  ~/.codex/agents/
done
```

Newer Codex versions also read `~/.agents/skills/`.

### Effort per step

The skill's orchestrator runs at whatever effort you invoke it with. It delegates three steps to sub-agents whose definitions pin their effort:

| Step | Agent | Effort |
|---|---|---|
| Outline | `report-to-slides-outliner` | high |
| Build | `report-to-slides-builder` | medium |
| Check | `report-to-slides-checker` | high |

To change a step's effort, edit `effort:` in `agents/claude/*.md` and `model_reasoning_effort` in `agents/codex/*.toml`. In Claude Code, the `CLAUDE_CODE_EFFORT_LEVEL` environment variable overrides these when set.
