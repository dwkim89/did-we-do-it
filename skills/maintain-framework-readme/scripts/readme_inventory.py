#!/usr/bin/env python3
"""Emit a deterministic public-documentation inventory for this framework."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path


def frontmatter_value(path: Path, key: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else ""


def cli_inventory(root: Path) -> dict[str, object]:
    sys.path.insert(0, str(root / "src"))
    from didwedoit.cli import build_parser  # noqa: PLC0415

    parser = build_parser()
    subparsers = next(
        action for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    )
    commands: dict[str, dict[str, object]] = {}
    providers: set[str] = set()
    for name, command_parser in sorted(subparsers.choices.items()):
        options = []
        positionals = []
        for action in command_parser._actions:
            if action.dest == "help":
                continue
            if action.option_strings:
                options.extend(action.option_strings)
                if action.dest == "provider" and action.choices:
                    providers.update(action.choices)
            else:
                positionals.append(action.dest)
        commands[name] = {
            "positionals": positionals,
            "options": sorted(options),
        }
    return {"commands": commands, "providers": sorted(providers)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    required = [root / "README.md", root / "pyproject.toml", root / "src" / "didwedoit" / "cli.py"]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"Missing required framework files: {missing}")

    with (root / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle).get("project", {})

    cli = cli_inventory(root)
    skills = []
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        skills.append({
            "name": frontmatter_value(path, "name"),
            "description": frontmatter_value(path, "description"),
        })

    readme = (root / "README.md").read_text(encoding="utf-8")
    documented_commands = sorted(set(re.findall(r"\bdidwedoit\s+([a-z][a-z-]+)", readme)))
    implemented_commands = sorted(cli["commands"])
    tests = sorted(path.name for path in (root / "tests").glob("test_*.py"))
    ignore_rules = [
        line.strip() for line in (root / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    payload = {
        "project": {
            "name": project.get("name"),
            "version": project.get("version"),
            "python": project.get("requires-python"),
            "dependencies": project.get("dependencies", []),
        },
        "implemented_cli": cli["commands"],
        "providers": cli["providers"],
        "documented_commands": documented_commands,
        "implemented_but_undocumented": sorted(set(implemented_commands) - set(documented_commands)),
        "documented_but_unimplemented": sorted(set(documented_commands) - set(implemented_commands)),
        "skills": skills,
        "tests": tests,
        "gitignore_rules": ignore_rules,
        "evidence_files": [
            "README.md", "pyproject.toml", ".gitignore",
            "src/didwedoit/cli.py", "src/didwedoit/config.py",
            "src/didwedoit/history.py", "src/didwedoit/render.py",
            "skills/*/SKILL.md", "tests/test_*.py",
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
