# DidWeDoIt

DidWeDoIt turns an existing meeting summary or a dated Zoom-format text
transcript into concise, reviewable Markdown. Reviewed summaries then support
weekly progress slides and a longitudinal project history.

The primary workflow is deliberately simple:

```text
existing summary (preferred) or transcript TXT
    -> normalized, reviewed Markdown summary
    -> weekly Beamer progress deck
    -> longitudinal project history
```

The framework keeps uncertainty visible. Unclear answers, owners, decisions, and
commitments remain under `Pending Confirmation` until a user resolves them.

## Current framework

| Capability | Status | Current role |
|---|---|---|
| Existing-summary normalization | Current, skill-driven | Prefers a supplied Zoom AI or human-written summary and normalizes it without an LLM API call by default. |
| Zoom TXT ingestion and filename dates | Current | Parses UTF-8 Zoom transcripts and takes the canonical meeting date from the first isolated `YYYYMMDD` token in the filename. |
| Markdown meeting summary | Primary | `didwedoit summarize` writes the editable record used by later skills. |
| CBORG provider | Default | Remote structured extraction with `gpt-5.6-luna-medium` through an HTTPS OpenAI-compatible endpoint. |
| Ollama provider | Optional | Local open-weight inference restricted to loopback addresses; performance depends on local hardware. |
| Heuristic provider | Development fallback | Deterministic, conservative extraction for tests and offline framework checks; not a replacement for semantic review. |
| HEP validation plots | Current, skill-driven | Produces checked vector PDFs and machine-readable JSON sidecars with propagated statistical uncertainties. |
| Weekly Beamer deck | Current, skill-driven | Builds an N+1 preparation deck from one reviewed summary, then a final differential from two consecutive reviewed summaries. |
| Project history | Current, skill-driven | Consolidates reviewed summaries into one longitudinal record per series. |
| JSON review and HTML dashboard | Transitional | Older `process`/`review`/`approve` workflow retained for compatibility. It is not the recommended path. |
| Hourly and daily progress reports | Current, active-session skills | Run during an active agent session; no background scheduler is included. |

## Input and privacy contract

The preferred input is an existing Zoom AI or human-written meeting summary in
Markdown, text, PDF, or DOCX. The summary skill reads it directly, normalizes it
to the canonical headings, and does not make an LLM API call by default. Its
filename must contain the meeting date as an isolated `YYYYMMDD` token.

When no usable summary exists, provide a UTF-8 `.txt` transcript exported in the
Zoom layout:

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
transcripts/          raw meeting inputs
summaries/            reviewed meeting records
slides/YYYYMMDD_*/    dated slide source, evidence, and rendered PDFs
branding/             other local branding material
project-history/      longitudinal project records
docs/                 interaction and audit reports
meetings/             legacy approved JSON/HTML records
reviews/              legacy pending review bundles
state/                runtime state
didwedoit.toml         local provider configuration
```

The exception is `slides/assets/`, which contains approved reusable logos and is
tracked. The public repository therefore contains framework code, tests, skills,
documentation, and shared presentation assets, but no meeting records or dated
project decks.

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
model = "gpt-5.6-luna-medium"
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
CBORG access and an endpoint are not provided by this repository. Users without
access should configure local Ollama or select the heuristic development fallback.

## Primary workflow

If a dated meeting summary already exists, ask the agent to apply
`summarize-meeting-markdown` to that file. This summary-first path is
skill-driven: it preserves the source file, records provenance, and uses the raw
transcript only for targeted verification when necessary.

When only a transcript is available, generate one dated Markdown summary with
the CLI:

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

### Validation plots

Use `build-hep-validation-plots` to produce data/MC overlays, ratio panels, or
scale-factor figures from histogram or binned analysis outputs. Each result has
a vector PDF and a machine-readable JSON sidecar containing the bin contents,
`sumw2` statistical uncertainties, selection, normalization, and provenance.
The skill checks for empty histograms, invalid values or variances, inconsistent
binning, undefined derived bins, and missing uncertainty metadata.

The plotting skill owns numerical figure production, not physics diagnosis or
slide layout. Pass checked PDF/JSON artifacts to `build-weekly-beamer`; use a
separate HEP QA workflow when a discrepancy needs interpretation.

### Weekly slides

The usual workflow starts `build-weekly-beamer` after meeting N is reviewed.
Meeting N supplies prior requests, open questions, pending confirmations, and
action items. The skill creates a structured deck for N+1 with specific evidence
placeholders for plots, tables, metrics, external PDFs, or user confirmation.
It writes:

```text
slides/YYYYMMDD_<series>/weekly-update.tex
slides/YYYYMMDD_<series>/weekly-update.pdf
```

These files are one output pair. The framework does not treat a TeX-only deck as
complete: every material edit must be recompiled, rendered, and visually checked
before the `.tex` and current `.pdf` are shared together.

The default Berkeley presentation profile uses TeX Gyre Heros, bold blue message
titles, a half-blue/half-gold title rule, neutral content surfaces, and approved
UC Berkeley and Berkeley Lab logos on the title page. Reusable approved logos
are tracked at:

```text
slides/assets/uc-berkeley-logo.png
slides/assets/berkeley-lab-logo.png
```

The slide skill copies these shared assets into each private deck. Dated deck
source, rendered output, and meeting-specific material remain excluded from Git.
Follow the applicable institutional brand guidance when reusing the logo files.

Each follow-up item receives a stable ID, owner, evidence requirement, success
criterion, and preparation status. Results supplied before N+1 are labeled
`pre-meeting evidence`; missing results remain `awaiting evidence`. Items not
finished before N+1 stay visible in its to-do list and later carry into N+2 unless
evidence marks them `done` or the user explicitly closes them.

The main deck normally aims for about 15 frames, including the title and
conclusion, without treating that number as a quota. An early “last week in
review” frame summarizes material requests and status. Each related evidence or
action frame repeats only its stable ID, compact prior request, and current
status. Decision-relevant results stay in the main narrative; alternate
selections, supporting plots, full tables, and detailed provenance go after
`\appendix` as backup.

Requests from meeting N to add a plot selection, uncertainty, region, or table
field remain attached to the original stable ID. The workflow keeps the earlier
artifact, records the exact requested change, and produces a versioned
replacement when traceable inputs are available. HEP plots are regenerated by
`build-hep-validation-plots`; the slide skill places the checked PDF/JSON result
and keeps missing inputs as explicit placeholders.

After the N+1 summary is reviewed, the same deck becomes the final N-to-N+1
differential. `not discussed` is used only at this retrospective stage. The deck
follows goal, last week in review, current status, work tried, evidence and
reasoning, work to try next, and conclusion. It uses at most two plots per
evidence frame and receives visual, contextual, and logical review before sharing.

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

- `summarize-meeting-markdown` - normalize an existing meeting summary, or convert a dated Zoom transcript, into reviewed Markdown;
- `build-hep-validation-plots` - produce checked HEP plots with uncertainties and JSON sidecars;
- `build-weekly-beamer` - prepare or update a Berkeley-profile weekly Beamer deck and verify its PDF;
- `simplify-slide-language` - make technical slide wording clear without weakening its claims;
- `maintain-project-history` - maintain the longitudinal record from reviewed summaries;
- `maintain-framework-readme` - verify this README against implemented behavior;
- `publish-safe-repository-files` - stage reusable files without publishing private meeting material;
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

Validate, compile, and render a Berkeley-profile weekly deck:

```bash
python3 skills/build-weekly-beamer/scripts/validate_beamer.py \
  slides/YYYYMMDD_example/weekly-update.tex \
  --brand-profile berkeley --compile --engine lualatex \
  --render-dir slides/YYYYMMDD_example/rendered
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

The cleaner protects transcripts, summaries, slide source, final PDFs, shared
and deck-local assets, project history, documentation, reviews, source code,
tests, and configuration.

## Known limitations and possible improvements

1. Decide whether to remove or migrate the transitional JSON/HTML review path,
   then stop the primary Markdown workflow from creating its empty directories.
2. Enforce exactly one valid filename date token instead of accepting the first
   match when a filename contains multiple `YYYYMMDD` values.
3. Add CLI commands for validation-plot, weekly-deck, and project-history
   orchestration if those workflows should run without an agent skill.
4. Add provider-quality evaluation fixtures for summary accuracy, ambiguity
   handling, and meeting-to-meeting consistency; current tests validate behavior
   and schemas, not scientific or semantic correctness.
5. Add continuous integration for tests, README inventory, formatting, and secret
   scanning. The repository currently relies on local validation.
6. Add an optional scheduler only if unattended hourly/daily reporting is needed;
   keep scheduled execution separate from skill definitions.
7. Add a migration command if existing canonical `meetings/` records need to
   become reviewed Markdown summaries.
8. Select and add a repository license before inviting external reuse. No
   `LICENSE` file is currently included.

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
