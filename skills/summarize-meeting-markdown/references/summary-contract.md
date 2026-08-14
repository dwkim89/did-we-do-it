# Meeting summary contract

## Output identity

- Path: `summaries/YYYYMMDD_<series>.md`
- Date: exactly the `YYYYMMDD` found in the transcript filename
- One input transcript produces one summary
- Frontmatter keeps `date`, `series`, `meeting_id`, `source`, `source_sha256`, `extractor`, and review `status`

## Required section order

1. `Key outcomes`
2. `Decisions made`
3. `Open Questions`
4. `Pending Confirmation`
5. `Action items`

`Progress by contributor` may appear after Key outcomes when the transcript supports speaker attribution. `Risks, blockers, and reasoning` and `Topics discussed` may follow the required sections.

## Classification rules

- Key outcome: material progress, result, change, or current project state.
- Decision: a settled choice accepted in the meeting, not a suggestion.
- Open question: a question with no established answer or only a partial answer.
- Pending confirmation: any model interpretation that a reasonable reader could dispute, including vague pronouns, unclear owners, uncertain commitments, or conflicting statements.
- Action item: explicit future work. Include owner and status only when supported.

Use `- None confirmed.` rather than inventing content. Keep evidence line ranges on decisions, questions, and actions. Use unchecked Markdown boxes for items needing human confirmation.
