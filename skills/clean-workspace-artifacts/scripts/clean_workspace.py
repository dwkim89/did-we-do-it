#!/usr/bin/env python3
"""Dry-run-first cleanup for allowlisted generated workspace artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path


LATEX_AUX = {".aux", ".fdb_latexmk", ".fls", ".log", ".nav", ".out", ".snm", ".toc", ".vrb"}
SKIP_PARTS = {".git", ".venv"}


@dataclass(frozen=True)
class Candidate:
    path: str
    reason: str
    bytes: int


def byte_size(path: Path) -> int:
    if path.is_symlink() or path.is_file():
        try:
            return path.lstat().st_size
        except FileNotFoundError:
            return 0
    total = 0
    for item in path.rglob("*"):
        if item.is_file() or item.is_symlink():
            try:
                total += item.lstat().st_size
            except FileNotFoundError:
                pass
    return total


def skipped(path: Path, root: Path) -> bool:
    return bool(SKIP_PARTS.intersection(path.relative_to(root).parts))


def scan(root: Path, include_build_output: bool) -> list[Candidate]:
    found: dict[Path, str] = {}

    def add(path: Path, reason: str) -> None:
        if path.exists() or path.is_symlink():
            found[path] = reason

    add(root / ".pytest_cache", "pytest cache")
    add(root / "tmp", "repository temporary output")
    add(root / ".coverage", "coverage data")
    add(root / ".DS_Store", "filesystem metadata")

    for path in root.rglob("__pycache__"):
        if not skipped(path, root):
            add(path, "Python bytecode cache")
    for path in root.rglob("*"):
        if skipped(path, root) or not path.is_file():
            continue
        if path.suffix in {".pyc", ".pyo"}:
            add(path, "Python bytecode")
        elif path.suffix in LATEX_AUX:
            relative_parts = path.relative_to(root).parts
            matching_tex = path.with_suffix(".tex").is_file()
            if "tmp" in relative_parts or matching_tex:
                add(path, "LaTeX auxiliary file")
        elif path.name == ".DS_Store":
            add(path, "filesystem metadata")
    slides = root / "slides"
    if slides.is_dir():
        for path in slides.rglob("rendered"):
            if path.is_dir():
                add(path, "rendered slide previews")

    for name in ("meetings", "state"):
        path = root / name
        if path.is_dir() and not any(path.iterdir()):
            add(path, "empty runtime directory")

    if include_build_output:
        add(root / "build", "generated build output")
        add(root / "dist", "generated distribution output")
        for path in root.rglob("*.egg-info"):
            if not skipped(path, root):
                add(path, "generated package metadata")

    selected = []
    for path in sorted(found, key=lambda item: (len(item.parts), str(item))):
        if any(parent in found for parent in path.parents if parent != path):
            continue
        selected.append(Candidate(str(path.relative_to(root)), found[path], byte_size(path)))
    return selected


def validate_root(root: Path) -> Path:
    root = root.expanduser().resolve()
    if not (root / "pyproject.toml").is_file() or not (root / "skills").is_dir():
        raise SystemExit("Refusing cleanup: root must contain pyproject.toml and skills/")
    return root


def apply(root: Path, candidates: list[Candidate]) -> None:
    for item in candidates:
        path = root / item.path
        resolved = path.resolve(strict=False)
        if not resolved.is_relative_to(root):
            raise SystemExit(f"Refusing path outside repository: {path}")
        if path.is_symlink() or path.is_file():
            path.unlink(missing_ok=True)
        elif path.is_dir():
            shutil.rmtree(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--include-build-output", action="store_true")
    parser.add_argument("--apply", action="store_true", help="Delete the previewed allowlisted paths")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = validate_root(args.root)
    candidates = scan(root, args.include_build_output)
    total = sum(item.bytes for item in candidates)
    if args.json:
        print(json.dumps({"mode": "apply" if args.apply else "dry-run", "root": str(root),
                          "total_bytes": total, "candidates": [asdict(item) for item in candidates]}, indent=2))
    else:
        print(f"{'APPLY' if args.apply else 'DRY RUN'}: {root}")
        for item in candidates:
            print(f"- {item.path} ({item.reason}, {item.bytes} bytes)")
        print(f"Total: {len(candidates)} paths, {total} bytes")
    if args.apply:
        apply(root, candidates)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
