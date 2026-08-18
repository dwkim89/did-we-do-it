#!/usr/bin/env python3
"""Flag specialist slide wording that needs replacement or a first-use definition."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


TERMS = {
    "ablation": (r"\bablation(?:s)?\b", "controlled input change or rerun after changing one input group"),
    "parity gate": (r"\bparity[ -]gate\b", "first reproduce the stored scores before changing inputs"),
    "closure": (r"\bclosure\b", "Data and MC agree within uncertainty, or ratio is consistent with one"),
    "score-response matrix": (r"\bscore[ -]response matrix\b", "table showing how scores change in each input test"),
    "sentinel": (r"\bsentinel(?:s)?\b", "special placeholder value"),
    "stratum": (r"\bstrat(?:um|a)\b", "subgroup or subgroups defined by the selection"),
    "decorrelate": (r"\bdecorrelat\w*\b", "shuffle values within the named subgroup"),
}


def visible_lines(text: str):
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("%"):
            continue
        # Remove LaTeX comments while preserving escaped percent signs.
        line = re.split(r"(?<!\\)%", line, maxsplit=1)[0]
        yield number, line


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--allow", action="append", default=[], metavar="TERM",
        help="Allow a necessary term after defining it on first use (repeatable)",
    )
    args = parser.parse_args()
    path = args.path.expanduser().resolve()
    text = path.read_text(encoding="utf-8")
    allowed = {term.casefold() for term in args.allow}
    findings: list[str] = []
    for number, line in visible_lines(text):
        for term, (pattern, replacement) in TERMS.items():
            if term.casefold() in allowed:
                continue
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(
                    f"{path}:{number}: '{term}' needs a plain replacement or first-use definition; "
                    f"consider: {replacement}"
                )
    if findings:
        print("\n".join(findings), file=sys.stderr)
        return 1
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
