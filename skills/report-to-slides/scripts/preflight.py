#!/usr/bin/env python3
"""Gate for report-to-slides.

Checks that every file the report and the guideline reference exists, then
compiles both into <slides>/build/. Writes <slides>/build/manifest.json.

Exit codes: 0 ready | 1 missing files/tools | 2 compile failed | 3 slides/main.tex exists
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from _tex import detect_engine, latexmk, log_errors, log_missing_files, strip_comments

GRAPHIC_EXTS = ["", ".pdf", ".png", ".jpg", ".jpeg", ".eps"]
FONT_CMDS = r"\\(?:set(?:main|sans|mono|math)font|newfontfamily\s*\\\w+|setfontfamily\s*\\\w+|fontspec)"
FONT_KEYS = ("UprightFont", "BoldFont", "ItalicFont", "BoldItalicFont", "SlantedFont", "BoldSlantedFont")


def kpse(name):
    if not shutil.which("kpsewhich"):
        return None
    out = subprocess.run(["kpsewhich", name], capture_output=True, text=True).stdout.strip()
    return out or None


def usable(arg):
    return arg and "#" not in arg and "\\" not in arg


class Scanner:
    def __init__(self, main):
        self.main = Path(main).resolve()
        self.base = self.main.parent
        self.seen = set()
        self.local = {}
        self.images = []
        self.bibs = []
        self.styles = []
        self.missing = []
        self.unverified = []
        self.graphicspath = []

    def find_local(self, ref, exts, here):
        for root in [self.base, here, *self.graphicspath]:
            for ext in exts:
                p = (root / (ref + ext)).resolve()
                if p.is_file():
                    return p
        return None

    def add_local(self, ref, path):
        self.local[str(path)] = ref

    def scan(self, path):
        path = Path(path).resolve()
        if path in self.seen:
            return
        self.seen.add(path)
        text = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        here = path.parent
        where = path.name

        for m in re.finditer(r"\\graphicspath\s*\{((?:\{[^}]*\})+)\}", text):
            self.graphicspath += [(self.base / d).resolve() for d in re.findall(r"\{([^}]*)\}", m.group(1))]

        for m in re.finditer(r"\\documentclass\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", text):
            self.package(m.group(1).strip(), ".cls", here, where)

        for m in re.finditer(r"\\(?:usepackage|RequirePackage)\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", text):
            for name in m.group(1).split(","):
                if usable(name.strip()):
                    self.package(name.strip(), ".sty", here, where)

        for m in re.finditer(r"\\(?:input|include|subfile)\s*\{([^}]*)\}", text):
            ref = m.group(1).strip()
            if not usable(ref):
                continue
            p = self.find_local(ref, ["", ".tex"], here)
            if p:
                self.add_local(ref, p)
                if p.suffix in (".tex", ".sty", ".cls", ""):
                    self.scan(p)
            elif not kpse(ref) and not kpse(ref + ".tex"):
                self.missing.append(f"{ref}  (\\input in {where})")

        for m in re.finditer(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", text):
            ref = m.group(1).strip()
            if not usable(ref):
                continue
            p = self.find_local(ref, GRAPHIC_EXTS, here)
            if p:
                self.add_local(ref, p)
                self.images.append({"ref": ref, "path": str(p), "in": where})
            else:
                self.missing.append(f"{ref}  (\\includegraphics in {where})")

        for m in re.finditer(r"\\bibliography\s*\{([^}]*)\}", text):
            for name in m.group(1).split(","):
                self.bib(name.strip() + ".bib", here, where)
        for m in re.finditer(r"\\addbibresource\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", text):
            self.bib(m.group(1).strip(), here, where)

        for m in re.finditer(FONT_CMDS + r"\s*(?:\[([^\]]*)\])?\s*\{([^}]*)\}\s*(?:\[([^\]]*)\])?", text):
            self.font(m.group(2).strip(), (m.group(1) or "") + "," + (m.group(3) or ""), where)

    def package(self, name, ext, here, where):
        ref = name if name.endswith(ext) else name + ext
        p = self.find_local(ref, [""], here)
        if p:
            self.add_local(ref, p)
            self.styles.append(str(p))
            self.scan(p)
        elif "/" in name:
            self.missing.append(f"{ref}  (\\usepackage in {where})")
        elif not kpse(ref):
            self.missing.append(f"{ref}  (TeX package not installed; used in {where})")

    def bib(self, ref, here, where):
        p = self.find_local(ref, [""], here)
        if p:
            self.add_local(ref, p)
            self.bibs.append(str(p))
        elif not kpse(ref):
            self.missing.append(f"{ref}  (bibliography in {where})")

    def font(self, name, opts, where):
        kv = dict(
            (k.strip(), v.strip()) for k, v in
            (o.split("=", 1) for o in re.split(r",\s*", opts.replace("\n", " ")) if "=" in o)
        )
        folder = kv.get("Path")
        ext = kv.get("Extension", "")
        if "\\" in opts or "\\" in name:
            self.unverified.append(f"font '{name}' set via macros ({where}); the compile step verifies it")
            return
        if not folder and not re.search(r"\.(ttf|otf)$", name, re.I):
            self.unverified.append(f"system font '{name}' ({where}); the compile step verifies it")
            return
        files = {kv[k] for k in FONT_KEYS if k in kv}
        if "UprightFont" not in kv:
            files.add(name)
        for f in files:
            f = f.replace("*", name)
            ref = (folder or "") + f + ("" if Path(f).suffix else ext)
            p = self.find_local(ref, [""], self.base)
            if p:
                self.add_local(ref, p)
            elif not folder and kpse(f):
                continue
            else:
                self.missing.append(f"{ref}  (font in {where})")

    def manifest(self, pdf, engine):
        roots = sorted({
            Path(p).relative_to(self.base).parts[0]
            for p in self.local if Path(p).is_relative_to(self.base) and Path(p) != self.main
        })
        outside = sorted(p for p in self.local if not Path(p).is_relative_to(self.base))
        return {
            "main": str(self.main),
            "dir": str(self.base),
            "engine": engine,
            "pdf": str(pdf),
            "asset_roots": roots,
            "files_outside_dir": outside,
            "local_styles": self.styles,
            "images": self.images,
            "bib": self.bibs,
        }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", help="report main .tex")
    ap.add_argument("guideline", help="slide guideline main .tex")
    ap.add_argument("--slides", help="output slides dir (default: <report dir>/../slides)")
    a = ap.parse_args()

    report = Path(a.report).resolve()
    guide = Path(a.guideline).resolve()
    slides = Path(a.slides).resolve() if a.slides else report.parent.parent / "slides"

    if (slides / "main.tex").exists():
        print(f"STOP: {slides / 'main.tex'} already exists. Ask the user: overwrite, or pick another --slides dir.")
        sys.exit(3)
    if (slides / "outline.md").exists():
        print(f"NOTE: {slides / 'outline.md'} exists from an earlier run. Ask the user whether to reuse it.")

    created = not slides.exists()

    def fail(code):
        if created:
            shutil.rmtree(slides, ignore_errors=True)
        sys.exit(code)

    missing = [f"{t}  (command-line tool)" for t in ("latexmk", "pdftoppm", "pdftotext") if not shutil.which(t)]
    scanners = {}
    for label, path in (("report", report), ("guideline", guide)):
        if not path.is_file():
            missing.append(f"{path}  ({label} main file)")
            continue
        s = Scanner(path)
        s.scan(path)
        scanners[label] = s
        missing += [f"[{label}] {m}" for m in s.missing]
        for u in s.unverified:
            print(f"[{label}] info: {u}")

    if missing:
        print("MISSING — ask the user to supply these, then rerun:")
        for m in missing:
            print(f"  - {m}")
        fail(1)

    build = slides / "build"
    manifest = {"slides_dir": str(slides)}
    for label, s in scanners.items():
        engine = detect_engine(s.main, s.styles)
        print(f"Compiling {label} ({engine}) ...", flush=True)
        ok, pdf, log = latexmk(s.main, build / label, engine)
        if not ok and log_missing_files(log):
            print(f"MISSING (found while compiling {label}) — ask the user to supply these, then rerun:")
            for f in log_missing_files(log):
                print(f"  - {f}  (path as LaTeX resolved it from {s.base})")
            fail(1)
        if not ok:
            print(f"COMPILE FAILED: {label} ({s.main}). Log: {log}")
            for e in log_errors(log):
                print(f"  {e}")
            fail(2)
        manifest[label] = s.manifest(pdf, engine)

    (build / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"READY. Manifest: {build / 'manifest.json'}")
    print(f"Report PDF (for cropping): {manifest['report']['pdf']}")


if __name__ == "__main__":
    main()
