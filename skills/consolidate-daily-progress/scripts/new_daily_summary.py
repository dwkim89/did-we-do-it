#!/usr/bin/env python3
"""Create a daily-summary skeleton from hourly progress reports."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


HOURLY_RE = re.compile(r"^(?P<date>\d{8})_(?P<hour>\d{2})_(?P<zone>[A-Za-z0-9+_-]+)_.+\.md$")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("brief description must contain a letter or number")
    return slug[:80].rstrip("-")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs-dir", type=Path, required=True)
    parser.add_argument("--brief", required=True)
    parser.add_argument("--timezone", default="America/Los_Angeles")
    parser.add_argument("--date", help="Target local day as YYYYMMDD; defaults to yesterday")
    parser.add_argument("--at", help="ISO current time override for deterministic tests")
    args = parser.parse_args()

    try:
        zone = ZoneInfo(args.timezone)
    except ZoneInfoNotFoundError as exc:
        raise SystemExit(f"Unknown IANA timezone: {args.timezone}") from exc
    now = datetime.fromisoformat(args.at) if args.at else datetime.now(zone)
    if now.tzinfo is None:
        now = now.replace(tzinfo=zone)
    now = now.astimezone(zone)
    target = args.date or (now.date() - timedelta(days=1)).strftime("%Y%m%d")
    if not re.fullmatch(r"\d{8}", target):
        raise SystemExit("--date must use YYYYMMDD")

    docs_dir = args.docs_dir.resolve()
    docs_dir.mkdir(parents=True, exist_ok=True)
    sources = sorted(
        path for path in docs_dir.glob(f"{target}_*.md")
        if HOURLY_RE.match(path.name)
    )
    if not sources:
        raise SystemExit(f"No hourly reports found for {target} in {docs_dir}")
    path = docs_dir / f"{target}_daily-summary_{slugify(args.brief)}.md"
    if path.exists():
        raise SystemExit(f"Daily summary already exists: {path}")
    links = "\n".join(f"- [{source.name}](./{source.name})" for source in sources)
    body = f"""---
kind: daily-progress-summary
source_date: {target}
generated_at: {now.isoformat(timespec="minutes")}
timezone: {args.timezone}
status: draft
---

# Daily progress summary: {args.brief.strip().replace("-", " ")}

## Executive handoff

- TODO

## Objectives pursued

- TODO

## Chronological progress and turning points

- TODO

## Failures and recoveries

- TODO

## Confirmed knowledge

- TODO

## Unresolved questions and risks

- TODO

## Recommended next-session starting point

- TODO

## Source hourly reports

{links}
"""
    path.write_text(body, encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
