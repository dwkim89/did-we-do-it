# DidWeDoIt

DidWeDoIt turns Zoom-format plain-text meeting transcripts into inspectable JSON,
a Markdown report, and a self-contained HTML dashboard. It keeps continuity with
the previous meeting while refusing to commit vague extracted items until a person
reviews them.

This repository contains a compact deterministic core plus a remote CBORG
DeepThought adapter. An optional Ollama adapter remains available for local
open-weight models, and the offline heuristic extractor is a conservative fallback
and test path.

## Input contract

The only required input is a UTF-8 `.txt` file exported in the Zoom layout:

```text
07:00:02 --> 07:00:04
Person Name: Spoken text.
```

The filename must contain the meeting date as `YYYYMMDD`, for example
`20260115_Weekly.txt`. Dates mentioned inside a discussion may refer to experiments,
deadlines, or previous meetings, so they are not used as the canonical meeting date.

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[test]'

didwedoit init
```

`init` writes a readable `didwedoit.toml`. The default provider is the remote
CBORG DeepThought model, configured through an HTTPS OpenAI-compatible endpoint.
Keep the API token in the environment rather than this repository:

```toml
[analysis]
provider = "cborg"
model = "cborg-deepthought"
chunk_chars = 40000
```

Then verify and produce the simple, editable meeting summary:

```bash
didwedoit doctor
didwedoit summarize transcripts/20260115_Weekly.txt --series research-project
```

This writes `summaries/20260115_research-project.md` with Key outcomes, Decisions made,
Open Questions, Pending Confirmation, and Action items. Optional contributor,
risk, and topic sections are added only when useful. The transcript is sent to the
configured remote provider; the result is validated locally. Ambiguous items stay
as unchecked Markdown entries for user confirmation, so routine review does not
require editing JSON.

The earlier canonical-history workflow is still available through `process`. For
a local open-weight model, configure `provider = "ollama"` and its exact model name.
The Ollama adapter accepts only `localhost` or `127.0.0.1`, so transcript content
does not leave the machine on that path.

To exercise the framework before installing a model:

```bash
didwedoit process transcripts/20260115_Weekly.txt --series research-project --provider heuristic
```

If extraction is uncertain, `process` writes a JSON bundle under `reviews/` and
does not modify `meetings/`. In an interactive terminal it offers to review now.
For every vague item choose:

- `a` to confirm it;
- `e` to correct it and confirm it; or
- `d` to discard it.

You can resume later:

```bash
didwedoit review reviews/2026-08-05_<checksum>.json
```

Advanced users may edit that JSON directly. `didwedoit approve FILE` refuses to
commit while any item still has `needs_review: true`.

After approval, outputs are intentionally few and editable:

```text
meetings/research-project/2026-01-15_<meeting-id>/
├── meeting.json
├── report.md
└── dashboard.html
```

`meeting.json` is canonical. Reports can always be regenerated from it. Transcript
content is not copied and no telemetry exists. Ollama traffic is restricted to the
configured loopback address; the heuristic fallback makes no network requests.

## Commands

```text
didwedoit init [WORKSPACE]
didwedoit summarize TRANSCRIPT.txt [--series NAME] [--workspace DIR]
didwedoit process TRANSCRIPT.txt [--series NAME] [--workspace DIR]
didwedoit doctor [--provider NAME] [--model NAME] [--json]
didwedoit review REVIEW.json [--workspace DIR]
didwedoit approve REVIEW.json [--workspace DIR]
didwedoit list [--series NAME] [--json]
didwedoit show MEETING_ID [--json]
```

## End-to-end workflow

The project uses four plain, inspectable artifact stages:

```text
transcripts/YYYYMMDD_*.txt
        |
        v
summaries/YYYYMMDD_<series>.md      reviewed meeting record
        |                    \
        v                     v
slides/YYYYMMDD_<series>/weekly-update.tex  project-history/<series>.md
        |
        v
slides/YYYYMMDD_<series>/weekly-update.pdf
```

1. Run `summarize` and resolve every material item under Pending Confirmation.
2. Compare two consecutive reviewed summaries. Meeting N supplies the actions and questions; meeting N+1 supplies evidence for `done`, `in progress`, `blocked`, `not discussed`, or `needs confirmation`.
3. Build the meeting N+1 weekly deck with the differential, contributor evidence, reasoning, new actions for N+2, and a decision checkpoint. A one-frame status page is not a weekly deck.
4. Add user-supplied plots, JSON results, or contributor material, then compile with LuaLaTeX.
5. Validate the PDF with qpdf, render every page with Ghostscript or Poppler, verify embedded fonts, and inspect every preview.
6. Update `project-history/<series>.md` from reviewed summaries for a concise longitudinal record.

Beamer already produces vector PDF. LuaLaTeX improves font handling; qpdf and
Ghostscript improve validation rather than replacing Beamer. Prefer vector PDF
plots, with high-resolution PNG only when vector output is unavailable.

## Design boundaries

- The source file is never modified.
- Evidence retains original physical line numbers, timestamps, speaker, and a short excerpt.
- Unassigned work stays unassigned.
- A prior action absent from the current meeting is `not discussed`, never completed.
- Historical fuzzy matches below the automatic threshold require human review.
- If ownership, status, evidence, or an artifact choice is materially unclear, ask the user before treating it as confirmed.
- HTML escapes transcript-derived content and loads no remote assets.
- JSON files and a compact Python package are preferred over a database and deep directory hierarchy.

## Skills

The editable source skills under `skills/` have intentionally separate ownership:

- `summarize-meeting-markdown` turns one dated Zoom TXT transcript into reviewable Markdown through the configured remote LLM;
- `build-weekly-beamer` compares two consecutive reviewed summaries and turns their action/status differential plus supplied evidence into a multi-frame Beamer deck and verified PDF;
- `maintain-project-history` consolidates reviewed meeting summaries into one longitudinal record per meeting series;
- `clean-workspace-artifacts` previews and removes allowlisted caches, temporary render files, and optional build outputs after testing;
- `capture-hourly-progress` writes `docs/YYYYMMDD_HH_TZ_brief-description.md` after roughly one hour of observable active work;
- `consolidate-daily-progress` reads one local day's hourly reports and writes `docs/YYYYMMDD_daily-summary_brief-description.md`;
- `audit-skill-orthogonality` checks new or changed skills against repository and installed skills before installation.

Codex copies are installed under `~/.codex/skills/`. Repository copies remain canonical so changes can be reviewed and versioned. Skills run during active agent turns; exact unattended wall-clock execution requires a separate scheduler.

Cleanup is dry-run-first:

```bash
python3 skills/clean-workspace-artifacts/scripts/clean_workspace.py --root .
python3 skills/clean-workspace-artifacts/scripts/clean_workspace.py --root . --include-build-output --apply
```

The cleaner never selects transcripts, summaries, slides, final PDFs, project history, docs, reviews, source, tests, or configuration.

See `MEETING_INTELLIGENCE_PRODUCT_TECHNICAL_SPEC.md` for the long-term product
contract. Richer semantic consolidation, model evaluation, status classification,
and migration tooling remain later milestones.
