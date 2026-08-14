---
name: audit-skill-orthogonality
description: Audit proposed, edited, or installable agent skills against repository-local and environment-installed skills to prevent overlapping triggers, responsibilities, outputs, and mutation authority. Use before creating, renaming, updating, or installing any skill, whenever multiple skills may trigger together, or when skill behavior interferes with another skill. Report conflicts and recommend narrower boundaries; do not install or rewrite skills itself.
---

# Audit Skill Orthogonality

Keep the skill library composable by assigning one clear owner to each responsibility.

## Workflow

1. Inventory candidate and existing `SKILL.md` files. For Codex, include `${CODEX_HOME}/skills` when set, otherwise `~/.codex/skills`. Include the repository's `skills/`. Add another environment only when its skill root is known.
2. Run:

   `python3 scripts/audit_skills.py --candidate-root <repo>/skills --existing-root <installed-root>`

3. Read the full `SKILL.md` for every candidate and each tool-flagged neighbor. The token score is triage, not a semantic decision.
4. Compare each pair on:

   - triggering phrases and timing;
   - inputs and source of truth;
   - outputs and filenames;
   - mutation authority and side effects;
   - lifecycle stage and handoff target;
   - explicit non-goals.

5. Classify the pair:

   - `orthogonal`: distinct responsibility and artifact ownership;
   - `complementary`: may trigger together but have an explicit order and handoff;
   - `overlap`: competing ownership or indistinguishable triggers;
   - `conflict`: same name with different content or contradictory authority.

6. Block installation on `conflict`. For `overlap`, narrow descriptions and non-goals, merge the skills, or define routing before installation.
7. Write a concise audit under `docs/` when the audit influences a design or installation decision.

## Required Audit Record

For each relevant pair, record classification, shared surface, distinct ownership, invocation order if complementary, and any remediation. Do not claim orthogonality solely from a low token-similarity score.

## Boundaries

- Do not perform the task owned by the audited skills.
- Do not edit or install skills; return a decision for the creator or installer.
- Do not treat environment-specific mirrors of identical skill content as conflicts.
