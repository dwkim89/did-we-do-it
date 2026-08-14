---
name: maintain-framework-readme
description: Audit and update a repository's public README against the implemented CLI, configuration, providers, outputs, tests, privacy rules, and repository-local skills. Use when README.md may be stale, after framework behavior or skills change, before a release or handoff, or when users ask what works now, what needs revision, and what could improve. Update documentation only; do not implement missing features or summarize private project artifacts.
---

# Maintain Framework README

Keep `README.md` accurate, concise, and useful to a new user. Treat executable
code and checked-in configuration as evidence; do not turn plans into current
capabilities.

## Workflow

1. Run the inventory from the repository root:

   ```bash
   python3 skills/maintain-framework-readme/scripts/readme_inventory.py --root .
   ```

2. Read the complete `README.md`. Inspect the files named by the inventory,
   especially `pyproject.toml`, the CLI parser, settings, `.gitignore`, tests,
   and every repository `SKILL.md` description.
3. Classify material README claims as:
   - **current** - directly supported by code, tests, or checked-in workflow;
   - **transitional** - supported but retained for compatibility rather than the
     recommended path;
   - **planned** - not implemented and clearly labeled as a possible improvement.
4. Update the smallest coherent set of README sections. Keep the recommended
   workflow before legacy or optional paths. Include exact privacy boundaries,
   output locations, and commands that can be copied safely.
5. Use generic synthetic filenames and project names. Never copy real
   transcripts, participant names, summaries, slide claims, credentials, local
   absolute paths, or ignored project artifacts into public documentation.
6. When documentation is stale but behavior is clear, correct the README. When
   behavior itself is ambiguous or inconsistent, report it and ask before editing
   implementation code.
7. Rerun the inventory and relevant tests. Run `git diff --check` and verify the
   README does not claim undocumented commands or expose ignored private paths.

## README Content Contract

Prefer this order when the repository supports it:

1. current purpose and primary workflow;
2. input and privacy contract;
3. installation and configuration;
4. primary commands and outputs;
5. weekly slides and project-history handoff;
6. current capability status;
7. transitional or legacy workflows;
8. skills and maintenance commands;
9. known limitations and possible improvements.

Keep planned improvements short and evidence-based. Do not use the README as a
session log, changelog, issue tracker, or long technical specification.

## Boundaries

- Own only public framework documentation in `README.md`.
- Do not summarize raw transcripts or edit meeting summaries, slides,
  project-history records, or `docs/` progress reports.
- Do not modify source code, tests, configuration, or another skill unless the
  user separately requests that change.
- Do not mark a feature complete because it appears in a specification.
- Do not publish, commit, push, or install the skill without user authorization
  and the repository's normal validation or orthogonality checks.
