---
name: clean-workspace-artifacts
description: Preview and remove disposable caches, temporary render files, empty runtime directories, and optionally generated build distributions from this repository. Use after tests, LaTeX/PDF checks, packaging, or other workspace validation leaves generated artifacts. Always dry-run first and never remove transcripts, summaries, slides, final PDFs, project history, docs, reviews, source, tests, or configuration.
---

# Clean Workspace Artifacts

Remove reproducible debris without treating domain artifacts as temporary data.

Read [references/cleanup-policy.md](references/cleanup-policy.md) before applying a cleanup.

## Workflow

1. Inspect repository status and identify user-owned or unfamiliar files before classifying anything.
2. Preview the default cleanup:

```bash
python3 skills/clean-workspace-artifacts/scripts/clean_workspace.py --root .
```

3. Add `--include-build-output` only when generated `build/`, `dist/`, or `*.egg-info` artifacts are reproducible and not intended for release or handoff.
4. Show the exact paths, reasons, and total bytes to the user. Ask before applying when any classification or intent is unclear.
5. Apply the identical selection with `--apply`. Do not add new flags between preview and apply.
6. Run relevant tests or checks, then run another dry-run to confirm only newly regenerated caches remain.

## Boundaries

- Never delete domain inputs or outputs, including `transcripts/`, `summaries/`, `slides/`, final PDFs, `project-history/`, `docs/`, `reviews/`, or meeting JSON.
- Never delete unfamiliar files, dirty tracked files, credentials, environments, or repository metadata.
- Treat build distributions as opt-in because they may be release deliverables.
- Keep cleanup deterministic and repository-scoped. Refuse roots without both `pyproject.toml` and `skills/`.
- Report what was deleted and that deletion is not recoverable unless another copy exists.
