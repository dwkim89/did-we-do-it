#!/usr/bin/env python3
"""Validate, compile, preflight, and render a weekly Beamer deck."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REQUIRED_ROLES = {
    "goal", "motivation", "current-status", "follow-up", "differential",
    "attempts", "evidence", "reasoning", "next", "conclusion",
}
CORE_ROLE_SEQUENCE = ("goal", "current-status", "attempts", "next", "conclusion")
FRAME_RE = re.compile(r"\\begin\{frame\}(?:\[[^]]*\])?(?:\{([^}]*)\})?(.*?)\\end\{frame\}", re.S)
BERKELEY_STYLE_MARKERS = {
    "TeX Gyre Heros sans-serif font": r"\setsansfont{TeX Gyre Heros}",
    "Berkeley blue": r"\definecolor{berkeleyblue}{HTML}{003262}",
    "California gold": r"\definecolor{californiagold}{HTML}{FDB515}",
    "bold deck title": r"\setbeamerfont{title}{series=\bfseries}",
    "bold frame titles": r"\setbeamerfont{frametitle}{series=\bfseries}",
    "blue half-rule": r"\color{berkeleyblue}\rule{0.5\textwidth}{0.8pt}",
    "gold half-rule": r"\color{californiagold}\rule{0.5\textwidth}{0.8pt}",
    "UC Berkeley title logo": "assets/uc-berkeley-logo.png",
    "Berkeley Lab title logo": "assets/berkeley-lab-logo.png",
}


def expanded_source(path: Path, seen: set[Path] | None = None) -> str:
    """Expand repository-local TeX inputs for structural validation."""
    seen = seen or set()
    resolved = path.resolve()
    if resolved in seen:
        return ""
    seen.add(resolved)
    source = resolved.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        target = match.group(1)
        candidate = (resolved.parent / target).resolve()
        if candidate.suffix == "":
            candidate = candidate.with_suffix(".tex")
        if not candidate.is_file():
            return match.group(0)
        return expanded_source(candidate, seen)

    return re.sub(r"\\input\{([^}]+)\}", replace, source)


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False, env=env,
    )


def validate_source(path: Path, brand_profile: str = "none") -> list[str]:
    source = expanded_source(path)
    errors: list[str] = []
    roles = {match.lower() for match in re.findall(r"^\s*%\s*role:\s*([\w-]+)\s*$", source, re.M)}
    missing = sorted(REQUIRED_ROLES - roles)
    if missing:
        errors.append("missing narrative role markers: " + ", ".join(missing))
    role_positions = {
        role: source.find(f"role: {role}") for role in CORE_ROLE_SEQUENCE
    }
    present_positions = [role_positions[role] for role in CORE_ROLE_SEQUENCE if role_positions[role] >= 0]
    if present_positions != sorted(present_positions):
        errors.append(
            "core narrative roles must appear in order: " + ", ".join(CORE_ROLE_SEQUENCE)
        )
    if re.search(r"\\(?:tiny|scriptsize)\b", source):
        errors.append("tiny or scriptsize body text is not allowed")

    frames = FRAME_RE.findall(source)
    if not frames:
        errors.append("no Beamer frames found")
    for index, (title, body) in enumerate(frames, 1):
        if not title and "\\titlepage" not in body:
            errors.append(f"frame {index} has no title")
        plot_count = len(re.findall(r"\\includegraphics\b", body))
        if plot_count > 2:
            errors.append(f"frame {index} has {plot_count} plots; maximum is 2")
        item_count = len(re.findall(r"\\item\b", body))
        if item_count > 6:
            errors.append(f"frame {index} has {item_count} items; maximum is 6")
    if brand_profile == "berkeley":
        for label, marker in BERKELEY_STYLE_MARKERS.items():
            if marker not in source:
                errors.append(f"Berkeley profile is missing {label}")
        for relative in (
            "assets/uc-berkeley-logo.png",
            "assets/berkeley-lab-logo.png",
        ):
            if not (path.parent / relative).is_file():
                errors.append(f"Berkeley profile requires approved logo asset: {relative}")
    return errors


def check_embedded_fonts(pdf: Path) -> list[str]:
    pdffonts = shutil.which("pdffonts")
    if not pdffonts:
        return []
    result = run([pdffonts, pdf.name], pdf.parent)
    if result.returncode:
        return ["pdffonts could not inspect the compiled PDF"]
    for line in result.stdout.splitlines()[2:]:
        flags = re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line)
        if flags and flags.group(1) == "no":
            return ["the compiled PDF contains a font that is not embedded"]
    return []


def preflight_pdf(pdf: Path) -> list[str]:
    errors: list[str] = []
    qpdf = shutil.which("qpdf")
    if qpdf:
        result = run([qpdf, "--check", pdf.name], pdf.parent)
        if result.returncode:
            errors.append("qpdf structural check failed:\n" + result.stdout.strip())
    gs = shutil.which("gs")
    if gs:
        result = run(
            [gs, "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=nullpage", pdf.name],
            pdf.parent,
        )
        if result.returncode:
            errors.append("Ghostscript could not render every PDF page:\n" + result.stdout.strip())
    errors.extend(check_embedded_fonts(pdf))
    return errors


def compile_tex(path: Path, engine: str) -> list[str]:
    latexmk = shutil.which("latexmk")
    if not latexmk:
        return ["latexmk is unavailable; install a TeX distribution before compiling"]
    mode = {"lualatex": "-lualatex", "xelatex": "-xelatex", "pdflatex": "-pdf"}[engine]
    environment = os.environ.copy()
    with tempfile.TemporaryDirectory(prefix="didwedoit-tex-cache-") as cache:
        if engine == "lualatex":
            environment["TEXMFVAR"] = cache
            environment["TEXMFCACHE"] = cache
        result = run(
            [latexmk, mode, "-interaction=nonstopmode", "-halt-on-error", path.name],
            path.parent, environment,
        )
    if result.returncode:
        tail = "\n".join(result.stdout.splitlines()[-25:])
        return [f"LaTeX compilation failed:\n{tail}"]
    log_path = path.with_suffix(".log")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else result.stdout
    errors: list[str] = []
    if "Overfull \\hbox" in log or "Overfull \\vbox" in log:
        errors.append("LaTeX reports an overfull box; revise the affected frame")
    pdf = path.with_suffix(".pdf")
    if not pdf.is_file():
        errors.append("LaTeX completed without producing the expected PDF")
    else:
        errors.extend(preflight_pdf(pdf))
    return errors


def render_pdf(pdf: Path, output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    gs = shutil.which("gs")
    if gs:
        pattern = str(output_dir / "slide-%03d.png")
        result = run(
            [gs, "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=pngalpha", "-r144", f"-sOutputFile={pattern}", str(pdf)],
            pdf.parent,
        )
    else:
        pdftoppm = shutil.which("pdftoppm")
        if not pdftoppm:
            return ["neither Ghostscript nor pdftoppm is available for page rendering"]
        result = run([pdftoppm, "-png", "-r", "144", str(pdf), str(output_dir / "slide")], pdf.parent)
    if result.returncode:
        return ["PDF preview rendering failed:\n" + result.stdout.strip()]
    if not list(output_dir.glob("slide-*.png")):
        return ["preview rendering produced no PNG pages"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tex", type=Path)
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--engine", choices=("lualatex", "xelatex", "pdflatex"), default="lualatex")
    parser.add_argument("--brand-profile", choices=("none", "berkeley"), default="none")
    parser.add_argument("--render-dir", type=Path)
    args = parser.parse_args()
    path = args.tex.expanduser().resolve()
    errors = validate_source(path, args.brand_profile)
    if args.compile and not errors:
        errors.extend(compile_tex(path, args.engine))
    if args.render_dir and not errors:
        pdf = path.with_suffix(".pdf")
        if not pdf.is_file():
            errors.append("--render-dir requires an existing PDF or --compile")
        else:
            errors.extend(render_pdf(pdf, args.render_dir.expanduser().resolve()))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {path}")
    if args.compile:
        print(f"PDF: {path.with_suffix('.pdf')}")
    if args.render_dir:
        print(f"Rendered pages: {args.render_dir.expanduser().resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
