# Meeting Intelligence Framework

## Public-Launch Product and Technical Specification

**Working product name:** DidWeDoIt<br>
**Repository placeholder:** `did-we-do-it`<br>
**Document status:** Implementation-ready specification<br>
**Target release:** MVP `0.1.0`<br>
**Primary platforms:** macOS and Linux<br>
**Primary interface:** Local command-line application<br>
**MVP input:** One UTF-8 plain-text (`.txt`) meeting transcript per run

> This document is the source of truth for the MVP. It is intentionally written so it can be provided to Codex as a single implementation brief. “DidWeDoIt” is a working name and may be changed without altering product scope.

---

## 1. Executive Summary

DidWeDoIt is a local-first, open-source meeting-intelligence framework for research groups and other small teams. A user supplies a plain-text meeting transcript. The application automatically generates:

1. a structured meeting summary;
2. questions raised and their resolution state;
3. decisions and conclusions;
4. action items, with owners only when supported by the transcript;
5. blockers, risks, and unresolved issues;
6. a self-contained, manager-friendly HTML dashboard; and
7. a comparison with the previous meeting showing what was completed, progressed, changed, blocked, introduced, resolved, or not discussed.

The product’s defining capability is continuity across meetings. It must not merely summarize an isolated transcript. It must preserve structured history, reconcile current statements with earlier action items and questions, and provide an evidence-backed account of change over time.

The application runs locally on macOS and Linux. Meeting content and generated artifacts remain on the user’s machine except when the user explicitly configures a remote language-model provider. The MVP does not include a hosted service, web accounts, collaborative editing, transcript recording, or audio/video ingestion.

---

## 2. Product Principles

1. **History is the product.** The cross-meeting differential is a first-class output, not an optional report.
2. **Structured data is the source of truth.** Markdown and HTML are rendered from validated records, never treated as canonical state.
3. **Evidence over confidence theater.** Material claims link to transcript evidence. Uncertainty is visible and machine-readable.
4. **No invented accountability.** The system must not fabricate owners, due dates, decisions, answers, or completion.
5. **Local-first by default.** No account, daemon, hosted database, or networked dashboard is required.
6. **Reviewable automation.** Users can understand what was extracted, why it was extracted, and what changed.
7. **Portable and maintainable.** The same documented workflow works in supported macOS and Linux terminals.
8. **Useful before clever.** Clear tables, labels, and accessible HTML take priority over visually complex graphics.

---

## 3. Problem Statement

Recurring meetings produce transcripts but often fail to produce reliable organizational memory. Summaries lose commitments, questions remain unresolved, and later meetings describe prior work in different words. Managers and principal investigators must reconstruct progress manually.

Existing transcript summarizers commonly treat each meeting in isolation. They may generate plausible prose, but do not reliably preserve stable item identities, distinguish “not discussed” from “completed,” or show evidence for inferred status changes. DidWeDoIt addresses this gap with a persistent, local history and an explicit reconciliation stage.

### 3.1 Product hypothesis

If a team can turn each transcript into traceable structured records and see the change from the previous meeting in one local report, then meeting follow-through becomes faster, clearer, and less dependent on individual memory.

### 3.2 MVP success measures

For pilot teams using the tool for at least four consecutive meetings:

- at least 90% of successful runs produce all required artifacts without manual file repair;
- at least 80% of human-confirmed action items are present in the generated record;
- fewer than 5% of extracted action items contain an owner not supported by evidence;
- 100% of reported completions contain current-meeting evidence;
- users can locate blocked work, unresolved questions, and newly completed work in under two minutes;
- a new user can install, initialize, and process the sample transcript by following the README alone.

Quality measures must be evaluated on an annotated, non-sensitive fixture set. They are release goals, not claims that an LLM is infallible.

---

## 4. Goals and Non-Goals

### 4.1 MVP goals

- Accept a single `.txt` transcript and optional command-line metadata.
- Normalize common plain-text transcript styles without requiring one vendor format.
- Extract a structured summary, topics, questions, decisions, conclusions, actions, blockers, and risks.
- Preserve transcript evidence for every action, decision, blocker, status transition, and answered question.
- Validate all model output before committing state.
- Assign an action owner only when the transcript supports the assignment; otherwise use `null` and display “Unassigned.”
- Maintain stable IDs and append-only change events across recurring meetings.
- Compare the current meeting to the chronologically previous meeting in the same series.
- Distinguish `not_discussed` from completion or cancellation.
- Produce consistent Markdown, JSON, and self-contained HTML outputs.
- Provide an offline-capable application path when a compatible local model provider is configured.
- Provide safe, documented support for an optional remote model provider.
- Be installable as a Python package and runnable through a stable CLI on macOS and Linux.
- Be suitable for public source distribution, external contributions, and semantic releases.

### 4.2 Non-goals for MVP

- Audio/video ingestion, transcription, diarization, or live meeting capture.
- PDF, DOCX, VTT, SRT, or cloud-document input. MVP input is `.txt` only.
- A hosted SaaS product, shared server, user accounts, or organization administration.
- Real-time collaboration, notifications, calendar integration, or task-system synchronization.
- Automatic emailing, messaging, or assignment notifications.
- Editing canonical records through the dashboard.
- Perfect identity resolution across people with ambiguous names.
- Arbitrary comparison between any two meetings; MVP compares with the previous meeting in a series.
- Fully autonomous changes to historical records without validation and an audit event.
- Fine-tuning models, training on user data, or collecting transcripts for product analytics.
- Windows support in the MVP. It may work but is not a release-gated platform.

---

## 5. Personas and Jobs to Be Done

### 5.1 Principal investigator or manager

**Need:** Understand progress, stalled work, unresolved questions, ownership gaps, and decisions without rereading a full transcript.

**Success:** Opens one dashboard and immediately sees the meeting delta and high-attention items.

### 5.2 Researcher or team member

**Need:** Confirm what they committed to, what was decided, and which questions remain open.

**Success:** Finds accurate actions and evidence, and can flag uncertain extraction for later correction.

### 5.3 Meeting organizer or project coordinator

**Need:** Process recurring transcripts consistently and retain an auditable history.

**Success:** Runs one command, receives deterministic artifact locations, and can rerun safely.

### 5.4 Maintainer or contributor

**Need:** Extend providers, extraction logic, or reports without destabilizing storage and history.

**Success:** Uses documented interfaces, fixtures, and tests; CI catches schema and output regressions.

---

## 6. Core User Journeys

### 6.1 First use

1. User installs the supported Python package.
2. User runs `didwedoit init` in a chosen workspace.
3. The application creates configuration, input, state, and output directories without overwriting existing files.
4. User selects/configures a local or remote model provider and validates it with `didwedoit doctor`.
5. User processes the included sample transcript.
6. The application produces a meeting record, reports, and dashboard and prints their paths.

### 6.2 Process the first real meeting in a series

1. User places a UTF-8 `.txt` transcript in the input directory.
2. User runs `didwedoit process path/to/transcript.txt --series lab-weekly --date 2026-08-08`.
3. The application validates input and displays which provider will receive transcript content.
4. It extracts and validates a current meeting record.
5. Because no earlier meeting exists in the series, it creates a baseline comparison that explicitly says “No previous meeting.”
6. It atomically commits state and writes all outputs.

### 6.3 Process the next meeting

1. User runs `process` with the same series.
2. The application identifies the latest earlier meeting by meeting date, not file modification time.
3. It extracts the current meeting, proposes links to historical items, and records confidence and evidence.
4. It classifies prior items as completed, progressed, still open, blocked, changed, cancelled, or not discussed.
5. It creates `comparison.md` and a dashboard that foreground the delta.
6. Ambiguous links remain separate or are flagged for review; they are not silently merged.

### 6.4 Recover from an interrupted or invalid run

1. Extraction or validation fails.
2. The application keeps the prior canonical state unchanged.
3. It writes a sanitized diagnostic record outside the canonical meeting directory and exits nonzero.
4. User corrects configuration or retries.
5. The rerun either resumes safe cached stages or replaces only a matching incomplete run.

### 6.5 Reproduce or inspect a result

1. User runs `didwedoit show <meeting-id>` or opens the artifact directory.
2. The record identifies schema version, application version, provider, model identifier, prompt/template version, configuration fingerprint, input checksum, creation time, and evidence.
3. The original transcript copy is available only if transcript retention is enabled.

---

## 7. Functional Requirements

Requirements use `FR-###` identifiers for tests and release tracking.

### 7.1 Initialization and configuration

- **FR-001:** `init` creates a workspace only in the user-selected directory.
- **FR-002:** `init` is idempotent and never overwrites non-generated configuration without `--force` and a confirmation.
- **FR-003:** Configuration precedence is CLI arguments, environment variables, project configuration, then built-in defaults.
- **FR-004:** `doctor` verifies Python/runtime compatibility, writable paths, configuration syntax, provider availability, and model connectivity where applicable.
- **FR-005:** `config show` prints effective non-secret configuration and the source of each value.

### 7.2 Transcript ingestion

- **FR-010:** Reject inputs whose extension is not `.txt` in the MVP.
- **FR-011:** Accept UTF-8 and UTF-8-with-BOM; report an actionable error for unsupported encoding.
- **FR-012:** Preserve the original file; never edit it in place.
- **FR-013:** Normalize line endings, Unicode whitespace, and repeated blank lines while retaining an immutable line map to the original.
- **FR-014:** Recognize common speaker-line and optional timestamp patterns without requiring timestamps.
- **FR-015:** Reject an empty transcript and enforce configurable byte and character/token safety limits before sending content to a provider.
- **FR-016:** Compute a SHA-256 input checksum and detect duplicate processing in the same series.
- **FR-017:** Accept metadata via flags: series, date, title, and optional participant aliases. If date is absent and cannot be safely inferred, fail with an instruction to supply it.

### 7.3 Extraction

- **FR-020:** Produce a validated `MeetingRecord` containing metadata, executive summary, topics, questions, decisions, conclusions, action observations, blockers, and risks.
- **FR-021:** Treat transcript content as untrusted data, not executable instructions. Prompt-like statements in transcripts must be summarized as meeting content and must not alter application behavior.
- **FR-022:** Every material extracted item contains one or more evidence references or is marked `needs_review`.
- **FR-023:** Evidence includes original line start/end and, when present, timestamp and speaker. Short excerpts are optional and configurable.
- **FR-024:** An owner, due date, answer, decision, or commitment may be populated only when supported by evidence.
- **FR-025:** Uncertainty is represented with `confidence` and `needs_review`; prose must not hide uncertainty.
- **FR-026:** Model/provider output is parsed as structured data and validated. Free-form output is never directly committed as canonical state.
- **FR-027:** The system attempts one configurable repair pass for invalid structured output, then fails safely.
- **FR-028:** The system supports transcripts larger than one model context through deterministic, overlap-aware chunking and a final consolidation stage.
- **FR-029:** Repeated facts from chunks are deduplicated without discarding distinct actions that happen to use similar wording.

### 7.4 History and reconciliation

- **FR-030:** Each series has an ordered sequence of meetings and its own item namespace.
- **FR-031:** Stable IDs use type-prefixed, zero-padded identifiers such as `AI-0001`, `Q-0001`, `D-0001`, and `B-0001`.
- **FR-032:** Existing stable IDs are never reused for different entities.
- **FR-033:** Reconciliation uses deterministic candidate retrieval plus model-assisted or rule-based classification; model output cannot directly mutate state.
- **FR-034:** A link decision stores current evidence, prior item ID, relation, confidence, and method/version.
- **FR-035:** Low-confidence matches are not merged automatically. They produce a review warning and preserve both records.
- **FR-036:** “Not mentioned” is represented as `not_discussed`; it is never treated as completed, cancelled, or resolved.
- **FR-037:** Completion requires affirmative current-meeting evidence.
- **FR-038:** Status transitions are validated against an allowed transition table. Exceptional transitions require a recorded reason.
- **FR-039:** Historical changes are append-only events. Current state is a projection of those events.
- **FR-040:** The previous meeting is the meeting with the greatest date/time earlier than the current meeting in the same series; ties require explicit disambiguation.
- **FR-041:** Processing a meeting dated before the current latest meeting requires `--allow-backfill` and rebuilds later projections deterministically or fails without mutation.

### 7.5 Differential

- **FR-050:** Every run creates a differential, including a baseline differential for the first meeting.
- **FR-051:** Differential categories include completed, progressed, still open, newly blocked, unblocked, changed, cancelled, not discussed, new actions, new/resolved questions, and new/changed decisions.
- **FR-052:** Each reported transition links prior state, current evidence, conclusion, and confidence.
- **FR-053:** The differential highlights management attention: overdue or repeatedly deferred items, blocked dependencies, missing owners, reversed decisions, and recurring unanswered questions.
- **FR-054:** Counts in Markdown, JSON, and HTML must derive from the same projection and agree exactly.

### 7.6 Reports and dashboard

- **FR-060:** Successful processing writes `meeting.json`, `summary.md`, `questions.md`, `action_items.md`, `decisions.md`, `comparison.md`, `dashboard.html`, and `run.json`.
- **FR-061:** Reports are generated from validated structured state using versioned templates.
- **FR-062:** The dashboard is a self-contained local HTML document that requires no server and makes no network requests.
- **FR-063:** The dashboard contains snapshot metrics, meeting delta, attention items, action status, workload by owner, unanswered questions, decisions, and a recent timeline.
- **FR-064:** Tables remain useful without JavaScript. Optional sorting/filtering progressively enhances the page.
- **FR-065:** Charts have adjacent textual values or accessible tables and are not the sole means of conveying information.
- **FR-066:** `export` can regenerate reports from canonical state without calling an LLM.

### 7.7 Idempotency and lifecycle

- **FR-070:** Reprocessing the same checksum, effective configuration, prompt version, and model identifier returns the existing successful run unless `--rerun` is supplied.
- **FR-071:** `--dry-run` validates and shows planned reads/writes/provider use without sending transcript content or mutating state.
- **FR-072:** Canonical state is written only after all required validation passes.
- **FR-073:** Temporary writes use a staging directory and atomic rename on the same filesystem.
- **FR-074:** `delete` is not an MVP command. Manual deletion and recovery behavior must be documented.

---

## 8. Output Contract

### 8.1 Workspace layout

```text
did-we-do-it-workspace/
├── didwedoit.toml
├── transcripts/                 # user-managed inputs
├── meetings/                    # generated, human-readable artifacts
│   └── lab-weekly/
│       └── 2026-08-08_<meeting-id>/
│           ├── transcript.txt   # optional; controlled by retention setting
│           ├── meeting.json
│           ├── summary.md
│           ├── questions.md
│           ├── action_items.md
│           ├── decisions.md
│           ├── comparison.md
│           ├── dashboard.html
│           └── run.json
├── state/                       # application-managed canonical state
│   ├── schema_version
│   ├── series/
│   └── index.json
├── cache/                       # disposable; contains no secrets
└── diagnostics/                 # sanitized run diagnostics
```

Generated directories are application-managed. Users should make corrections through a future review workflow or by rerunning; editing rendered Markdown does not update canonical state.

### 8.2 Summary format

`summary.md` uses this stable order:

1. meeting information;
2. executive summary;
3. topics discussed;
4. key decisions;
5. questions;
6. action items;
7. blockers and risks;
8. conclusions;
9. items needing review;
10. provenance.

### 8.3 Example `comparison.md`

```markdown
# Changes Since Previous Meeting

## Executive Delta

- Completed: 1
- Progressed: 1
- Newly blocked: 1
- New actions: 2
- Unanswered questions: 1

## Management Attention

- **AI-0007 — Validate detector calibration** is blocked by unavailable reference data.
- **AI-0009 — Select baseline model** remains unassigned.

## Completed

### AI-0003 — Rerun the learning-rate experiment

- Owner: Alice
- Previous state: In progress
- Current state: Completed
- Evidence: lines 44–47
- Conclusion: Alice reported that the rerun finished and results were uploaded.
- Confidence: High

## Not Discussed

- AI-0005 — Draft the methods section

> Not discussed does not imply completion.
```

### 8.4 Example manager snapshot

```text
OPEN ACTIONS       8
COMPLETED          1
BLOCKED            2
NEW                2
UNANSWERED         1

Delta: +2 new · 1 completed · 1 progressed · 1 newly blocked
```

### 8.5 Example action item JSON

```json
{
  "id": "AI-0003",
  "description": "Rerun the learning-rate experiment at 0.001",
  "owner_person_id": "P-0001",
  "status": "completed",
  "priority": "unspecified",
  "due_date": null,
  "created_in_meeting_id": "M-20260801-01",
  "updated_in_meeting_id": "M-20260808-01",
  "confidence": "high",
  "needs_review": false,
  "evidence": [
    {
      "meeting_id": "M-20260808-01",
      "line_start": 44,
      "line_end": 47,
      "speaker": "Alice",
      "timestamp": "00:18:12"
    }
  ]
}
```

---

## 9. Data Model

Implement schema models with strict validation and explicit schema versions. Pydantic is recommended for runtime models; JSON Schema should be exportable for provider contracts and interoperability.

### 9.1 Enumerations

- `Confidence`: `high`, `medium`, `low`
- `ActionStatus`: `new`, `open`, `in_progress`, `blocked`, `completed`, `cancelled`, `unknown`
- `QuestionStatus`: `answered`, `partially_answered`, `unanswered`, `deferred`, `unknown`
- `Priority`: `high`, `medium`, `low`, `unspecified`
- `Severity`: `high`, `medium`, `low`, `unspecified`
- `DeltaKind`: `created`, `progressed`, `blocked`, `unblocked`, `completed`, `changed`, `cancelled`, `not_discussed`, `resolved`, `reopened`

Do not encode `not_discussed` as an action’s durable business status. It is an observation in a meeting differential.

### 9.2 Core entities

**MeetingSeries**

- `id`, `slug`, `display_name`, `created_at`, `meeting_ids`, `next_id_counters`

**MeetingRecord**

- `schema_version`, `id`, `series_id`, `title`, `date`, optional `start_time`, `participants`, `executive_summary`, `topics`, `questions`, `action_observations`, `decisions`, `conclusions`, `blockers`, `risks`, `source`, `provenance`, `created_at`

**Person**

- `id`, `display_name`, `aliases`, optional `canonical_key`, `needs_review`

**Topic**

- `id`, `title`, `summary`, related entity IDs, evidence

**Question**

- `id`, `text`, optional asker/addressee IDs, status, optional answer, topic IDs, evidence, confidence, `needs_review`

**ActionItem**

- `id`, `description`, optional owner ID, collaborator IDs, status, priority, optional due date, topic IDs, dependency IDs, created/updated meeting IDs, confidence, `needs_review`

**ActionObservation**

- `meeting_id`, optional prior action ID, observed description/status, relationship claim, evidence, confidence, `needs_review`

**Decision**

- `id`, `description`, optional rationale, participant IDs, topic IDs, supersedes ID, evidence, confidence, `needs_review`

**Blocker**

- `id`, `description`, optional owner ID, affected action IDs, severity, status, evidence, confidence

**EvidenceRef**

- `meeting_id`, source checksum, normalized/original line range, optional speaker, optional timestamp, optional excerpt

**StateEvent**

- `id`, series ID, meeting ID, entity type/ID, event type, prior/new values, evidence IDs, confidence, method/version, recorded time

**Differential**

- current/previous meeting IDs, categorized transitions, management attention, counts, warnings

**RunManifest**

- run ID/status, application/schema/template versions, start/end time, platform/Python version, input checksum, provider and model identifier, configuration fingerprint, stages, warnings, artifact checksums, sanitized error

### 9.3 Storage choice

For MVP, use versioned JSON files with atomic writes and a small repository abstraction. This keeps state inspectable and avoids requiring a database. Do not expose file-layout assumptions beyond the repository interface. A future SQLite migration must be possible through explicit, tested schema migrations.

### 9.4 Migration policy

- Every canonical record includes `schema_version`.
- Readers support the current schema and documented migration from at least the previous minor schema.
- Migrations are explicit, backed up, idempotent, and covered by golden fixtures.
- Unknown future schema versions fail closed with an upgrade instruction.
- Rendering old records must not call an LLM.

---

## 10. Architecture

### 10.1 Logical pipeline

```text
TXT transcript
  → input validation and normalization
  → chunking (when required)
  → structured extraction
  → schema validation and repair
  → candidate retrieval from series history
  → reconciliation and transition validation
  → append-only events and state projection
  → Markdown/JSON/HTML rendering
  → atomic commit and run manifest
```

### 10.2 Components

1. **CLI layer:** argument parsing, user messaging, exit codes, orchestration.
2. **Configuration layer:** typed settings, precedence, secret references, validation.
3. **Ingestion layer:** file validation, encoding, line mapping, metadata, normalization, chunking.
4. **Provider abstraction:** structured generation interface, capabilities, retries, timeout, redacted diagnostics.
5. **Extraction layer:** versioned prompts/contracts, validation, consolidation, confidence policy.
6. **History repository:** series records, stable IDs, event log, projection, atomic persistence, migrations.
7. **Reconciliation engine:** candidate selection, matching, transition rules, ambiguity handling.
8. **Reporting layer:** deterministic Markdown, JSON, and static HTML rendering.
9. **Provenance/diagnostics:** run manifests, checksums, versions, safe error details.

### 10.3 Dependency direction

Domain models and policy must not import CLI, provider SDKs, or report templates. Provider implementations and storage implementations depend on interfaces defined by the application/domain layer. The reconciliation engine accepts structured records and repository interfaces, making it testable without network access.

### 10.4 Suggested repository structure

```text
did-we-do-it/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── pyproject.toml
├── didwedoit.example.toml
├── src/didwedoit/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── domain/
│   ├── ingestion/
│   ├── extraction/
│   ├── providers/
│   ├── history/
│   ├── reconciliation/
│   ├── reports/
│   │   └── templates/
│   └── diagnostics/
├── tests/
│   ├── fixtures/
│   ├── golden/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── examples/
├── docs/
└── .github/
    ├── workflows/
    ├── ISSUE_TEMPLATE/
    └── pull_request_template.md
```

### 10.5 Technology baseline

- Python 3.11 or newer, with the exact supported range declared in `pyproject.toml`.
- Standard `src/` package layout and PEP 517/518 build.
- A maintained CLI library or standard library parser; choose one and keep the public command contract stable.
- Pydantic for validated domain/provider schemas.
- Jinja2 or equivalent for deterministic report templates.
- Local static HTML/CSS with minimal vendored JavaScript only if needed.
- `pytest` for tests; a single formatter/linter and a static type checker enforced in CI.

Pin lower bounds intentionally and use a lock or constraints strategy for development/release reproducibility. Avoid heavy frontend and data-science dependencies for the MVP.

---

## 11. Provider and Local-First Design

### 11.1 Provider contract

Define an `AnalysisProvider` interface that accepts normalized/chunked transcript data plus a versioned output schema and returns provider-agnostic structured data. The interface must expose:

- provider/model identifier;
- structured-output capability;
- context/input limit information when available;
- timeout and retry policy;
- health check;
- extraction and optional reconciliation operations.

Provider-specific SDK objects must not leak into domain models.

### 11.2 Local provider

The architecture must support at least one documented local provider path for offline use. The local model/runtime is a user-installed optional dependency and must be capability-checked by `doctor`. “Local-first” means the product and state run locally; the quality and hardware requirements of a particular model must be documented honestly.

### 11.3 Remote provider

A remote provider is opt-in. Before the first remote run, documentation and CLI output must make clear that transcript content will leave the machine and identify the configured provider. Credentials come only from environment variables or supported OS/user secret mechanisms—not committed TOML, CLI flags, logs, manifests, or generated reports.

### 11.4 Determinism and model drift

- Use the most deterministic supported settings suitable for extraction.
- Record the concrete provider and model identifier returned/configured for every run.
- Version prompts, schemas, reconciliation rules, and templates independently.
- Do not promise byte-identical LLM output across providers or time.
- Golden tests use fake/replay providers; CI must not depend on a live paid API.

---

## 12. CLI Specification

Executable name: `didwedoit`.

```bash
didwedoit --help
didwedoit --version

didwedoit init [DIRECTORY] [--force]
didwedoit doctor [--provider NAME] [--json]
didwedoit config show [--json]

didwedoit process TRANSCRIPT.txt \
  --series SERIES \
  --date YYYY-MM-DD \
  [--title TITLE] \
  [--provider NAME] \
  [--model MODEL] \
  [--dry-run] \
  [--rerun] \
  [--allow-backfill] \
  [--json]

didwedoit list [--series SERIES] [--json]
didwedoit show MEETING_ID [--json]
didwedoit export MEETING_ID [--format all|markdown|html|json]
didwedoit history [--series SERIES] [--json]
```

### 12.1 CLI behavior

- Default output is concise, human-readable, and never prints transcript content.
- `--json` sends a stable machine-readable result to stdout; human diagnostics go to stderr.
- Non-interactive commands never hang on a prompt. Required confirmation in a non-TTY fails with instructions.
- Every mutating run prints its planned workspace, series, input, provider mode, and artifact location.
- Success output links or prints absolute paths to the dashboard and comparison report.
- Help includes examples and privacy-relevant flags.

### 12.2 Exit codes

- `0`: success
- `2`: CLI usage or configuration error
- `3`: invalid or unsupported input
- `4`: provider unavailable, unauthorized, timed out, or rate limited
- `5`: structured output or schema validation failure
- `6`: history/reconciliation conflict
- `7`: filesystem or atomic commit failure
- `8`: unsupported schema/application version
- `1`: unexpected internal error

---

## 13. Configuration Contract

Example `didwedoit.toml`:

```toml
config_version = 1

[workspace]
transcripts_dir = "transcripts"
meetings_dir = "meetings"
state_dir = "state"
cache_dir = "cache"
diagnostics_dir = "diagnostics"
retain_transcript_copy = true
retain_evidence_excerpt = true

[analysis]
provider = "local"
model = "user-configured-model"
chunk_size = 12000
chunk_overlap = 500
repair_attempts = 1
minimum_auto_link_confidence = 0.85

[privacy]
allow_remote_provider = false
telemetry = false
redact_evidence_in_diagnostics = true

[reports]
dashboard = true
theme = "system"
recent_meeting_count = 8
```

Rules:

- Paths in project configuration resolve relative to the configuration file.
- Environment variables use the `DIDWEDOIT_` prefix and nested `__` separators.
- Unknown keys are errors, not silently ignored.
- Secrets are never accepted in project configuration.
- Invalid enum/range/path combinations fail before provider calls.
- `config show` redacts secret-like environment values and prints remote/local mode.
- Configuration and privacy defaults are documented in one reference page generated from the typed settings.

---

## 14. Privacy, Security, and Trust

### 14.1 Privacy stance

- No account is required.
- No transcript, evidence, summary, or action item is sent anywhere unless the configured provider requires it and the user has enabled remote processing.
- Telemetry is disabled and absent by default for the MVP.
- No training or product analytics use of user transcript data is performed by this application.
- Provider data-handling terms are outside this application’s control and must be clearly linked/documented by provider adapters.
- Users control transcript-copy retention and can keep original inputs outside the workspace.

### 14.2 Threat model

Treat transcripts, filenames, configuration, provider responses, and historical state as untrusted. Address at minimum:

- prompt injection embedded in a transcript;
- malicious HTML/Markdown in meeting content;
- path traversal via series/title/filename;
- symlink and unsafe overwrite behavior;
- secret leakage in logs, errors, manifests, or reports;
- oversized input and resource exhaustion;
- malformed provider output;
- partial/corrupt state writes;
- spreadsheet-formula-style injection in future exports;
- dependency and release artifact compromise.

### 14.3 Required controls

- Delimit transcript data and instruct providers that it is inert source content.
- Validate provider responses against strict schemas and allowlists.
- HTML-escape all user/model content. Do not render untrusted raw HTML.
- Sanitize generated path slugs and verify resolved paths remain inside the workspace.
- Do not follow unsafe output symlinks; use exclusive/staged writes and atomic rename.
- Enforce input size, stage timeout, retry, and output size limits.
- Redact API keys, authorization headers, transcript excerpts, and likely secrets from diagnostics.
- Use secure temporary files with user-only permissions where supported.
- Keep provider/network code separated from deterministic rendering and history.
- Scan dependencies and the repository in CI; publish checksums and build provenance when supported.
- Provide a `SECURITY.md` with private vulnerability-reporting instructions and supported versions.

### 14.4 Consent and sensitive meetings

The README must tell deployers to confirm participant consent and organizational policy before processing or retaining transcripts. The application must not claim compliance with HIPAA, GDPR, FERPA, or other regimes without a separate legal/security assessment. Public examples and test fixtures must be synthetic and contain no real meeting data.

---

## 15. Telemetry and Logging

### 15.1 Telemetry

MVP ships with no outbound product telemetry. Do not include analytics SDKs, crash-reporting beacons, hidden update checks, or remote fonts/assets. A future telemetry proposal requires a separate public design review, explicit opt-in, a documented event schema, data minimization, and a deletion/disable mechanism. Transcript content and derived meeting intelligence must never be telemetry.

### 15.2 Local logs

- Default log level is `INFO`; no transcript body or evidence excerpts are logged.
- `--verbose` adds stage/timing details, not content.
- `--debug` remains content-safe and may include stack traces with path/secret redaction.
- Diagnostics have configurable retention and can be deleted without harming canonical state.
- A run ID connects terminal output, diagnostics, and `run.json`.

---

## 16. Error Handling and Recovery

Errors must identify: what failed, whether state changed, the likely remedy, the run ID, and where safe diagnostics exist.

### 16.1 Failure policy

- Validate cheaply before expensive/provider operations.
- Retry only transient provider/network errors, using bounded exponential backoff and jitter.
- Do not retry authentication, schema, policy, or invalid-input errors automatically.
- Never commit partial canonical state.
- Preserve successful prior state and rendered outputs on failure.
- Quarantine staging artifacts from failed runs and expire them safely.
- Provide a clear error when a workspace lock is active; stale locks are recoverable through a documented procedure.
- Detect corrupt JSON/checksum mismatch and fail closed with backup/recovery instructions.

### 16.2 Human-readable example

```text
Processing stopped: the provider returned data that did not match the meeting schema.
No meeting history was changed.
Run: R-20260808-143210-a1b2
Next: verify the selected model supports structured output, then rerun `didwedoit doctor`.
```

---

## 17. Accessibility and Readability

- Dashboard targets WCAG 2.2 AA for applicable static content and interactions.
- Use semantic headings, landmarks, lists, tables, captions, and real buttons/links.
- All functions are keyboard accessible with visible focus.
- Do not communicate status by color alone; use text labels and symbols.
- Maintain at least AA contrast in light and dark/system themes.
- Respect `prefers-reduced-motion`; avoid animated charts in MVP.
- Charts include textual summaries and accessible data tables.
- Tables have scoped headers and remain readable on narrow screens.
- Use plain language, short management summaries, and consistent status vocabulary.
- Markdown reports remain complete without HTML or JavaScript.
- Dates use ISO format in canonical output; localized presentation may be future work.
- Accessibility is tested with automated checks plus keyboard and screen-reader smoke testing before public release.

---

## 18. Performance and Reliability Targets

- CLI startup/help under 1 second on a typical supported developer laptop, excluding first environment activation.
- Deterministic local stages process a 1 MB transcript in under 5 seconds, excluding model/provider time.
- Dashboard opens locally and becomes readable in under 2 seconds for 100 meetings and 2,000 actions on a typical laptop.
- No canonical corruption after simulated interruption at each write stage.
- Rendering the same canonical state with the same template version is byte-stable except explicitly documented timestamps.
- Support at least 100 meetings per series and 2,000 tracked action items in MVP tests.
- Provider timeout, chunking, and retry limits are configurable with safe defaults.

---

## 19. Testing Strategy

### 19.1 Test layers

**Unit tests**

- normalization and original-line mapping;
- typed configuration and precedence;
- schema validation and unknown-field handling;
- stable ID allocation;
- transition-table enforcement;
- candidate ranking, confidence thresholds, and no-silent-merge behavior;
- path sanitization and HTML escaping;
- dashboard metric calculations;
- exit-code mapping.

**Integration tests**

- complete pipeline with a fake/replay provider;
- multi-chunk consolidation and deduplication;
- first meeting, second meeting, and backfill cases;
- atomic writes, locks, interruption, and recovery;
- schema migration and old-record rendering;
- configuration/environment/CLI interactions.

**End-to-end tests**

- clean install in supported Python versions on macOS and Linux CI;
- `init → doctor → process → show → export` using synthetic transcripts;
- all required artifacts and consistent counts;
- offline execution makes no network request;
- remote mode is blocked unless explicitly enabled.

**Golden tests**

- committed synthetic transcripts and expected structured/differential outputs;
- semantic assertions for required entities and evidence, not brittle full prose matching;
- deterministic rendered Markdown/HTML snapshots.

**Security tests**

- transcript prompt injection attempts;
- HTML/script injection;
- path traversal and symlink attacks;
- oversized/malformed data;
- secrets in simulated provider errors;
- corrupt/partial state.

**Accessibility tests**

- automated HTML checks;
- keyboard-only dashboard walkthrough;
- screen-reader smoke test of snapshot, delta, table, and attention items.

### 19.2 Evaluation dataset

Create synthetic fixtures covering clear and ambiguous ownership, implied versus explicit commitments, due dates, unanswered/partially answered questions, changed decisions, blockers, renamed topics, not-discussed actions, false completion cues, duplicate phrasing, speaker ambiguity, absent timestamps, and transcript-injected instructions.

Annotate expected actions, owners, evidence lines, questions, decisions, and transitions. Add a local evaluation command that reports precision/recall for extractable categories and false-owner/false-completion rates. Never require proprietary or sensitive data to run tests.

### 19.3 Coverage policy

Set a meaningful project threshold (recommended: 85% line coverage initially) while requiring near-complete branch coverage for transition rules, atomic persistence, path safety, and secret redaction. Coverage does not replace behavior-focused tests.

---

## 20. CI/CD and Supply Chain

### 20.1 Pull-request CI

Run on supported macOS and Linux runners and supported Python versions:

1. packaging/build metadata validation;
2. formatting and lint checks;
3. static type checking;
4. unit and integration tests with coverage;
5. end-to-end smoke test from built wheel;
6. security/static analysis and dependency review;
7. docs link/build checks;
8. dashboard HTML/accessibility checks;
9. secret scanning.

CI uses fake providers and must not expose a maintainer API key to forked pull requests.

### 20.2 Release pipeline

- Trigger from a protected, signed version tag after approval.
- Build source distribution and universal Python wheel in a clean environment.
- Test installation from the built artifacts on macOS and Linux.
- Publish to a staging package index first, smoke test, then publish to the public index using trusted publishing where available.
- Attach artifacts, SHA-256 checksums, changelog, and compatibility notes to the GitHub release.
- Generate provenance/SBOM when supported by the release platform.
- Never publish automatically from an unreviewed pull request.

### 20.3 Dependency management

- Use automated dependency update pull requests with tests.
- Prefer maintained, narrowly scoped libraries.
- Declare optional provider dependencies as extras so offline/core installs stay small.
- Document the security-update process and supported release branches.

---

## 21. Public Packaging and Distribution

- Package/import name: `didwedoit` subject to registry availability; verify availability before publication.
- CLI command: `didwedoit`.
- Publish a PEP-compliant wheel and source distribution.
- Core install contains local workflow, schemas, history, rendering, and fake/manual provider support.
- Provider SDKs use optional extras, for example `didwedoit[openai]` or `didwedoit[local]`, only after adapter choices are finalized.
- The wheel includes templates, JSON schemas, and required static assets and works without the repository checkout.
- The package must not write outside an explicitly initialized workspace except standard read-only package caches or user-approved model runtime behavior.
- Provide `pipx` as the preferred isolated CLI installation route and `pip`/virtual environment instructions for contributors.
- Containers, Homebrew, and standalone binaries are post-MVP options, not launch blockers.

The public README must avoid implying that the package is an official product of any provider or transcript vendor.

---

## 22. Licensing and Legal Guidance

Recommended default: **Apache License 2.0** because it is permissive and includes an express patent grant. **MIT** is an acceptable simpler alternative if the maintainers prefer it. This is product guidance, not legal advice; the repository owner should obtain institutional/legal approval before public release, especially for university-owned work.

Before release:

- choose and commit exactly one `LICENSE` file;
- confirm the project name and package name do not conflict with existing trademarks/packages;
- audit all dependency licenses and generated/vendored assets for compatibility;
- add copyright notices consistent with institutional policy;
- document that users are responsible for meeting consent, transcript rights, retention policy, and provider terms;
- use only synthetic examples with clear licensing;
- add a third-party notices file if required;
- do not add a Contributor License Agreement unless governance/legal needs justify it; use Developer Certificate of Origin sign-off only if the maintainers can enforce and document it consistently.

---

## 23. Documentation Set

Required for the public MVP:

- `README.md`: value proposition, privacy warning, 5-minute quick start, example output, supported platforms, limitations.
- `docs/installation.md`: `pipx`, virtual environment, macOS/Linux prerequisites, troubleshooting.
- `docs/configuration.md`: every setting, precedence, privacy effects, provider setup, secret handling.
- `docs/user-guide.md`: first and recurring meeting workflows, backfill, rerun, export, workspace backup.
- `docs/output-reference.md`: files, schemas, statuses, confidence, evidence, and “not discussed.”
- `docs/architecture.md`: boundaries, pipeline, state/events, provider contract, diagrams.
- `docs/privacy-security.md`: local/remote data flow, threat model, retention, consent, reporting vulnerabilities.
- `docs/provider-development.md`: adapter interface, capability tests, data-handling documentation requirements.
- `docs/contributing.md`: setup, test commands, style, fixtures, PR process.
- `docs/troubleshooting.md`: error codes and recovery without exposing transcript data.
- `CHANGELOG.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, and contribution templates.

Documentation commands must be copy-paste tested on a clean macOS and Linux environment before release.

---

## 24. Contribution and Governance Model

- Use a public issue tracker with bug, feature, provider, security-routing, and documentation templates.
- Require a focused issue or design discussion for schema, storage, privacy, provider, and CLI-contract changes.
- Require at least one maintainer review and passing CI for protected branches.
- Use a pull-request template covering tests, docs, privacy/security impact, schema/migration impact, and screenshots for dashboard changes.
- Label good first issues that do not require sensitive fixtures or provider credentials.
- Apply a published code of conduct.
- Publish maintainer roles, decision process, and release authority before accepting major external contributions.
- Never ask contributors to upload real transcripts. Bug reports must use synthetic/minimized reproduction data.
- Keep experimental providers/features behind clearly documented feature flags or pre-1.0 APIs.

---

## 25. Versioning and Release Policy

Use Semantic Versioning.

- `0.x`: public API/schema may evolve, but changes are documented and migrations are supplied for persisted state.
- `1.0`: stable CLI command contract, provider interface, canonical schema/migration policy, and supported platform matrix.
- Patch release: compatible fixes, security patches, documentation.
- Minor release: backward-compatible features and schema additions with migrations.
- Major release: breaking CLI/API/schema changes.

Maintain a Keep a Changelog-style `CHANGELOG.md`. Deprecations emit actionable warnings for at least one minor release where practicable. Security releases identify affected and fixed versions without exposing users before a fix is available.

### 25.1 MVP release gates

No public `0.1.0` release until:

- all P0 acceptance criteria pass on macOS and Linux;
- threat-model controls and security tests pass;
- package installs from built artifacts in a clean environment;
- README quick start is independently verified;
- no real transcript or credential exists in repository history intended for publication;
- license, security policy, code of conduct, and contribution guide are present;
- dashboard accessibility smoke tests pass;
- a tagged release candidate processes at least two synthetic consecutive meetings and produces a correct differential.

---

## 26. Acceptance Criteria

### P0 — required for MVP

- **AC-001:** On clean supported macOS and Linux environments, a user installs the built package and `didwedoit --help` succeeds.
- **AC-002:** `init` creates the documented workspace and a second invocation does not overwrite user files.
- **AC-003:** A valid UTF-8 `.txt` transcript produces all eight required artifacts with a successful run manifest.
- **AC-004:** A non-`.txt`, empty, oversized, or invalid-encoding input fails before any provider call and leaves canonical state unchanged.
- **AC-005:** The first meeting reports a baseline with no previous meeting; the second meeting uses the correct prior meeting in the same series.
- **AC-006:** A prior action absent from the current transcript appears as `not discussed`, not completed.
- **AC-007:** A completed action is reported only with affirmative current evidence, and the evidence line range resolves to the original transcript.
- **AC-008:** Ambiguous owner language does not create a confirmed owner; output shows “Unassigned” or `needs_review`.
- **AC-009:** Low-confidence historical matches are not silently merged.
- **AC-010:** Counts and statuses match across canonical JSON, Markdown reports, and dashboard.
- **AC-011:** Dashboard opens from disk with networking disabled, contains no remote resources, and remains usable without JavaScript.
- **AC-012:** Transcript HTML/script content is escaped and cannot execute in the dashboard.
- **AC-013:** Path traversal, malicious series/title values, and unsafe output symlinks cannot write outside the workspace.
- **AC-014:** Simulated interruption before commit leaves the prior canonical state byte-identical and rerunnable.
- **AC-015:** Remote processing is blocked by default; when enabled, CLI clearly states that transcript content will be sent to the configured provider.
- **AC-016:** Logs, errors, manifests, and reports do not reveal configured credentials.
- **AC-017:** Offline/local mode completes without outbound network connections.
- **AC-018:** `export` regenerates required reports from state without a provider call.
- **AC-019:** CI passes from the built wheel on the supported OS/Python matrix with no live-provider dependency.
- **AC-020:** The README quick start takes a new user from installation to opening the sample dashboard without undocumented steps.

### P1 — should follow shortly after MVP

- Human review/correction workflow that records audit events.
- Comparison with an explicitly selected historical meeting.
- Search and filtering across a series.
- Import/export backup bundle and integrity verification.
- Additional local and remote provider adapters.
- Optional SQLite storage migration after profiling justifies it.

---

## 27. Phased Roadmap

### Phase 0 — Discovery and contracts

- Confirm name/package availability and license approval.
- Create synthetic annotated transcripts and expected differential cases.
- Finalize canonical schemas, status-transition policy, provider interface, and privacy defaults.
- Prototype extraction against at least one local and one optional remote provider without committing provider-specific domain design.

**Exit:** Schemas, fixtures, architecture decision records, and evaluation measures are reviewed.

### Phase 1 — Deterministic core

- Package/CLI skeleton, typed config, initialization, ingestion, normalization, line evidence, repository, event model, projection, and deterministic report shell.
- Fake provider and full test harness.

**Exit:** Two hand-authored structured meetings generate stable history, differential, Markdown, and HTML with no network.

### Phase 2 — Automated intelligence

- Provider abstraction and first production adapter(s).
- Chunked extraction, validation/repair, consolidation, matching, confidence/review behavior.
- Evaluation command and threshold reporting.

**Exit:** Synthetic evaluation meets false-owner and false-completion gates; failure paths preserve state.

### Phase 3 — Public MVP hardening

- Security controls, accessible dashboard, error recovery, migrations, documentation, packaging, CI/CD, release candidate.
- Pilot with consented, non-public team data; only aggregate, content-free quality notes may enter project issues.

**Exit:** All P0 acceptance criteria and release gates pass; publish `0.1.0`.

### Phase 4 — Review and team utility

- Human correction/audit UI or CLI, richer history search, selected comparisons, backup bundle, more adapters.

### Phase 5 — Optional ecosystem

- Task/calendar integrations, additional input formats, hosted collaboration, or transcription only through separate privacy/security/product specifications.

---

## 28. Decisions Deferred Beyond This Specification

The implementer may make reversible choices for CLI, templates, and testing libraries. The following require an architecture decision record before implementation changes scope:

- final project/package name;
- exact local model runtime and first remote provider;
- JSON-files-to-SQLite migration;
- human review/correction interaction design;
- adding any networked dashboard, hosted storage, or telemetry;
- supporting formats other than `.txt`;
- changing automatic historical merge thresholds or completion policy.

---

## 29. Explicit Codex Implementation Instructions

Use this section as the execution directive when this file is supplied to Codex.

### 29.1 Mission

Implement the public-ready MVP described in this specification. Treat this document as the product contract. Preserve macOS/Linux compatibility, TXT-only meeting input, local-first operation, automated structured outputs, the manager dashboard, and previous-versus-current differential as non-negotiable core requirements.

### 29.2 Working rules

1. Inspect the repository, `AGENTS.md`, existing code, tests, and configuration before editing.
2. Do not overwrite unrelated user changes or commit secrets, real transcripts, generated private outputs, caches, or local state.
3. If the repository is empty, create the structure in Section 10.4. If it already has compatible structure, adapt it rather than reorganizing gratuitously.
4. Maintain a short implementation plan mapped to requirement and acceptance-criterion IDs; update it as work completes.
5. Make the smallest coherent implementation that satisfies the current phase. Do not add SaaS, audio ingestion, accounts, or integrations.
6. Establish domain schemas, repository interfaces, status-transition rules, evidence line mapping, and fake provider before connecting a production model provider.
7. Keep provider SDKs behind adapters and optional dependencies. Core and CI must work without network access or credentials.
8. Treat transcript text and provider output as untrusted. Implement escaping, path containment, schema validation, redaction, and atomic persistence before declaring the pipeline complete.
9. Never infer ownership or completion without evidence. Preserve `not_discussed` as a differential observation.
10. Generate human-facing outputs only from validated canonical state.
11. Add tests with every behavior. Prefer synthetic fixtures and fake/replay provider responses over mocks that bypass validation.
12. Run formatting, linting, type checks, unit/integration/end-to-end tests, package build, and installation smoke test before handoff.
13. Verify the dashboard visually and functionally from a local file with networking disabled; check keyboard navigation and escaped content.
14. Update README, reference docs, changelog, and example outputs as part of the implementation—not as a later cleanup.
15. Do not publish a package, push a release, enable paid provider calls, or modify external services unless the user explicitly authorizes it.

### 29.3 Required implementation order

1. **Repository audit and decisions:** report existing state, conflicts, proposed stack, and any decisions that cannot be inferred safely.
2. **Contracts:** implement strict models, exported JSON schemas, config, transition table, provider/repository interfaces, and version constants.
3. **Safe ingestion:** implement `.txt` validation, metadata, normalization, line mapping, checksums, limits, and path safety.
4. **Deterministic state:** implement series, stable IDs, append-only events, projections, atomic commits, locks, migrations, and backfill behavior.
5. **Fake-provider vertical slice:** implement `init`, `doctor`, `process`, artifacts, baseline/second-meeting differential, and `export` end to end.
6. **Provider automation:** implement configured production adapter(s), chunking, schema-constrained extraction, bounded repair, consolidation, and redacted errors.
7. **Reconciliation:** implement candidate retrieval, evidence-backed transitions, thresholds, ambiguity/review flags, and management-attention logic.
8. **Dashboard and accessibility:** implement self-contained HTML, equivalent text/tables, responsive styles, no remote assets, and accessibility tests.
9. **Public hardening:** complete security tests, docs, packaging, CI, contribution/legal files, performance checks, and release-candidate validation.

### 29.4 Progress and handoff format

At each milestone, report:

- requirement/acceptance IDs completed;
- files materially changed;
- tests/checks run and results;
- known limitations or deferred decisions;
- the next smallest coherent milestone.

At final handoff, provide:

- a concise outcome summary;
- installation and sample commands actually verified;
- absolute or repository-relative paths to the dashboard and example outputs;
- full validation results, including any skipped checks and why;
- security/privacy behavior of the selected provider configuration;
- any remaining P0 gap. Do not claim completion while a P0 gap remains.

### 29.5 Definition of done

Implementation is done only when all P0 acceptance criteria pass, required public documentation exists, package artifacts install cleanly on macOS and Linux, the two-meeting synthetic scenario produces a correct evidence-backed differential, and failure/interruption tests prove canonical state is not corrupted.

---

## 30. Final Product Positioning

**Short description:**

> DidWeDoIt turns plain-text meeting transcripts into private, evidence-backed summaries, actions, open questions, manager dashboards, and a clear account of what changed since the last meeting.

**Public-launch promise:**

> Bring a transcript. Keep control of the data. See what the team decided, who committed to what, and whether anything actually moved forward.
