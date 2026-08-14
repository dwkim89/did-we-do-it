---
name: summarize-meeting-markdown
description: Convert a dated Zoom-format TXT meeting transcript into a concise, editable Markdown record using the configured remote LLM and evidence-based ambiguity handling. Use when a user supplies a raw meeting transcript, asks for a dated meeting summary, or needs canonical Markdown input for later weekly slides. Do not build or update presentation files.
---

# Summarize Meeting Markdown

Create one reviewable Markdown artifact from one transcript. Preserve uncertainty instead of turning vague discussion into a decision or assignment.

Read [references/summary-contract.md](references/summary-contract.md) before writing or reviewing the summary.

## Workflow

1. Confirm the input is a UTF-8 `.txt` Zoom transcript whose filename contains exactly one usable `YYYYMMDD` meeting date. Use the filename date as canonical.
2. Tell the user that transcript content will be sent to the configured remote provider before making the call. Never print credentials.
3. Run from the repository root:

```bash
didwedoit summarize INPUT.txt --series SERIES
```

4. Read the complete generated `summaries/YYYYMMDD_series.md`. Verify every required heading, factual claim, owner, and source-line reference.
5. Put any unclear owner, commitment, answer, status, decision, or interpretation under `Pending Confirmation` as an unchecked item. Ask the user the smallest concrete question needed to resolve it. Do not silently guess.
6. Apply the user's corrections directly to the Markdown. Change frontmatter `status: draft` to `status: reviewed` only after the user confirms all material ambiguities; unresolved items may remain if explicitly accepted as unresolved.
7. Hand the reviewed Markdown to `$build-weekly-beamer` when slides are requested and to `$maintain-project-history` when the longitudinal record is updated.

## Guardrails

- Keep wording compact and literal. Prefer one claim per bullet.
- Keep names and ownership exactly as supported by the transcript. `Unassigned` is valid.
- Distinguish a proposal from a decision and discussion from an action item.
- Treat absent follow-up as `not discussed`, not completed.
- Retain frontmatter provenance and transcript line references.
- Do not write presentation files, update project history, or invoke local Ollama unless the user explicitly overrides the remote provider.
- Never require the user to edit JSON for routine ambiguity review; the Markdown is the human review surface.
