---
name: maintain-project-history
description: Create or update one longitudinal project-history Markdown file from reviewed dated meeting summaries. Use after weekly summaries are reviewed, when users want an overall project record, decision history, action trajectory, recurring questions, or a later project retrospective. Do not read raw transcripts, summarize Codex work logs, or create presentation files.
---

# Maintain Project History

Maintain a compact, evidence-linked memory of the project across meetings. Treat reviewed meeting summaries as the only source of truth.

Read [references/history-contract.md](references/history-contract.md) before creating or updating the history.

## Workflow

1. Select one meeting series. Read every matching reviewed `summaries/YYYYMMDD_<series>.md` in chronological order.
2. Refuse to treat `status: draft` claims as established. Ask the user whether to exclude the draft or resolve its pending confirmations.
3. Create or update `project-history/<series>.md`. Preserve earlier entries; correct them only when a later reviewed summary explicitly supersedes them.
4. Deduplicate repeated status discussion while preserving dated turning points, decisions, reopened questions, and changes in reasoning.
5. Track actions through the exact states `done`, `in progress`, `blocked`, `not discussed`, and `needs confirmation`. Silence never means completion.
6. Link every dated claim to its source meeting summary. Mark conflicting evidence and ask the user rather than selecting one interpretation silently.
7. Keep the current-state section brief enough to read at the start of a new session. Keep older detail in the dated timeline.

## Boundaries

- Do not call an LLM on raw transcripts; `$summarize-meeting-markdown` owns that step.
- Do not create weekly slides; `$build-weekly-beamer` consumes reviewed summaries directly.
- Do not read `docs/` interaction reports; `$capture-hourly-progress` and `$consolidate-daily-progress` own agent-session history.
- Do not invent missing owners, dates, outcomes, causal explanations, or resolutions.
- Ask the user whenever source status, conflicts, or consolidation choices are unclear.
