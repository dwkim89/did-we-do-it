# Meeting summary contract

## Output identity

- Path: `summaries/YYYYMMDD_<series>.md`
- Date: exactly the `YYYYMMDD` found in the primary source filename
- Primary source: prefer an existing meeting summary in Markdown, text, PDF, or DOCX; otherwise use the raw Zoom TXT transcript
- One meeting source produces one canonical summary; a companion transcript may be used only for targeted verification
- Frontmatter keeps `date`, `series`, `meeting_id`, `source`, `source_sha256`, `extractor`, and review `status`
- Use `extractor: provided-summary-normalization` when no provider extraction is performed

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

Use `- None confirmed.` rather than inventing content. Keep evidence line ranges for transcript sources. For existing summaries, use the most precise available section, bullet, page, or line locator and do not invent transcript evidence. Use unchecked Markdown boxes for items needing human confirmation.

## Source priority

1. User corrections and confirmations.
2. Reviewed canonical Markdown already in `summaries/`.
3. A supplied human-written or Zoom AI meeting summary.
4. A raw transcript, used for full extraction only when no usable summary exists or for targeted verification.

A later AI summary is supplementary evidence, not authority to overwrite a reviewed canonical record. Preserve proposals, observations, and causal claims at the strength supported by the source.
