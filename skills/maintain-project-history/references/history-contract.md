# Project history contract

## Output

Write one file per meeting series at `project-history/<series>.md`.

Use this stable structure:

1. `Project objective`
2. `Current state`
3. `Major outcomes and turning points`
4. `Decision log`
5. `Action trajectory`
6. `Open and resolved questions`
7. `Recurring risks and lessons`
8. `Meeting index`

## Evidence rules

- Use only meeting summaries with `status: reviewed` unless the user explicitly asks for a provisional view.
- Give every outcome, decision, action-state change, and question resolution a meeting date and relative Markdown link.
- Preserve `needs confirmation` rather than smoothing over ambiguous evidence.
- Label an inference as an inference and ask the user before treating it as project knowledge.
- When a later meeting contradicts an earlier meeting, retain both dated states and describe the transition.

## Writing rules

- Keep `Current state` to at most ten bullets.
- Keep one idea per bullet.
- Prefer chronological tables for decisions and actions.
- Use plain Markdown so collaborators can edit the history without specialized tooling.
