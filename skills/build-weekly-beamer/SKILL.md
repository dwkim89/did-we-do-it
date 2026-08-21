---
name: build-weekly-beamer
description: Prepare, update, and quality-review a weekly LaTeX Beamer deck and verified PDF from one reviewed meeting summary or two consecutive reviewed summaries. Use to present last week's requests and current status, generate a roughly 15-frame main narrative plus supporting backup, build next-meeting evidence placeholders and meeting-to-meeting differentials, carry unresolved work forward, synthesize contributors, revise requested plot/table evidence, or perform visual/contextual/logical slide review. Do not summarize raw transcripts or alter meeting-summary evidence.
---

# Build Weekly Beamer

Build a decision-oriented weekly deck from approved source material. The deck exists to check commitments from one meeting at the next meeting. Use the Berkeley presentation profile defined in the deck contract: white and neutral surfaces, Berkeley blue, California gold, and TeX Gyre Heros. Organize by workstream or contributor, but make the project story more prominent than presenter order.

Read [references/deck-contract.md](references/deck-contract.md) before creating or updating a deck. For a deck prepared from only meeting N, also read [references/preparation-mode.md](references/preparation-mode.md). Start from [assets/weekly_beamer_template.tex](assets/weekly_beamer_template.tex).
Use the sibling `apply-berkeley-beamer-layout` skill for the maintained visual
layout, spacing rules, and supporting-material divider.

## Workflow

1. Inventory all source Markdown, existing `.tex`, plots, JSON, PDFs, contributor decks, and approved branding assets. Record the date and source for each claim or asset.
2. Choose the mode from available evidence:
   - preparation mode: use one reviewed meeting N summary to build the deck for N+1, with `awaiting evidence` placeholders and no claims about progress that has not occurred;
   - differential mode: use reviewed summaries N and N+1 to record what changed. Before N+1 is reviewed, supplied dated artifacts may update preparation status but remain `pre-meeting evidence`.
3. Confirm the next meeting date and series name. Title the output for N+1 and write it as `slides/YYYYMMDD_<series>/weekly-update.tex` and `.pdf`. If the date is unknown, ask the user rather than inventing it. Copy the approved Berkeley logo files from `slides/assets/` into the deck's local `assets/` directory. If either shared file is missing, ask the user for the approved asset; never recreate, trace, recolor, or substitute an institutional logo.
4. Build a follow-up ledger from meeting N decisions, open questions, pending confirmations, action items, and requested checks. Give every material item a stable, human-facing number such as `Item 1`, plus compact wording, responsible person, required evidence or answer, success criterion, and status. Do not expose meeting codes, initials, or identifiers such as `W19-DK-04` unless the user asks for them; internal LaTeX labels may remain machine-oriented. For a requested artifact revision, also record the prior artifact, exact requested change, and replacement artifact. Never infer completion from silence or from a contributor slide alone.
5. In preparation mode, create a specific evidence placeholder for each check: plot, table, metric, external PDF, or user confirmation; required selection or comparison; and the conclusion it could support. Do not use a generic empty box when the summary specifies what must be tested.
6. When both previous and current plots exist for a material claim, prefer a side-by-side visual differential. Match variable, category, kinematic interval, binning, normalization, and displayed axis window. Label both selections and dates. If source slices must be combined, aggregate compatible JSON with [scripts/make_matched_shape_plot.py](scripts/make_matched_shape_plot.py). If a material dimension cannot be matched, disclose it prominently and do not describe the pair as a controlled before/after comparison.
7. For each transcript-requested revision, update the evidence for the next meeting rather than merely restating the request. If a plot must be regenerated from histogram or binned data, invoke `build-hep-validation-plots` first and consume its checked PDF/JSON pair. If supplied values support a table revision, edit the table and preserve its provenance. When required inputs are absent or the requested change is ambiguous, keep a specific placeholder and ask the user. Do not overwrite the prior artifact; retain both versions for a reversible comparison.
8. Use contributor decks only as evidence for the N-to-N+1 interval. Select relevant dated plots or tables; do not reproduce a contributor deck wholesale. If a contributor artifact is newer than N+1, label it as later resolution rather than meeting-time evidence.
9. Draft a complete story in this order: title; a team-wide `Follow-up items` overview; the presenting contributor's workstream; other decision-relevant workstreams and dependencies; current evidence and reasoning; unfinished work; next actions; conclusion or decision checkpoint. The overview must include every responsible person represented in the source, not only the presenter, and show `Item`, `Responsible`, `Follow-up`, and `Status` in one compact table. Completed items may remain there for context without receiving a dedicated slide. When one contributor has a focused presentation and collaborators may present their own current results, end that contributor's main section with one handoff slide: summarize only the supported findings, state possible connections to named collaborators' work, and avoid guessing their progress or replacing their update with a speculative plan. Aim for about 15 main frames, including the title and conclusion, but treat this as a planning target rather than a quota. Keep only decision-relevant material in the main deck; put supporting plots, alternate selections, complete tables, and detailed provenance after `\appendix`. Preserve the template's font, palette, bold message titles, half-blue/half-gold title rule, and two-logo title page. Use `% role: ...` markers from the template. Add or remove frames when the argument requires it, and split a dense frame instead of shrinking it.
10. Treat the opening `Follow-up items` frame as the authoritative whole-team
    list. Do not repeat an `Item N | request | status` strip beneath detailed
    slide titles. Keep an item number in a title only when it helps navigation;
    otherwise put necessary context directly into the body.
11. Carry every unresolved meeting N item into the N+1 to-do frame with the same item number and responsible person. Remove it only when evidence establishes `done` or the user explicitly closes or drops it; record that disposition. Do not duplicate a carried item as unrelated new work.
12. Use the sibling `simplify-slide-language` skill for a dedicated wording pass. Write for a broad university audience using familiar words, active voice, and short sentences. Replace method nicknames with concrete actions: for example, “rerun after changing one input group” instead of “ablation.” Define any necessary specialist term on first use. Remove filler, repeated context, and unnecessary articles when the meaning stays clear. Keep claim-based titles to roughly ten words, at most six short bullets, and no more than two plots per frame. State the hypothesis or question on every evidence frame and say whether the displayed evidence supports, challenges, or does not yet resolve it.
13. After the first complete render, use the sibling `review-slide-message-clarity` skill for a separate deck-level argument pass. Check what question each slide answers, why the next slide follows, whether evidence status matches the wording, and whether the conclusion traces to displayed evidence. Reorder or remove slides when the logic is clearer than adding transition text.
14. For JSON, quote exact values and labels; make a compact table or metric strip only when it clarifies the claim. For plots, preserve axis labels, units, legends, and provenance. Do not fabricate or silently transform results.
15. If evidence, ownership, status, or interpretation is ambiguous, pause that claim and ask the user. Mark it `needs confirmation` until resolved.
16. Treat the `.tex` and compiled `.pdf` as one required output pair. Compile with LuaLaTeX and run structural, render, font, and density checks:

```bash
python3 skills/build-weekly-beamer/scripts/validate_beamer.py PATH/weekly.tex \
  --brand-profile berkeley --compile --engine lualatex --render-dir PATH/rendered
```

17. Before sharing, perform four review passes over the complete rendered deck, including every backup frame:
    - visual: no overlap among plots, tables, text, legends, titles, or source notes; no clipping, tiny labels, unnecessary density, or inconsistent alignment;
      after the text is stable, enlarge each evidence plot to use the available content area. Judge the visible axes and data region rather than the imported PDF boundary. Large unused areas are acceptable only when further enlargement would crowd text, clip labels, distort the aspect ratio, or weaken a deliberate comparison;
      do not rely on one full-deck thumbnail sheet. Review at most six slides per contact sheet at a resolution where labels are readable, and open every dense plot with an internal legend, colorbar, inset, or ratio panel individually at full rendered size. LaTeX box checks cannot detect overlap already embedded inside a plot PDF.
    - contextual: every claim has the correct date, selection, category, units, source, and meeting-time status;
    - logical: the sequence is goal, current status, work tried, evidence/reasoning, work to try, and conclusion; conclusions do not exceed the evidence.
    - language: a broad technical audience can understand every title, action, and conclusion on first reading; method nicknames are replaced or defined without weakening the claim.
18. Revise and repeat compilation and all four review passes after any material change. Deliver both `.tex` and the current `.pdf` only after every page passes. A slide task is incomplete when the source exists without a successfully rendered and inspected PDF.

## Update Mode

When new plots, tables, JSON, PDFs, or user confirmations arrive before N+1, match each artifact to its stable item number. Update the smallest number of frames, status, evidence source, and carry-forward list. For a requested revision, record the old-to-new artifact mapping and the exact selection, column, uncertainty, or completeness change. Put the revised result and its takeaway in the main deck when it affects a decision; move supporting variants to backup. Preserve the rest of the deck, rerun validation, recompile, and inspect the entire PDF because layout can shift globally. After the N+1 summary is reviewed, reconcile every ledger item against it and convert the preparation deck into the final N-to-N+1 differential.

## Guardrails

- Do not call the transcript summarizer or rewrite source Markdown.
- From only meeting N, create a clearly labeled preparation skeleton. Use `awaiting evidence`, not `done`, for checks that have not yet received results; reserve `not discussed` for retrospective review of meeting N+1.
- Do not use later evidence to silently rewrite the N-to-N+1 differential.
- Do not place unmatched plots side by side without stating every differing selection dimension; identical panel size or axis limits must not imply an otherwise false equivalence.
- Do not give every contributor equal slide space by default; allocate space to decision relevance and evidence.
- Do not open with a presenter-only task list when the source assigns work to several people. Show the whole team first, then move into the presenter's detailed topic.
- Avoid generic section-divider slides, decorative graphics, tiny text, and dense provenance blocks.
- Never allow plots, tables, text, legends, titles, or source notes to overlap. Split the frame when fit is uncertain.
- Treat 15 main frames as the usual planning target, not a pass/fail limit. Do not add filler to reach it or omit necessary evidence to stay near it. Backup frames do not count toward the target.
- Never hand off a `.tex` file alone. If compilation or rendering fails, report the deck as blocked and retain the source for repair; do not present it as completed.
- Keep the Berkeley profile consistent across frames. Use blue for hierarchy, gold only for the split rule and pale block accents, and never color-code contributors.
- Keep both institutional logos on the title page only. Preserve their aspect ratios, clear space, and original colors.
- Use ASCII hyphens in LaTeX source and rendered text.
- Keep source notes legible but subordinate.
- Put source notes at the bottom edge of the content area. Do not leave unused space below them or shrink evidence merely to create a source band.
- Do not leave a plot unnecessarily small when the frame has usable empty space. Increase `\includegraphics` width or height until the visible evidence is easy to read and the surrounding text, source, labels, legends, and ratio panels still fit cleanly.
