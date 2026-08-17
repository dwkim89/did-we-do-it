---
name: build-weekly-beamer
description: Prepare, update, and quality-review a multi-frame weekly LaTeX Beamer deck and verified PDF from one reviewed meeting summary or two consecutive reviewed summaries. Use to generate a structured next-meeting skeleton with evidence placeholders, track prior actions and questions, build meeting-to-meeting progress differentials, carry unresolved work forward, synthesize contributors, add plots/JSON/PDF evidence, or perform visual/contextual/logical slide review. Do not summarize raw transcripts or alter meeting-summary evidence.
---

# Build Weekly Beamer

Build a decision-oriented weekly deck from approved source material. The deck exists to check commitments from one meeting at the next meeting. Use the Berkeley presentation profile defined in the deck contract: white and neutral surfaces, Berkeley blue, California gold, and TeX Gyre Heros. Organize by workstream or contributor, but make the project story more prominent than presenter order.

Read [references/deck-contract.md](references/deck-contract.md) before creating or updating a deck. For a deck prepared from only meeting N, also read [references/preparation-mode.md](references/preparation-mode.md). Start from [assets/weekly_beamer_template.tex](assets/weekly_beamer_template.tex).

## Workflow

1. Inventory all source Markdown, existing `.tex`, plots, JSON, PDFs, contributor decks, and approved branding assets. Record the date and source for each claim or asset.
2. Choose the mode from available evidence:
   - preparation mode: use one reviewed meeting N summary to build the deck for N+1, with `awaiting evidence` placeholders and no claims about progress that has not occurred;
   - differential mode: use reviewed summaries N and N+1 to record what changed. Before N+1 is reviewed, supplied dated artifacts may update preparation status but remain `pre-meeting evidence`.
3. Confirm the next meeting date and series name. Title the output for N+1 and write it as `slides/YYYYMMDD_<series>/weekly-update.tex` and `.pdf`. If the date is unknown, ask the user rather than inventing it. Copy the approved local Berkeley logo files from `branding/berkeley/` into the deck's `assets/` directory. If either file is missing, ask the user for the approved asset; never recreate, trace, recolor, or substitute an institutional logo.
4. Build a follow-up ledger from meeting N decisions, open questions, pending confirmations, action items, and requested checks. Give every material item a stable ID, compact wording, owner, required evidence or answer, success criterion, and status. Never infer completion from silence or from a contributor slide alone.
5. In preparation mode, create a specific evidence placeholder for each check: plot, table, metric, external PDF, or user confirmation; required selection or comparison; and the conclusion it could support. Do not use a generic empty box when the summary specifies what must be tested.
6. When both previous and current plots exist for a material claim, prefer a side-by-side visual differential. Match variable, category, kinematic interval, binning, normalization, and displayed axis window. Label both selections and dates. If source slices must be combined, aggregate compatible JSON with [scripts/make_matched_shape_plot.py](scripts/make_matched_shape_plot.py). If a material dimension cannot be matched, disclose it prominently and do not describe the pair as a controlled before/after comparison.
7. Use contributor decks only as evidence for the N-to-N+1 interval. Select relevant dated plots or tables; do not reproduce a contributor deck wholesale. If a contributor artifact is newer than N+1, label it as later resolution rather than meeting-time evidence.
8. Draft a complete story in this order: goal and motivation; current status and prior follow-up; work already tried; evidence and reasoning; unfinished items carried forward; work to try next; conclusion or decision checkpoint. Preserve the template's font, palette, bold message titles, half-blue/half-gold title rule, and two-logo title page. Use `% role: ...` markers from the template. Do not impose a maximum frame count: add a frame only when it makes one clear point or tests one distinct hypothesis, and split a dense frame instead of shrinking it.
9. Carry every unresolved meeting N item into the N+1 to-do frame with the same stable ID and owner. Remove it only when evidence establishes `done` or the user explicitly closes or drops it; record that disposition. Do not duplicate a carried item as unrelated new work.
10. Write for a broad university audience. Use familiar words, active voice, and short sentences. Remove filler, repeated context, and unnecessary articles when the meaning stays clear. Avoid internal labels such as “grid” unless they are defined. Keep claim-based titles to roughly ten words, at most six short bullets, and no more than two plots per frame. State the hypothesis or question on every evidence frame and say whether the displayed evidence supports, challenges, or does not yet resolve it.
11. For JSON, quote exact values and labels; make a compact table or metric strip only when it clarifies the claim. For plots, preserve axis labels, units, legends, and provenance. Do not fabricate or silently transform results.
12. If evidence, ownership, status, or interpretation is ambiguous, pause that claim and ask the user. Mark it `needs confirmation` until resolved.
13. Treat the `.tex` and compiled `.pdf` as one required output pair. Compile with LuaLaTeX and run structural, render, font, and density checks:

```bash
python3 skills/build-weekly-beamer/scripts/validate_beamer.py PATH/weekly.tex \
  --brand-profile berkeley --compile --engine lualatex --render-dir PATH/rendered
```

14. Before sharing, perform three review passes over the complete rendered deck:
    - visual: no overlap among plots, tables, text, legends, titles, or source notes; no clipping, tiny labels, unnecessary density, or inconsistent alignment;
    - contextual: every claim has the correct date, selection, category, units, source, and meeting-time status;
    - logical: the sequence is goal, current status, work tried, evidence/reasoning, work to try, and conclusion; conclusions do not exceed the evidence.
15. Revise and repeat compilation and all three review passes after any material change. Deliver both `.tex` and the current `.pdf` only after every page passes. A slide task is incomplete when the source exists without a successfully rendered and inspected PDF.

## Update Mode

When new plots, tables, JSON, PDFs, or user confirmations arrive before N+1, match each artifact to a stable follow-up ID. Update the smallest number of frames, status, evidence source, and carry-forward list. Preserve the rest of the deck, rerun validation, recompile, and inspect the entire PDF because layout can shift globally. After the N+1 summary is reviewed, reconcile every ledger item against it and convert the preparation deck into the final N-to-N+1 differential.

## Guardrails

- Do not call the transcript summarizer or rewrite source Markdown.
- From only meeting N, create a clearly labeled preparation skeleton. Use `awaiting evidence`, not `done`, for checks that have not yet received results; reserve `not discussed` for retrospective review of meeting N+1.
- Do not use later evidence to silently rewrite the N-to-N+1 differential.
- Do not place unmatched plots side by side without stating every differing selection dimension; identical panel size or axis limits must not imply an otherwise false equivalence.
- Do not give every contributor equal slide space by default; allocate space to decision relevance and evidence.
- Avoid generic section-divider slides, decorative graphics, tiny text, and dense provenance blocks.
- Never allow plots, tables, text, legends, titles, or source notes to overlap. Split the frame when fit is uncertain.
- Do not add filler to reach a target length, and do not omit necessary evidence to stay below one. Deck length follows the argument.
- Never hand off a `.tex` file alone. If compilation or rendering fails, report the deck as blocked and retain the source for repair; do not present it as completed.
- Keep the Berkeley profile consistent across frames. Use blue for hierarchy, gold only for the split rule and pale block accents, and never color-code contributors.
- Keep both institutional logos on the title page only. Preserve their aspect ratios, clear space, and original colors.
- Use ASCII hyphens in LaTeX source and rendered text.
- Keep source notes legible but subordinate.
- Put source notes at the bottom edge of the content area. Do not leave unused space below them or shrink evidence merely to create a source band.
