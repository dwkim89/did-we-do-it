# Cleanup policy

## Default disposable artifacts

- `.pytest_cache/`
- any `__pycache__/` directory and standalone `.pyc` or `.pyo`
- repository `tmp/`
- `.coverage` and `.DS_Store`
- LaTeX auxiliary files: `.aux`, `.fdb_latexmk`, `.fls`, `.log`, `.nav`, `.out`, `.snm`, `.toc`, `.vrb`
- `slides/**/rendered/` preview directories after visual inspection
- empty top-level `meetings/` and `state/`

## Opt-in build outputs

With `--include-build-output`, also select top-level `build/`, `dist/`, and any `*.egg-info/`. Confirm that no package is awaiting publication or handoff.

## Protected artifacts

Never select raw transcripts, reviewed summaries, slide source, final slide PDFs, project history, documentation, reviews, source code, tests, examples, configuration, `.git/`, or virtual environments. Do not generalize the allowlist merely because another directory appears unused.

If an artifact is not explicitly covered above, leave it in place and ask the user.
