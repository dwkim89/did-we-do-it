---
name: apply-berkeley-beamer-layout
description: Apply or review the approved Berkeley weekly-update layout for LaTeX Beamer decks. Use when creating a new weekly deck, restyling an existing deck, or checking title rules, content placement, takeaway spacing, source notes, and the supporting-material divider. Do not use it to decide the scientific narrative or alter evidence.
---

# Apply Berkeley Beamer Layout

Use the repository's approved Berkeley weekly-presentation layout. Read
[references/layout-contract.md](references/layout-contract.md) before editing a
deck. For a new deck, start from
[assets/berkeley-beamer-layout.tex](assets/berkeley-beamer-layout.tex), or copy
its layout definitions into the project deck.

## Workflow

1. Preserve the slide content, evidence, selection, uncertainty, and source
   notes. This skill controls presentation layout, not scientific conclusions.
2. Use a 16:9, 10-point, globally top-aligned Beamer document. Keep the title
   page separate from ordinary frames.
3. Put the bold Berkeley-blue frame title close to a thin rule split equally
   between Berkeley blue and California gold. Start the body near that rule;
   do not vertically center short slide bodies.
4. Use white backgrounds, dark neutral body text, pale-gray block bodies, and
   pale-gold block headings. Keep page numbers small at bottom right.
5. Add a visible blank gap before a standalone takeaway placed after columns,
   a table, or a plot. Examples include “Why this matters,” “Purpose,” and
   “Result.” The takeaway must not look attached to the preceding object.
6. Keep the opening follow-up table authoritative. Do not add a repeated
   `Item N | request | status` strip under later slide titles. An item number may
   remain in a title when it helps navigation.
7. Immediately after `\appendix`, add one divider containing only centered
   `Supporting material`, with a split blue/gold rule above and below. Suppress
   the ordinary upper-left frame title and title rule on this divider.
8. Compile with LuaLaTeX, render every page, and inspect the visible layout.
   Check title-rule distance, body start position, takeaway spacing, clipping,
   source-note placement, and the supporting-material divider. LaTeX box checks
   do not replace visual inspection.

The maintained template in this skill is the canonical visual reference. A
project deck may be used as an additional comparison when supplied, but the
skill must remain usable without private or ignored meeting material.
