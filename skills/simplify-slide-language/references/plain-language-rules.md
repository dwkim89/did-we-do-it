# Plain-language rules for technical slides

## The audience test

Assume readers know the field basics but not the project’s internal vocabulary. A word is acceptable when it is standard for that audience, necessary for precision, and clear from the slide itself. Otherwise replace or define it.

Ask: “Can the reader tell what we changed or observed without knowing this method’s nickname?” If not, rewrite it.

## Preferred patterns

| Avoid or define | Prefer on first use |
|---|---|
| ablation | controlled input change; rerun after changing one input group |
| parity gate | first reproduce the stored scores before changing inputs |
| closure | data and MC agree within uncertainty; Data/MC ratio is consistent with one |
| score-response matrix | table showing how scores change in each input test |
| sentinel | special placeholder value |
| stratum / strata | subgroup / subgroups defined by the named selection |
| decorrelate | shuffle the values within a stated subgroup |
| intervention | deliberate input change |
| marginal distribution | one-variable distribution |
| conditioned on | after selecting; within events that satisfy |
| domain mismatch | Data values differ from the range or pattern represented in training |

Keep standard physics notation and exact variable names when they are clearer than a paraphrase. Define uncommon acronyms and project-specific working-point names.

## Rewrite method labels as actions

- “Coordinate ablation” becomes “Rerun after changing one coordinate group at a time.”
- “Permutation test” becomes “Shuffle complete cell records and rerun the model.”
- “Parity failed” becomes “The unchanged rerun did not reproduce the stored scores.”
- “Closure improves” becomes “The Data/MC efficiency ratio moves closer to one.”

## Preserve evidence strength

Plain language must not turn association into cause.

- Keep “is associated with” when no controlled input change was performed.
- Use “causes” only when the test supports a causal interpretation and controls are stable.
- Keep uncertainty, sample limitations, and selection boundaries visible.
- Prefer “does not explain the full effect” over “is irrelevant” when a residual remains.

## Slide-level review

For each slide, verify:

1. The title states the takeaway or question.
2. The first sentence supplies any context required to understand the evidence.
3. Each bullet contains one action, result, or implication.
4. Method names are replaced by what was actually done.
5. The conclusion answers the stated question without exceeding the evidence.
6. A reader does not need to reread the slide or search earlier slides for a definition.
