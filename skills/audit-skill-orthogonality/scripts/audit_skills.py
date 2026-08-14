#!/usr/bin/env python3
"""Triage trigger/scope overlap between candidate and existing skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


STOP = {
    "a", "an", "and", "any", "for", "from", "in", "into", "is", "it", "of", "on",
    "or", "the", "this", "to", "use", "when", "with", "skill", "skills", "user", "users",
}


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    path: str
    digest: str


def frontmatter(path: Path) -> Skill | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    if not metadata.get("name") or not metadata.get("description"):
        return None
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return Skill(metadata["name"], metadata["description"], str(path.resolve()), digest)


def inventory(root: Path) -> list[Skill]:
    if not root.exists():
        return []
    result = []
    for path in sorted(root.rglob("SKILL.md")):
        parsed = frontmatter(path)
        if parsed:
            result.append(parsed)
    return result


def tokens(skill: Skill) -> set[str]:
    words = re.findall(r"[a-z0-9]+", f"{skill.name} {skill.description}".lower())
    return {word for word in words if len(word) > 2 and word not in STOP}


def similarity(left: Skill, right: Skill) -> float:
    a, b = tokens(left), tokens(right)
    return len(a & b) / len(a | b) if a or b else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--existing-root", type=Path, action="append", default=[])
    parser.add_argument("--threshold", type=float, default=0.22)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    candidates = inventory(args.candidate_root)
    existing = [skill for root in args.existing_root for skill in inventory(root)]
    results: list[dict] = []
    pairs: list[tuple[Skill, Skill]] = []
    for index, left in enumerate(candidates):
        pairs.extend((left, right) for right in candidates[index + 1 :])
        pairs.extend((left, right) for right in existing)
    conflict = False
    for left, right in pairs:
        score = similarity(left, right)
        if left.name == right.name:
            classification = "mirror" if left.digest == right.digest else "conflict"
            conflict = conflict or classification == "conflict"
        elif score >= args.threshold:
            classification = "review"
        else:
            continue
        results.append({
            "candidate": left.name,
            "neighbor": right.name,
            "classification": classification,
            "token_similarity": round(score, 3),
            "candidate_path": left.path,
            "neighbor_path": right.path,
        })

    payload = {
        "candidate_count": len(candidates),
        "existing_count": len(existing),
        "threshold": args.threshold,
        "results": results,
        "note": "Token similarity is triage only; perform the semantic six-boundary review from SKILL.md.",
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Candidates: {len(candidates)}; existing: {len(existing)}; threshold: {args.threshold:.2f}")
        for item in results:
            print(
                f"{item['classification'].upper():8} {item['candidate']} <-> {item['neighbor']} "
                f"({item['token_similarity']:.3f})"
            )
        print(payload["note"])
    return 2 if conflict else 0


if __name__ == "__main__":
    raise SystemExit(main())
