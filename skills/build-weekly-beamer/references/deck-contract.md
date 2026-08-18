# Weekly Beamer contract

## Narrative roles

Mark every deck role in the `.tex` source with `% role: NAME`:

1. `goal` - project target for this reporting period
2. `motivation` - why the work or decision matters now
3. `current-status` - present state of the project or workstream
4. `follow-up` - status of actions requested previously
5. `differential` - what changed from meeting N to meeting N+1
6. `attempts` - work already tried, including unsuccessful or inconclusive checks
7. `evidence` - plot, table, metric, or observation tied to a stated hypothesis
8. `reasoning` - what the evidence implies and why
9. `next` - owner, concrete work to try, and confirmed due date or success criterion
10. `conclusion` - key takeaways and decisions needed

Roles may share a frame, but the first occurrence of the core roles must follow
`goal`, `current-status`, `attempts`, `next`, `conclusion`. State the takeaway in
each frame title instead of repeating the role name.

## Visual system

- Use the Berkeley presentation profile consistently:
  - Berkeley blue `#003262` for titles, bullets, and primary hierarchy;
  - California gold `#FDB515` for the second half of the title rule;
  - charcoal `#1F2933`, slate `#52606D`, white, and light gray for body text and surfaces;
  - pale gold `#FFF6D6` only for restrained block-title accents.
- Draw the rule under every frame title as two equal halves: Berkeley blue on the left and California gold on the right.
- Use TeX Gyre Heros through LuaLaTeX. Use regular weight for body text and bold for the deck title and claim-based frame titles.
- Use a white background. Do not add gradients, decorative backgrounds, saturated status colors, or a different color per contributor.
- Keep both approved institutional logos on the title page only. Put UC Berkeley at lower left and Berkeley Lab at lower right, preserve aspect ratio and clear space, and balance their visible heights.
- Source approved logo files from the tracked `slides/assets/` directory, copy them into each deck's local `assets/` directory, and never recreate or alter them. Ask the user when either asset is unavailable.
- Use color only to establish hierarchy or draw attention to one conclusion.
- Keep alignment, margins, title placement, source notes, and page numbers consistent.

## Density and evidence

- Maximum two plots per frame; one is preferred.
- Maximum six `\item` entries per frame.
- No `\tiny` or `\scriptsize` body text.
- Use no fixed maximum frame count. Add a frame for a distinct, necessary point;
  never add filler or compress evidence merely to meet a target length.
- Each evidence frame must state one hypothesis or question and say whether the
  displayed result supports, challenges, or leaves it unresolved.
- Prefer vector PDF for plots. Use high-resolution PNG only when vector output is unavailable.
- Preserve plot axis labels, units, legends, aspect ratio, uncertainty, and source filename.
- Make the visible evidence as large as the frame safely allows. If labels are hard to read while blank space remains, increase the imported width or height. Inspect the visible axes and data region because internal PDF margins can make a nominally wide image appear small; use `trim` and `clip` only when they remove empty margins without cutting labels, legends, uncertainty, or ratio panels.
- Use JSON values exactly as supplied; create a compact table only when it clarifies the claim.

When plots or tables are not yet available, retain a clearly labeled evidence placeholder. Do not fabricate an example result. The skeleton must still contain goal, motivation, previous actions, expected evidence, reasoning questions, next actions, and conclusion criteria.

## Language and source notes

- Write for university students who know the field basics but not the project history.
- Prefer short, direct wording: “Forward efficiency is lower in data,” not “A degradation of the signal efficiency is observed in the forward region.”
- Use familiar labels. Replace vague project terms such as “grid,” “framework,” or “closure” with the concrete object or result unless the term is defined.
- Replace method nicknames with the action a collaborator must perform. Use “rerun after changing one input group” instead of “ablation,” and “first reproduce the stored scores” instead of “parity gate.” Use the `simplify-slide-language` skill for the final wording pass.
- Remove filler, repeated setup, and unnecessary articles when the message remains natural.
- Aim for one idea per sentence and about ten words per frame title.
- Place the source note at the bottom of the content area, below the evidence. Keep it legible and concise; move detailed provenance to notes or a report.

## Multi-contributor synthesis

Organize primarily by workstream, deliverable, or decision. Within a workstream, label the contributor and their evidence. Do not concatenate contributor decks. Use the repeated pattern: outcome, evidence, blocker, next action.

## Previous-action tracking

In preparation mode use `awaiting evidence`, `in progress`, `blocked`, `needs confirmation`, or `done`. In retrospective differential mode, `not discussed` is also valid. Absence of discussion is never proof of completion. Preserve a faithful compact version of the prior request, stable ID, and owner when known.

Every item not marked `done` must appear in the next to-do list unless the user explicitly closes or drops it. Record that disposition; never let an item disappear because a later meeting or artifact is silent.

## Meeting-to-meeting differential

- Meeting N defines the prior action, question, decision, or requested check.
- Meeting N+1 defines its presentation status and the evidence for what changed.
- Before N+1, meeting N may generate a preparation skeleton. Label all supplied
  results as `pre-meeting evidence` and leave missing evidence as a specific placeholder.
- Every material prior commitment appears in the differential, even when N+1 did not discuss it.
- Contributor artifacts support claims but do not override reviewed summaries. Evidence created after N+1 must be labeled `later resolution`.
- The final action frame contains work requested at N+1 for checking at N+2; do not mix it with the N-to-N+1 status table.
- Produce a complete multi-frame argument. Length follows the number of necessary
  claims, comparisons, and actions rather than a preset upper limit.

## Matched visual differential

- Prefer old-versus-new panels when a plot directly answers a prior request.
- Match variable, conversion/category, eta and pT intervals, bin edges, normalization, axis limits, ratio range, and panel size.
- Put the prior result on the left and the current result on the right. Label the date and selection change above each panel.
- Preserve axes, units, legends, uncertainty, sample counts, and source filenames.
- If compatible current JSON slices partition the old interval, aggregate those slices before plotting and record the components in the source note.
- If any material dimension cannot be matched, state the mismatch on the frame and treat the comparison as contextual rather than controlled.

## Production pipeline

The final artifact is an editable `.tex` plus its compiled and visually verified
`.pdf`. Never treat source-only output as a completed deck.

1. Compile with `latexmk -lualatex` for reproducible reruns and modern font handling.
2. Check the PDF structure with qpdf when available.
3. Render every PDF page through Ghostscript when available; this detects problems that source inspection misses.
4. Generate PNG previews with Ghostscript or Poppler and visually inspect every page.
5. Confirm fonts are embedded with `pdffonts` when available.
6. Review the rendered deck visually: check overlap, clipping, hierarchy,
   alignment, plot legibility, and source-note placement.
7. Review it contextually: check date, selection, category, units, provenance,
   contributor, and whether evidence is meeting-time or later resolution.
8. Review it logically: check the goal-to-conclusion sequence, ensure each
   evidence frame addresses its hypothesis, and weaken any unsupported conclusion.
9. Confirm the delivered PDF was compiled from the delivered TeX after the last
   material edit. Deliver both files together.

Beamer already creates vector PDF. Do not round-trip through PowerPoint or rasterize the entire deck; those steps reduce editability without improving quality.
