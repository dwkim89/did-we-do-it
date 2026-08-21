# Berkeley weekly Beamer layout contract

## Core geometry

- Use `\documentclass[aspectratio=169,10pt,t]{beamer}`. The global `t` option is
  important: ordinary slide bodies begin near the title rule instead of being
  vertically centered.
- Use TeX Gyre Heros, a white background, and 0.70 cm left and right text
  margins.
- Frame titles are bold Berkeley blue (`#003262`).
- Place the title rule close to the title. The approved template uses
  `\vspace{0.12cm}` before the title, `\\[-0.04cm]` before the rule, and
  `\par\vspace{0.02cm}` after it.
- Split the rule at half the text width: Berkeley blue on the left and
  California gold (`#FDB515`) on the right.

## Content placement

- Let the first block, table, columns, or plot start immediately below the
  title-rule area. Avoid manual vertical space at the start of a frame unless
  alignment with another frame requires it.
- Keep columns top-aligned with `[T,onlytextwidth]`.
- Add about `0.18cm` before a standalone conclusion that follows columns or a
  block group. Use a slightly smaller gap only when a dense plot or table needs
  it and the rendered separation remains obvious.
- A takeaway such as `Why this matters:`, `Purpose:`, or `Result:` should read
  as a new paragraph. Never place it directly against the last bullet, plot, or
  table rule.
- Use `\vfill` inside the source-note macro so the source remains at the bottom
  while the evidence stays near the title.
- Do not add repeated item/status context strips beneath detailed slide titles.
  Keep item numbers in the opening summary and, when useful, in a slide title.

## Supporting-material divider

The divider immediately after `\appendix` contains only centered
`Supporting material` and one split blue/gold rule above and below. Suppress the
normal frame-title template locally, while retaining a non-empty source title
for structural validators.

```tex
{
\setbeamertemplate{frametitle}{}
\begin{frame}[plain]{Supporting material}
  \centering
  \vfill
  \begin{tikzpicture}
    \draw[berkeleyblue,line width=1.6pt] (0,0) -- (3.2,0);
    \draw[californiagold,line width=1.6pt] (3.2,0) -- (6.4,0);
  \end{tikzpicture}\par
  \vspace{0.40cm}
  {\color{berkeleyblue}\bfseries\fontsize{30}{36}\selectfont Supporting material}\par
  \vspace{0.40cm}
  \begin{tikzpicture}
    \draw[berkeleyblue,line width=1.6pt] (0,0) -- (3.2,0);
    \draw[californiagold,line width=1.6pt] (3.2,0) -- (6.4,0);
  \end{tikzpicture}
  \vfill
\end{frame}
}
```

## Render review

Inspect every changed frame at readable resolution. Confirm:

- the title and rule do not collide;
- the rule is visually close to the title;
- content begins near the rule and is not vertically centered;
- conclusion lines have an intentional gap above them;
- tables, plots, legends, source notes, and buttons do not overlap;
- the divider has no upper-left title or ordinary title rule;
- `Supporting material` stays on one line between the two split rules.
