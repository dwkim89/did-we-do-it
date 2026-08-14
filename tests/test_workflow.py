from pathlib import Path

from didwedoit.history import commit_record, meeting_records, reconcile
from didwedoit.ingest import load_transcript
from didwedoit.models import ReviewBundle
from didwedoit.providers import HeuristicProvider
from didwedoit.render import render_html, render_markdown, render_summary_markdown


def _write(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


FIRST = """09:00:00 --> 09:00:05
Alice: Welcome to today's detector meeting.

09:00:06 --> 09:00:12
Bob: Why does the forward region disagree with simulation?

09:00:13 --> 09:00:20
Alice: The input coordinate may be shifted in the data sample.

09:00:21 --> 09:00:28
Bob: I will produce the comparison plot after applying the selection.
"""

SECOND = """09:00:00 --> 09:00:05
Alice: Welcome to today's detector meeting.

09:00:06 --> 09:00:12
Alice: We need to understand the new calibration discrepancy.
"""


def test_review_gate_and_not_discussed_history(tmp_path: Path):
    first_path = _write(tmp_path / "20260805_first.txt", FIRST)
    first = HeuristicProvider().analyze(load_transcript(first_path), "detector")
    assert first.pending_review_count >= 1
    for collection in (first.questions, first.actions, first.decisions, first.blockers):
        for item in collection:
            item.needs_review = False
            item.review_reason = None
    first = reconcile(tmp_path, first)
    out = commit_record(tmp_path, first, render_markdown(first), render_html(first))
    assert (out / "meeting.json").exists()
    assert "<script" not in (out / "dashboard.html").read_text(encoding="utf-8")
    assert first.differential.baseline is True

    second_path = _write(tmp_path / "20260807_second.txt", SECOND)
    second = HeuristicProvider().analyze(load_transcript(second_path), "detector")
    for collection in (second.questions, second.actions, second.decisions, second.blockers):
        for item in collection:
            item.needs_review = False
            item.review_reason = None
    second = reconcile(tmp_path, second)
    assert second.previous_meeting_id == first.id
    assert first.actions[0].id in second.not_discussed_action_ids
    assert any(item.kind == "not_discussed" for item in second.differential.changes)
    assert "Meeting-to-meeting differential" in render_html(second)


def test_html_escapes_transcript_content(tmp_path: Path):
    path = _write(
        tmp_path / "20260808_injection.txt",
        "09:00:00 --> 09:00:05\nAlice: I will investigate <script>alert(1)</script> tomorrow.\n",
    )
    record = HeuristicProvider().analyze(load_transcript(path), "security")
    rendered = render_html(record)
    assert "<script>alert" not in rendered
    assert "&lt;script&gt;" in rendered


def test_summary_markdown_has_stable_slide_input_sections(tmp_path: Path):
    path = _write(tmp_path / "20260805_summary.txt", FIRST)
    record = HeuristicProvider().analyze(load_transcript(path), "detector")
    rendered = render_summary_markdown(record)
    headings = [
        "## Key outcomes", "## Decisions made", "## Open Questions",
        "## Pending Confirmation", "## Action items",
    ]
    positions = [rendered.index(heading) for heading in headings]
    assert positions == sorted(positions)
    assert "date: 2026-08-05" in rendered
    assert "source_sha256:" in rendered
