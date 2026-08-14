#!/usr/bin/env python3
"""Create a collision-safe hourly progress-report skeleton."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("brief description must contain a letter or number")
    return slug[:80].rstrip("-")


def local_time(value: str | None, zone: ZoneInfo) -> datetime:
    if value is None:
        return datetime.now(zone)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=zone)
    return parsed.astimezone(zone)


def available_path(docs_dir: Path, stem: str) -> Path:
    candidate = docs_dir / f"{stem}.md"
    sequence = 2
    while candidate.exists():
        candidate = docs_dir / f"{stem}_{sequence:02d}.md"
        sequence += 1
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs-dir", type=Path, required=True)
    parser.add_argument("--brief", required=True)
    parser.add_argument("--timezone", default="America/Los_Angeles")
    parser.add_argument("--at", help="ISO report end time; defaults to now")
    parser.add_argument("--started-at", help="ISO interval start time, if known")
    args = parser.parse_args()

    try:
        zone = ZoneInfo(args.timezone)
    except ZoneInfoNotFoundError as exc:
        raise SystemExit(f"Unknown IANA timezone: {args.timezone}") from exc
    ended = local_time(args.at, zone)
    started = local_time(args.started_at, zone).isoformat(timespec="minutes") if args.started_at else "unknown"
    abbreviation = ended.tzname() or args.timezone.replace("/", "-")
    stem = f"{ended:%Y%m%d}_{ended:%H}_{abbreviation}_{slugify(args.brief)}"
    docs_dir = args.docs_dir.resolve()
    docs_dir.mkdir(parents=True, exist_ok=True)
    path = available_path(docs_dir, stem)
    title = args.brief.strip().replace("-", " ")
    body = f"""---
kind: hourly-progress
period_start: {started}
period_end: {ended.isoformat(timespec="minutes")}
timezone: {args.timezone}
status: draft
---

# Hourly progress: {title}

## Objective and scope

- TODO

## Tried

- TODO

## Failed

- TODO or `None observed.`

## Retried or adjusted

- TODO or `No retries in this interval.`

## Knowledge gained from results and interaction

- TODO

## Evidence and artifacts

- TODO

## Open questions and risks

- TODO or `None currently known.`

## Next steps

- TODO
"""
    path.write_text(body, encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
