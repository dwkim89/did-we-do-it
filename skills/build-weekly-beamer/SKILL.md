---
name: build-weekly-beamer
description: Create or update a multi-frame weekly LaTeX Beamer deck and verified PDF by comparing two consecutive reviewed meeting summaries, tracking whether prior actions and questions were addressed, and adding relevant plots, JSON results, or contributor slides. Use for meeting-to-meeting progress differentials, previous-action follow-up, multi-contributor synthesis, or evidence updates. Do not summarize raw transcripts or alter meeting-summary evidence.
---

# Build Weekly Beamer

Build a decision-oriented weekly deck from approved source material. The deck exists to check commitments from one meeting at the next meeting. Use a restrained white, charcoal, gray, and muted-navy visual system. Organize by workstream or contributor, but make the project story more prominent than presenter order.

Read [references/deck-contract.md](references/deck-contract.md) before creating or updating a deck. Start from [assets/weekly_beamer_template.tex](assets/weekly_beamer_template.tex).

## Workflow

1. Inventory all source Markdown, existing `.tex`, plots, JSON, PDFs, and contributor decks. Record the date and source for each claim or asset.
2. Select two consecutive reviewed summaries: meeting N supplies prior actions, questions, decisions, and requested checks; meeting N+1 supplies the status evidence. Title the output for meeting N+1 and write it as `slides/YYYYMMDD_<series>/weekly-update.tex` and `.pdf`.
3. Build an explicit differential table with one row per material prior commitment: compact prior request, owner, what changed by N+1, and exactly one status: `done`, `in progress`, `blocked`, `not discussed`, or `needs confirmation`. Never infer completion from silence or from a contributor slide alone.
4. When both previous and current plots exist for a material claim, prefer a side-by-side visual differential. Match variable, category, kinematic interval, binning, normalization, and displayed axis window. Label both selections and dates. If source slices must be combined, aggregate compatible JSON with [scripts/make_matched_shape_plot.py](scripts/make_matched_shape_plot.py). If a material dimension cannot be matched, disclose it prominently and do not describe the pair as a controlled before/after comparison.
5. Use contributor decks only as evidence for the N-to-N+1 interval. Select relevant dated plots or tables; do not reproduce a contributor deck wholesale. If a contributor artifact is newer than N+1, label it as later resolution rather than meeting-time evidence.
6. Draft a complete 6--10 frame story: title/reporting interval; goal and motivation; N-to-N+1 differential; contributor/workstream evidence; reasoning and unresolved discussion; next actions for N+2; conclusion/decision checkpoint. Use `% role: ...` markers from the template. A one-frame status page is not a weekly deck.
7. Write for a broad university audience. Use familiar words, active voice, and short sentences. Remove filler, repeated context, and unnecessary articles when the meaning stays clear. Avoid internal labels such as “grid” unless they are defined. Keep claim-based titles to roughly ten words, at most six short bullets, and no more than two plots per frame.
8. For JSON, quote exact values and labels; make a compact table or metric strip only when it clarifies the claim. For plots, preserve axis labels, units, legends, and provenance. Do not fabricate or silently transform results.
9. If evidence, ownership, status, or interpretation is ambiguous, pause that claim and ask the user. Mark it `needs confirmation` until resolved.
10. Compile with LuaLaTeX and run structural, render, font, and density checks:

```bash
python3 skills/build-weekly-beamer/scripts/validate_beamer.py PATH/weekly.tex \
  --compile --engine lualatex --render-dir PATH/rendered
```

11. Inspect every rendered page and revise until there is no clipping, overlap, illegible plot text, unnecessary density, or inconsistent hierarchy. Deliver both `.tex` and `.pdf`.

## Update Mode

When new plots or JSON arrive, update the smallest number of frames whose claims change. Preserve the rest of the deck, update the source note and date, rerun validation, recompile, and visually inspect the entire PDF because layout can shift globally.

## Guardrails

- Do not call the transcript summarizer or rewrite source Markdown.
- Do not build a weekly deck from only meeting N; without N+1, create a clearly labeled skeleton whose statuses remain `not discussed` or `needs confirmation`.
- Do not use later evidence to silently rewrite the N-to-N+1 differential.
- Do not place unmatched plots side by side without stating every differing selection dimension; identical panel size or axis limits must not imply an otherwise false equivalence.
- Do not give every contributor equal slide space by default; allocate space to decision relevance and evidence.
- Avoid generic section-divider slides, decorative graphics, tiny text, and dense provenance blocks.
- Keep the palette neutral with one muted accent; do not color-code contributors.
- Use ASCII hyphens in LaTeX source and rendered text.
- Keep source notes legible but subordinate.
- Put source notes at the bottom edge of the content area. Do not leave unused space below them or shrink evidence merely to create a source band.
