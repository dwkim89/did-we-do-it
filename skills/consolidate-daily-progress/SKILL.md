---
name: consolidate-daily-progress
description: Consolidate one local calendar day's hourly progress reports into a concise handoff and historical summary. Use on the next active session after a day closes, at an end-of-day checkpoint, or when the user asks for daily history from docs/YYYYMMDD_HH_TZ_*.md reports. Summarize only the hourly reports; do not create new evidence, rerun work, or promote tentative lessons into stable knowledge.
---

# Consolidate Daily Progress

Produce one daily narrative that helps the next session or another person resume work without rereading every hourly report.

## Workflow

1. Select the target local calendar date. With no user choice, summarize the previous day.
2. Run `scripts/new_daily_summary.py --docs-dir <repo>/docs --brief <slug> --timezone <zone> [--date YYYYMMDD]`.
3. Read every source listed in the generated skeleton completely and in chronological order.
4. Replace placeholders with a deduplicated synthesis. Preserve meaningful changes of understanding across the day rather than reporting only the final state.
5. Separate confirmed knowledge, failed approaches, and unresolved hypotheses.
6. Include direct relative links to the hourly reports and important artifacts.
7. Verify every material claim has support in at least one listed hourly report, then change `status: draft` to `status: complete`.

## Output Contract

Write `docs/YYYYMMDD_daily-summary_brief-description.md`. Include:

- executive handoff;
- objectives pursued;
- chronological progress and turning points;
- failures and recoveries;
- confirmed knowledge;
- unresolved questions and risks;
- recommended next-session starting point;
- complete list of source hourly reports.

## Boundaries

- Do not read raw interaction history when an hourly report exists; the hourly report is the daily summary's source of record.
- Do not silently resolve contradictions. Cite both hourly reports and describe the later evidence.
- Do not overwrite an existing daily summary. Update it explicitly only when the user requests a revision.
- A skill does not run as a background daily job. Apply it on the first active turn after the date becomes due, or connect it to a separate scheduler later.
