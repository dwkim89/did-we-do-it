---
name: summarize-meeting-markdown
description: Normalize an existing dated meeting summary, or convert a dated Zoom-format TXT transcript, into a concise editable Markdown record with evidence-based ambiguity handling. Use when a user provides a Zoom AI or human-written summary in Markdown, text, PDF, or DOCX; supplies a raw meeting transcript; asks for a dated meeting summary; or needs canonical Markdown input for later weekly slides. Prefer an existing summary and avoid an LLM API call unless deeper transcript analysis is necessary and the user approves it. Do not build or update presentation files.
---

# Summarize Meeting Markdown

Create one reviewable Markdown artifact from the simplest available meeting source. Preserve uncertainty instead of turning vague discussion into a decision, cause, or assignment.

Read [references/summary-contract.md](references/summary-contract.md) before writing or reviewing the summary.

## Workflow

1. Inventory the supplied file and same-stem companions. Accept an existing meeting summary in `.md`, `.txt`, `.pdf`, or `.docx`, or a raw UTF-8 Zoom `.txt` transcript. Require one usable `YYYYMMDD` date in the primary input filename and use it as canonical.
2. Choose the shortest reliable route:
   - **summary-first:** when an existing Zoom AI or human-written summary is available, read it directly and normalize it to the summary contract. Do not call an LLM provider merely to re-summarize it;
   - **transcript route:** when no usable summary exists, tell the user that transcript content will be sent to the configured remote provider, then run the CLI below. Never print credentials;
   - **targeted verification:** when a supplied summary makes a material claim unclear or stronger than its evidence, consult the raw transcript only for that claim when available. Ask the user before sending any source to a remote provider.
3. For the transcript route, run from the repository root:

```bash
didwedoit summarize INPUT.txt --series SERIES
```

4. For the summary-first route, create or update `summaries/YYYYMMDD_series.md` directly. Preserve the supplied summary as an immutable source, record its path and checksum in frontmatter, set `extractor: provided-summary-normalization`, and begin with `status: draft`. Map its contents into the required headings without inventing missing facts.
5. Read the complete canonical Markdown. Verify every required heading, factual claim, owner, and available source locator. For a provided summary, cite its section, bullet, page, or line when possible; never fabricate transcript line references.
6. Put any unclear owner, commitment, answer, status, decision, cause, or interpretation under `Pending Confirmation` as an unchecked item. Treat AI-generated source summaries as useful but fallible: weaken unsupported causal wording and ask the smallest concrete question needed. Do not silently guess.
7. Apply the user's corrections directly to the canonical Markdown. Change `status: draft` to `status: reviewed` only after the user confirms all material ambiguities; unresolved items may remain when explicitly accepted as unresolved.
8. Hand the reviewed Markdown to `$build-weekly-beamer` when slides are requested and to `$maintain-project-history` when the longitudinal record is updated.

## Guardrails

- Keep wording compact and literal. Prefer one claim per bullet.
- Keep names and ownership exactly as supported by the transcript. `Unassigned` is valid.
- Distinguish a proposal from a decision and discussion from an action item.
- Treat absent follow-up as `not discussed`, not completed.
- Retain frontmatter provenance and the most precise locators available from the primary source.
- Never overwrite a reviewed canonical summary with a newly supplied AI summary. Reconcile new material as a secondary source and ask before changing established claims.
- Do not claim that an observed feature drives or causes a result when the source supports only correlation or inference sensitivity.
- Do not write presentation files, update project history, or invoke local Ollama unless the user explicitly overrides the remote provider.
- Never require the user to edit JSON for routine ambiguity review; the Markdown is the human review surface.
