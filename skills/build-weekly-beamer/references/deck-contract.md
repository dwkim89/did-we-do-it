# Weekly Beamer contract

## Narrative roles

Mark every deck role in the `.tex` source with `% role: NAME`:

1. `goal` - project target for this reporting period
2. `motivation` - why the work or decision matters now
3. `follow-up` - status of actions requested previously
4. `differential` - what changed from meeting N to meeting N+1
5. `progress` - evidence organized by workstream or contributor
6. `reasoning` - what the evidence implies and why
7. `actions` - owner, concrete next step, and confirmed due date
8. `conclusion` - key takeaways and decisions needed

Roles may share a frame. State the takeaway in each frame title instead of repeating the role name.

## Visual system

- Use a white background, charcoal text, muted navy as the single accent, and light gray rules or panels.
- Do not add gradients, decorative backgrounds, saturated status colors, or a different color per contributor.
- Use one sans-serif family with regular and bold weights. The template uses TeX Gyre Heros through LuaLaTeX.
- Use color only to establish hierarchy or draw attention to one conclusion.
- Keep alignment, margins, title placement, source notes, and page numbers consistent.

## Density and evidence

- Maximum two plots per frame; one is preferred.
- Maximum six `\item` entries per frame.
- No `\tiny` or `\scriptsize` body text.
- Each plot must support a sentence-level claim stated on the frame.
- Prefer vector PDF for plots. Use high-resolution PNG only when vector output is unavailable.
- Preserve plot axis labels, units, legends, aspect ratio, uncertainty, and source filename.
- Use JSON values exactly as supplied; create a compact table only when it clarifies the claim.

When plots or tables are not yet available, retain a clearly labeled evidence placeholder. Do not fabricate an example result. The skeleton must still contain goal, motivation, previous actions, expected evidence, reasoning questions, next actions, and conclusion criteria.

## Language and source notes

- Write for university students who know the field basics but not the project history.
- Prefer short, direct wording: “Forward efficiency is lower in data,” not “A degradation of the signal efficiency is observed in the forward region.”
- Use familiar labels. Replace vague project terms such as “grid,” “framework,” or “closure” with the concrete object or result unless the term is defined.
- Remove filler, repeated setup, and unnecessary articles when the message remains natural.
- Aim for one idea per sentence and about ten words per frame title.
- Place the source note at the bottom of the content area, below the evidence. Keep it legible and concise; move detailed provenance to notes or a report.

## Multi-contributor synthesis

Organize primarily by workstream, deliverable, or decision. Within a workstream, label the contributor and their evidence. Do not concatenate contributor decks. Use the repeated pattern: outcome, evidence, blocker, next action.

## Previous-action tracking

Use exactly these states: `done`, `in progress`, `blocked`, `not discussed`, `needs confirmation`. Absence of discussion is never proof of completion. Preserve a faithful compact version of the prior request and its owner when known.

## Meeting-to-meeting differential

- Meeting N defines the prior action, question, decision, or requested check.
- Meeting N+1 defines its presentation status and the evidence for what changed.
- Every material prior commitment appears in the differential, even when N+1 did not discuss it.
- Contributor artifacts support claims but do not override reviewed summaries. Evidence created after N+1 must be labeled `later resolution`.
- The final action frame contains work requested at N+1 for checking at N+2; do not mix it with the N-to-N+1 status table.
- Produce a complete 6--10 frame weekly deck. A single progress frame is not compliant.

## Matched visual differential

- Prefer old-versus-new panels when a plot directly answers a prior request.
- Match variable, conversion/category, eta and pT intervals, bin edges, normalization, axis limits, ratio range, and panel size.
- Put the prior result on the left and the current result on the right. Label the date and selection change above each panel.
- Preserve axes, units, legends, uncertainty, sample counts, and source filenames.
- If compatible current JSON slices partition the old interval, aggregate those slices before plotting and record the components in the source note.
- If any material dimension cannot be matched, state the mismatch on the frame and treat the comparison as contextual rather than controlled.

## Production pipeline

1. Compile with `latexmk -lualatex` for reproducible reruns and modern font handling.
2. Check the PDF structure with qpdf when available.
3. Render every PDF page through Ghostscript when available; this detects problems that source inspection misses.
4. Generate PNG previews with Ghostscript or Poppler and visually inspect every page.
5. Confirm fonts are embedded with `pdffonts` when available.

Beamer already creates vector PDF. Do not round-trip through PowerPoint or rasterize the entire deck; those steps reduce editability without improving quality.
