# DidWeDoIt

DidWeDoIt turns dated Zoom-format text transcripts into concise, reviewable
meeting summaries. Reviewed summaries then support weekly progress slides and a
longitudinal project history.

The primary workflow is deliberately simple:

```text
transcript TXT
    -> reviewed Markdown summary
    -> weekly Beamer progress deck
    -> longitudinal project history
```

The framework keeps uncertainty visible. Unclear answers, owners, decisions, and
commitments remain under `Pending Confirmation` until a user resolves them.

## Current framework

| Capability | Status | Current role |
|---|---|---|
| Zoom TXT ingestion and filename dates | Current | Parses UTF-8 Zoom transcripts and takes the canonical meeting date from the first isolated `YYYYMMDD` token in the filename. |
| Markdown meeting summary | Primary | `didwedoit summarize` writes the editable record used by later skills. |
| CBORG DeepThought provider | Default | Remote structured extraction through an HTTPS OpenAI-compatible endpoint. |
| Ollama provider | Optional | Local open-weight inference restricted to loopback addresses; performance depends on local hardware. |
| Heuristic provider | Development fallback | Deterministic, conservative extraction for tests and offline framework checks; not a replacement for semantic review. |
| Weekly Beamer deck | Current, skill-driven | Compares consecutive reviewed summaries and adds selected plots or contributor evidence. |
| Project history | Current, skill-driven | Consolidates reviewed summaries into one longitudinal record per series. |
| JSON review and HTML dashboard | Transitional | Older `process`/`review`/`approve` workflow retained for compatibility. It is not the recommended path. |
| Hourly and daily progress reports | Current, active-session skills | Run during an active agent session; no background scheduler is included. |

## Input and privacy contract

The only required input is a UTF-8 `.txt` file exported in the Zoom layout:

```text
07:00:02 --> 07:00:04
Person Name: Spoken text.
```

The filename must contain a usable meeting date as an isolated `YYYYMMDD` token,
for example `20260115_Weekly.txt`. The current parser uses the first matching
token. Dates mentioned during discussion may describe deadlines or earlier
meetings, so transcript content is not used as the canonical date.

Private runtime artifacts are excluded from Git by default:

```text
transcripts/       raw meeting inputs
summaries/         reviewed meeting records
slides/            slide source, evidence, and rendered PDFs
project-history/   longitudinal project records
docs/              interaction and audit reports
meetings/          legacy approved JSON/HTML records
reviews/           legacy pending review bundles
state/             runtime state
didwedoit.toml      local provider configuration
```

Git exclusions do not change provider privacy. CBORG sends transcript content to
the configured remote endpoint. Ollama is restricted to `localhost`,
`127.0.0.1`, or `::1`. The heuristic provider makes no network requests.

## Installation

DidWeDoIt requires Python 3.11 or newer.

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[test]'

didwedoit init
```

`init` writes a local `didwedoit.toml`. The default analysis configuration is:

```toml
[analysis]
provider = "cborg"
model = "cborg-deepthought"
chunk_chars = 40000
context_tokens = 16384
```

For CBORG, set the endpoint and credential in the environment rather than in Git:

```bash
export CBORG_BASE_URL="https://your-cborg-endpoint.example/v1"
export CBORG_API_KEY="your-token"
didwedoit doctor
```

`OPENAI_BASE_URL` may be used instead of `CBORG_BASE_URL`. The implementation
requires HTTPS and suppresses provider response bodies from HTTP errors.

## Primary workflow

Generate one dated Markdown summary:

```bash
didwedoit summarize transcripts/20260115_Weekly.txt \
  --series research-project
```

The output is `summaries/20260115_research-project.md` with these stable sections:

- Key outcomes
- Decisions made
- Open Questions
- Pending Confirmation
- Action items

Contributor progress, topics, risks, blockers, or reasoning are included only
when supported by the transcript. The generated file begins as `status: draft`.
Resolve material unchecked items with the user before changing it to
`status: reviewed` or using its claims in slides and project history.

### Weekly slides

Use `build-weekly-beamer` after two consecutive summaries are reviewed. Meeting N
provides prior requests and action items; meeting N+1 provides evidence of what
changed. The skill writes:

```text
slides/YYYYMMDD_<series>/weekly-update.tex
slides/YYYYMMDD_<series>/weekly-update.pdf
```

The deck is a 6-10 frame progress story, not a one-page summary. It tracks prior
actions with the exact states `done`, `in progress`, `blocked`, `not discussed`,
or `needs confirmation`. Supplied plots, JSON, or contributor slides are selected
for decision relevance, with at most two plots per frame.

### Project history

Use `maintain-project-history` after summaries are reviewed. It reads only dated
meeting summaries and updates:

```text
project-history/<series>.md
```

Raw transcripts and agent-session reports are not sources for project history.

## Implemented CLI commands

```text
didwedoit init [WORKSPACE]
didwedoit summarize TRANSCRIPT.txt [--series NAME] [--workspace DIR]
                    [--provider NAME] [--model NAME] [--force]
didwedoit doctor [--workspace DIR] [--provider NAME] [--model NAME] [--json]

# Transitional canonical JSON/HTML workflow
didwedoit process TRANSCRIPT.txt [--series NAME] [--workspace DIR]
                  [--provider NAME] [--model NAME]
didwedoit review REVIEW.json [--workspace DIR]
didwedoit approve REVIEW.json [--workspace DIR]
didwedoit list [--series NAME] [--workspace DIR] [--json]
didwedoit show MEETING_ID [--workspace DIR] [--json]
```

Valid provider names are `cborg`, `ollama`, and `heuristic`.

## Transitional workflow needing revision

The older `process` command builds canonical `meeting.json`, `report.md`, and a
self-contained `dashboard.html`. Ambiguous results first enter `reviews/` as JSON
plus an HTML preview and require `review` or `approve` before they enter
`meetings/`.

This path is still implemented and tested, but the project now uses editable
Markdown summaries as the human review surface. Unless JSON/HTML canonical state
is needed, prefer `summarize` and the summary/slide/history skills.

One implementation detail remains transitional: `init`, `summarize`, and
`process` share the same workspace initializer, so they currently create empty
`meetings/`, `reviews/`, and `state/` directories even when only the Markdown
workflow is used. These directories are ignored by Git and may be removed when
empty, but a later run can recreate them.

## Repository skills

Repository copies under `skills/` are canonical and reviewable:

- `summarize-meeting-markdown` - convert one dated Zoom transcript into reviewed Markdown;
- `build-weekly-beamer` - build and verify a differential weekly Beamer deck;
- `maintain-project-history` - maintain the longitudinal record from reviewed summaries;
- `maintain-framework-readme` - verify this README against implemented behavior;
- `clean-workspace-artifacts` - preview and remove allowlisted disposable artifacts;
- `capture-hourly-progress` - record evidence from a long active work interval;
- `consolidate-daily-progress` - consolidate one day of hourly reports;
- `audit-skill-orthogonality` - prevent competing skill ownership and triggers.

Installed Codex copies normally live under `~/.codex/skills/`. Skills execute
during active agent turns. Unattended wall-clock execution requires a separate
scheduler.

## Testing and maintenance

After an editable installation:

```bash
python3 -m pytest -q
```

Without installing the package first:

```bash
PYTHONPATH=src python3 -m pytest -q
```

The current suite covers transcript ingestion, dated summary structure, CBORG and
Ollama adapters, historical reconciliation, HTML escaping, and cleanup safety.

Review this README against the implementation:

```bash
python3 skills/maintain-framework-readme/scripts/readme_inventory.py --root .
```

Cleanup is dry-run-first. Apply exactly the selection that was previewed:

```bash
python3 skills/clean-workspace-artifacts/scripts/clean_workspace.py --root .
python3 skills/clean-workspace-artifacts/scripts/clean_workspace.py --root . --apply
```

To include reproducible package builds, preview and apply with the same additional
flag:

```bash
python3 skills/clean-workspace-artifacts/scripts/clean_workspace.py \
  --root . --include-build-output
python3 skills/clean-workspace-artifacts/scripts/clean_workspace.py \
  --root . --include-build-output --apply
```

The cleaner protects transcripts, summaries, slide source, final PDFs, project
history, documentation, reviews, source code, tests, and configuration.

## Known limitations and possible improvements

1. Decide whether to remove or migrate the transitional JSON/HTML review path,
   then stop the primary Markdown workflow from creating its empty directories.
2. Enforce exactly one valid filename date token instead of accepting the first
   match when a filename contains multiple `YYYYMMDD` values.
3. Add CLI commands for weekly-deck and project-history orchestration if those
   workflows should run without an agent skill.
4. Add provider-quality evaluation fixtures for summary accuracy, ambiguity
   handling, and meeting-to-meeting consistency; current tests validate behavior
   and schemas, not scientific or semantic correctness.
5. Add continuous integration for tests, README inventory, formatting, and secret
   scanning. The repository currently relies on local validation.
6. Add an optional scheduler only if unattended hourly/daily reporting is needed;
   keep scheduled execution separate from skill definitions.
7. Add a migration command if existing canonical `meetings/` records need to
   become reviewed Markdown summaries.

See `MEETING_INTELLIGENCE_PRODUCT_TECHNICAL_SPEC.md` for the longer-term product
contract. Specification text is not evidence that a feature is implemented.

## Design boundaries

- Never modify the source transcript.
- Preserve original line numbers, timestamps, speaker, and short evidence excerpts.
- Keep unassigned work unassigned.
- Treat silence as `not discussed`, never as completion.
- Ask the user when ownership, status, evidence, or interpretation is unclear.
- Escape transcript-derived HTML and load no remote dashboard assets.
- Prefer compact files and shallow, inspectable directories over a database.
