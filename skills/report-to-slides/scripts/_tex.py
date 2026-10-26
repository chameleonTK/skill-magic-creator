"""Shared LaTeX helpers for the report-to-slides scripts (stdlib only)."""
import re
import subprocess
from pathlib import Path

ENGINE_FLAGS = {"xelatex": "-xelatex", "lualatex": "-lualatex", "pdflatex": "-pdf"}


def strip_comments(text):
    return re.sub(r"(?<!\\)%.*", "", text)


def detect_engine(tex_path, extra_files=()):
    """Magic comment, then fontspec use in the main file or its local styles."""
    raw = Path(tex_path).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"%\s*!TeX\s+(?:TS-)?program\s*=\s*(\w+)", raw, re.I)
    if m and m.group(1).lower() in ENGINE_FLAGS:
        return m.group(1).lower()
    for f in [tex_path, *extra_files]:
        text = strip_comments(Path(f).read_text(encoding="utf-8", errors="replace"))
        if re.search(r"\\(?:usepackage|RequirePackage)(\[[^\]]*\])?\{[^}]*fontspec|\\setmainfont|\\RequireXeTeX", text):
            return "xelatex"
    return "pdflatex"


def latexmk(tex_path, outdir, engine=None):
    tex_path = Path(tex_path).resolve()
    outdir = Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    engine = engine or detect_engine(tex_path)
    cmd = ["latexmk", ENGINE_FLAGS[engine], "-interaction=nonstopmode", "-halt-on-error",
           "-file-line-error", f"-outdir={outdir}", tex_path.name]
    proc = subprocess.run(cmd, cwd=tex_path.parent, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    pdf = outdir / (tex_path.stem + ".pdf")
    log = outdir / (tex_path.stem + ".log")
    return proc.returncode == 0 and pdf.exists(), pdf, log


def log_errors(log_path, limit=15):
    if not Path(log_path).exists():
        return ["(no log file produced)"]
    lines = Path(log_path).read_text(encoding="utf-8", errors="replace").splitlines()
    out = []
    for i, line in enumerate(lines):
        if line.startswith("! ") or re.match(r"^[^:\s]+\.\w+:\d+: ", line):
            out.append(" | ".join(l.strip() for l in lines[i:i + 3] if l.strip()))
    return out[:limit] or [l for l in lines[-20:]]


MISSING_PATTERNS = [
    r"Unable to load picture or PDF file '([^']+)'",
    r"File `([^']+)' not found",
    r"The font \"([^\"]+)\" cannot be found",
    r"I couldn't open (?:database )?file ([^\s]+)",
]


def log_missing_files(log_path):
    if not Path(log_path).exists():
        return []
    text = Path(log_path).read_text(encoding="utf-8", errors="replace").replace("\n", "")
    found = []
    for pat in MISSING_PATTERNS:
        found += [m.group(1) for m in re.finditer(pat, text)]
    return sorted(set(found))
