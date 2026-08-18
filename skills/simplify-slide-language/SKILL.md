---
name: simplify-slide-language
description: Review and rewrite technical presentation text so a broad scientific or university audience can follow it on the first reading without losing accuracy. Use when creating or editing Beamer, PowerPoint, Google Slides, speaker notes, slide titles, bullets, tables, captions, or handoff instructions; when a user says wording is awkward, jargon-heavy, unclear, or hard to follow; or before delivering a technical deck to collaborators outside the immediate analysis team.
---

# Simplify Slide Language

Make every slide understandable at presentation speed. Preserve the claim, selection, uncertainty, and limits of the evidence while replacing method nicknames with concrete actions.

Read [references/plain-language-rules.md](references/plain-language-rules.md) before revising a deck.

## Workflow

1. Identify the audience, the decision they need to make, and the field knowledge they can reasonably share. Do not assume they know project-specific method names.
2. Review all visible text: title, subtitle, bullets, block headings, table headers, annotations, legends added by the deck, conclusion, and next steps. Ignore filenames and exact software or variable names when they must remain literal.
3. Apply the jargon test to each specialist word:
   - use it directly when the target audience will know it;
   - replace it with the concrete action or observation when the term adds no precision;
   - otherwise define it in plain language on first use, then use it consistently.
4. Prefer action and outcome wording. Write “rerun the model after changing one input group” instead of “perform an ablation.” Write “first reproduce the stored scores” instead of “pass the parity gate.”
5. Keep one idea per sentence and one main claim per slide. Use active voice, specific nouns, and short titles. Split a dense slide instead of compressing the wording.
6. Preserve technical meaning. Do not remove qualifiers such as “suggests,” “within uncertainty,” “associated with,” “not yet causal,” or a selection condition merely to shorten the text.
7. Run the language checker on editable text and address every finding:

```bash
python3 skills/simplify-slide-language/scripts/check_slide_language.py PATH/weekly-update.tex
```

   Use `--allow TERM` only when the term is necessary for the audience and is defined on first use.
8. Render the deck and read every slide at normal speaking speed. Revise wording that requires rereading, relies on a later slide for its definition, or is too small because the sentence is too long.

## Completion criteria

- A collaborator can state the slide’s main point after one reading.
- Every necessary specialist term is familiar to the audience or defined where it first appears.
- Titles state outcomes or questions rather than analysis labels.
- Next steps say what will be changed, rerun, compared, and accepted as success.
- Simplification does not strengthen a claim beyond the evidence.
