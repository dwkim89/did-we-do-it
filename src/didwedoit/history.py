from __future__ import annotations

import json
import os
import re
from difflib import SequenceMatcher
from pathlib import Path

from .models import Confidence, DeltaItem, MeetingDifferential, MeetingRecord, ReviewBundle


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("Series must contain at least one letter or number")
    return slug[:80]


def workspace_paths(workspace: Path) -> dict[str, Path]:
    root = workspace.expanduser().resolve()
    return {
        "root": root,
        "meetings": root / "meetings",
        "reviews": root / "reviews",
        "state": root / "state",
    }


def initialize_workspace(workspace: Path) -> dict[str, Path]:
    paths = workspace_paths(workspace)
    for name in ("meetings", "reviews", "state"):
        paths[name].mkdir(parents=True, exist_ok=True)
    config = paths["root"] / "didwedoit.toml"
    if not config.exists():
        config.write_text(
            "config_version = 1\n\n[analysis]\nprovider = \"cborg\"\n"
            "model = \"cborg-deepthought\"\nchunk_chars = 40000\ncontext_tokens = 16384\n\n"
            "[cborg]\ntimeout_seconds = 300\n\n"
            "[ollama]\nurl = \"http://127.0.0.1:11434\"\ntimeout_seconds = 300\n\n"
            "[privacy]\nretain_transcript_copy = false\n",
            encoding="utf-8",
        )
    return paths


def _atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("x", encoding="utf-8") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def meeting_records(workspace: Path, series: str | None = None) -> list[MeetingRecord]:
    base = workspace_paths(workspace)["meetings"]
    roots = [base / safe_slug(series)] if series else ([path for path in base.iterdir() if path.is_dir()] if base.exists() else [])
    records: list[MeetingRecord] = []
    for root in roots:
        for path in root.glob("*/meeting.json"):
            try:
                records.append(MeetingRecord.model_validate_json(path.read_text(encoding="utf-8")))
            except (ValueError, OSError):
                continue
    return sorted(records, key=lambda record: (record.date, record.id))


def previous_record(workspace: Path, record: MeetingRecord) -> MeetingRecord | None:
    earlier = [item for item in meeting_records(workspace, record.series) if item.date < record.date]
    return earlier[-1] if earlier else None


def previous_review_record(workspace: Path, record: MeetingRecord) -> MeetingRecord | None:
    candidates: list[MeetingRecord] = []
    for path in workspace_paths(workspace)["reviews"].glob("*.json"):
        try:
            item = load_review(path).meeting
        except (ValueError, OSError):
            continue
        if (item.series == record.series and item.extractor == record.extractor and item.date < record.date
                and item.source.checksum_sha256 != record.source.checksum_sha256):
            candidates.append(item)
    return sorted(candidates, key=lambda item: (item.date, item.created_at))[-1] if candidates else None


def _normalized(value: str) -> str:
    return re.sub(r"\W+", " ", value.lower()).strip()


def _next_ids(workspace: Path, series: str) -> dict[str, int]:
    counters = {"AI": 1, "Q": 1, "D": 1, "B": 1}
    pattern = re.compile(r"^(AI|Q|D|B)-(\d+)$")
    for meeting in meeting_records(workspace, series):
        for collection in (meeting.actions, meeting.questions, meeting.decisions, meeting.blockers):
            for item in collection:
                if item.id and (match := pattern.match(item.id)):
                    counters[match.group(1)] = max(counters[match.group(1)], int(match.group(2)) + 1)
    return counters


def _best_match(text: str, prior_items: list, attribute: str, used: set[str]):
    ranked = sorted(
        (
            (SequenceMatcher(None, _normalized(text), _normalized(getattr(old, attribute))).ratio(), old)
            for old in prior_items if old.id and old.id not in used
        ),
        key=lambda pair: pair[0], reverse=True,
    )
    return ranked[0] if ranked else None


def _build_differential(record: MeetingRecord, prior: MeetingRecord | None) -> MeetingDifferential:
    changes: list[DeltaItem] = []
    if prior is None:
        for entity_type, items, attribute in (
            ("action", record.actions, "description"), ("question", record.questions, "text"),
            ("decision", record.decisions, "description"), ("blocker", record.blockers, "description"),
            ("diagnosis", record.diagnoses, "finding"),
        ):
            changes.extend(DeltaItem(
                kind="baseline", entity_type=entity_type, description=getattr(item, attribute),
                reason="First recorded meeting in this series.", current_id=item.id,
                confidence=item.confidence,
            ) for item in items)
    else:
        for action in record.actions:
            if action.relation == "completed" or action.status == "completed":
                kind, reason = "completed", "The current meeting explicitly marks the action completed."
            elif action.status == "blocked" or action.relation == "blocked":
                kind, reason = "blocked", "The current meeting marks the action blocked."
            elif action.status == "in_progress" or action.relation == "progressed":
                kind, reason = "progressed", "The current meeting reports work in progress."
            elif action.prior_id:
                kind, reason = "still_open", "The action matches a prior action and remains open."
            else:
                kind, reason = "new", "No sufficiently similar prior action was linked."
            changes.append(DeltaItem(kind=kind, entity_type="action", description=action.description,
                                     reason=reason, prior_id=action.prior_id, current_id=action.id,
                                     confidence=action.confidence))
        prior_actions = {item.id: item for item in prior.actions if item.id}
        for item_id in record.not_discussed_action_ids:
            old = prior_actions.get(item_id)
            if old:
                changes.append(DeltaItem(
                    kind="not_discussed", entity_type="action", description=old.description,
                    reason="The prior open action was not linked to current-meeting evidence.",
                    prior_id=item_id, confidence=Confidence.HIGH,
                ))
        for question in record.questions:
            if question.status == "answered" and question.id and question.id.startswith("Q-"):
                kind, reason = "resolved", "The current meeting records an answer."
            elif question.id and any(old.id == question.id for old in prior.questions):
                kind, reason = "still_open", "The question recurs without a confirmed resolution."
            else:
                kind, reason = "new", "No sufficiently similar prior question was linked."
            changes.append(DeltaItem(kind=kind, entity_type="question", description=question.text,
                                     reason=reason, current_id=question.id, confidence=question.confidence))
        for decision in record.decisions:
            changes.append(DeltaItem(kind="new", entity_type="decision", description=decision.description,
                                     reason="A decision was recorded in the current meeting.",
                                     current_id=decision.id, confidence=decision.confidence))
        for blocker in record.blockers:
            linked = blocker.id and any(old.id == blocker.id for old in prior.blockers)
            changes.append(DeltaItem(kind="still_open" if linked else "blocked", entity_type="blocker",
                                     description=blocker.description,
                                     reason="The blocker persists." if linked else "A new blocker was recorded.",
                                     current_id=blocker.id, confidence=blocker.confidence))
        for diagnosis in record.diagnoses:
            changes.append(DeltaItem(kind="new", entity_type="diagnosis", description=diagnosis.finding,
                                     reason=diagnosis.reason, confidence=diagnosis.confidence))

    attention = []
    attention.extend(f"Missing owner: {item.description}" for item in record.actions if item.owner is None)
    attention.extend(f"Blocked: {item.description}" for item in record.blockers)
    attention.extend(f"Unanswered: {item.text}" for item in record.questions
                     if item.status in {"unanswered", "unknown", "partially_answered"})
    attention.extend(f"{item.severity.title()} {item.category}: {item.finding}" for item in record.diagnoses
                     if item.severity in {"high", "critical"})
    return MeetingDifferential(previous_meeting_id=prior.id if prior else None, baseline=prior is None,
                               changes=changes, attention=list(dict.fromkeys(attention))[:20])


def reconcile(workspace: Path, record: MeetingRecord, prior_override: MeetingRecord | None = None,
              assign_ids: bool = True) -> MeetingRecord:
    prior = prior_override or previous_record(workspace, record)
    record.previous_meeting_id = prior.id if prior else None
    counters = _next_ids(workspace, record.series)
    linked: set[str] = set()

    if prior:
        for action in record.actions:
            if action.prior_id and not action.needs_review:
                action.id = action.prior_id
                action.relation = "completed" if action.status == "completed" else "same"
                linked.add(action.prior_id)
                continue
            ranked = sorted(
                ((SequenceMatcher(None, _normalized(action.description), _normalized(old.description)).ratio(), old)
                 for old in prior.actions if old.id),
                key=lambda pair: pair[0],
                reverse=True,
            )
            if ranked and ranked[0][0] >= 0.88:
                old = ranked[0][1]
                action.id = old.id
                action.prior_id = old.id
                action.relation = "completed" if action.status == "completed" else "same"
                linked.add(old.id or "")
            elif ranked and ranked[0][0] >= 0.64:
                old = ranked[0][1]
                action.prior_id = old.id
                action.needs_review = True
                action.review_reason = (
                    f"This may refer to {old.id}, but the wording changed; confirm whether they are the same action."
                )

        record.not_discussed_action_ids = [
            action.id for action in prior.actions
            if action.id and action.id not in linked and action.status not in {"completed", "cancelled"}
        ]

        for current_items, prior_items, attribute in (
            (record.questions, prior.questions, "text"),
            (record.decisions, prior.decisions, "description"),
            (record.blockers, prior.blockers, "description"),
        ):
            used: set[str] = set()
            for item in current_items:
                match = _best_match(getattr(item, attribute), prior_items, attribute, used)
                if match and match[0] >= 0.88 and not item.needs_review:
                    item.id = match[1].id
                    used.add(match[1].id)
                elif match and match[0] >= 0.64:
                    item.needs_review = True
                    item.review_reason = item.review_reason or (
                        f"This may refer to {match[1].id}; confirm the cross-meeting link."
                    )

    for prefix, collection in (
        ("AI", record.actions), ("Q", record.questions), ("D", record.decisions), ("B", record.blockers)
    ):
        for item in collection:
            if assign_ids and item.id is None and not item.needs_review:
                item.id = f"{prefix}-{counters[prefix]:04d}"
                counters[prefix] += 1
    record.differential = _build_differential(record, prior)
    record.differential.provisional = prior_override is not None
    return record


def write_review(workspace: Path, record: MeetingRecord, warnings: list[str] | None = None) -> Path:
    paths = initialize_workspace(workspace)
    extractor = safe_slug(record.extractor)[:48]
    path = paths["reviews"] / f"{record.date.isoformat()}_{record.source.checksum_sha256[:8]}_{extractor}.json"
    bundle = ReviewBundle(meeting=record, warnings=warnings or [])
    _atomic_text(path, bundle.model_dump_json(indent=2))
    return path


def write_review_preview(review_path: Path, content: str) -> Path:
    preview = review_path.with_suffix(".html")
    _atomic_text(preview, content)
    return preview


def load_review(path: Path) -> ReviewBundle:
    return ReviewBundle.model_validate_json(path.read_text(encoding="utf-8"))


def commit_record(workspace: Path, record: MeetingRecord, report_md: str, dashboard_html: str) -> Path:
    if record.pending_review_count:
        raise ValueError(f"Cannot commit: {record.pending_review_count} items still need review")
    paths = initialize_workspace(workspace)
    meetings_root = paths["meetings"].resolve()
    series_root = meetings_root / safe_slug(record.series)
    series_root.mkdir(parents=True, exist_ok=True)
    if series_root.resolve().parent != meetings_root:
        raise ValueError("Unsafe series output path or symlink")
    directory = series_root / f"{record.date.isoformat()}_{record.id}"
    if directory.exists():
        if directory.is_symlink():
            raise ValueError("Refusing to write through an output symlink")
        return directory
    staging = series_root / f".{directory.name}.{os.getpid()}.staging"
    if staging.exists() or staging.is_symlink():
        raise ValueError(f"Staging path already exists: {staging}")
    staging.mkdir()
    _atomic_text(staging / "meeting.json", record.model_dump_json(indent=2))
    _atomic_text(staging / "report.md", report_md)
    _atomic_text(staging / "dashboard.html", dashboard_html)
    staging.replace(directory)
    return directory
