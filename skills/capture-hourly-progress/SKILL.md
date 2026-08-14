---
name: capture-hourly-progress
description: Capture an evidence-based progress report for a long-running interaction or work session. Use when roughly 60 minutes of active work have elapsed, before context compaction or handoff, after a substantial retry cycle, or when the user asks what was tried, failed, retried, and learned. Write only cross-project interaction history under the current repository's docs/ directory; do not replace domain run reports or promote lessons into stable knowledge.
---

# Capture Hourly Progress

Create one inspectable report for the latest work interval without interrupting active work merely to reach an exact clock boundary.

## Workflow

1. Identify the repository root and local IANA timezone. Default to `America/Los_Angeles` only when the user has not specified another timezone.
2. Run `scripts/new_hourly_report.py --docs-dir <repo>/docs --brief <slug> --timezone <zone>`. Use `--at` and `--started-at` only for backfills or tests.
3. Read the created skeleton completely and fill every section using the current interaction, command results, artifacts, and user corrections.
4. Distinguish facts from inference. Include exact commands only when they aid reproducibility; never copy secrets, credentials, personal identifiers, or large raw logs.
5. Link repository artifacts with relative paths. State when an attempt produced no artifact.
6. Leave unresolved uncertainty under `Open questions and risks`; do not invent a resolution.
7. Change frontmatter `status` from `draft` to `complete` only after verifying the report against available evidence.

## Content Contract

Record:

- objective and scope;
- approaches tried and their outcomes;
- failures, including observable symptoms;
- retries or adjustments and why they differed;
- knowledge gained from results and user interaction;
- artifacts and verification evidence;
- unresolved risks and next steps.

The filename is `YYYYMMDD_HH_TZ_brief-description.md`, for example `20260809_14_PDT_qwen-transcript-evaluation.md`. The helper adds `_02`, `_03`, and so on rather than overwriting a report created in the same hour.

## Boundaries

- Do not summarize a full day; use `$consolidate-daily-progress`.
- Do not create analysis-specific provenance bundles; allow domain reporting skills to own those.
- Do not convert tentative observations into stable operational lessons.
- A skill does not run as a background timer. Apply this workflow during an active Codex turn when the elapsed-work trigger is observable.
