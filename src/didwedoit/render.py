from __future__ import annotations

import html
from collections import Counter

from .models import MeetingRecord, ReviewBundle


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_markdown(record: MeetingRecord) -> str:
    lines = [
        f"# {record.title}", "", f"- Date: {record.date.isoformat()}", f"- Series: {record.series}",
        f"- Meeting ID: {record.id}", f"- Previous meeting: {record.previous_meeting_id or 'None'}", "",
        "## Executive Summary", "", record.executive_summary, "", "## Topics", "",
    ]
    lines.extend(f"- {_md(topic)}" for topic in record.topics)
    lines.extend(["", "## Project Diagnosis", ""])
    if record.diagnoses:
        for item in record.diagnoses:
            lines.append(f"- **{item.severity.upper()} · {item.category}:** {_md(item.finding)}")
            lines.append(f"  - Reason: {_md(item.reason)}")
    else:
        lines.append("No evidence-backed diagnosis identified.")
    lines.extend(["", "## Changes Since Previous Meeting", ""])
    if record.differential.baseline:
        lines.append("Baseline meeting: no earlier approved meeting exists in this series.")
    for item in record.differential.changes:
        lines.append(f"- **{item.kind} · {item.entity_type}:** {_md(item.description)}")
        lines.append(f"  - Why: {_md(item.reason)}")
    lines.extend(["", "## Management Attention", ""])
    lines.extend(f"- {_md(item)}" for item in record.differential.attention)
    if not record.differential.attention:
        lines.append("None identified.")

    sections = (
        ("Action Items", record.actions, "description"), ("Questions", record.questions, "text"),
        ("Decisions", record.decisions, "description"), ("Blockers", record.blockers, "description"),
    )
    for heading, items, field in sections:
        lines.extend(["", f"## {heading}", ""])
        if not items:
            lines.append("None identified.")
            continue
        for item in items:
            evidence = item.evidence[0]
            lines.append(f"- **{item.id or 'REVIEW'}:** {_md(getattr(item, field))} — lines {evidence.line_start}–{evidence.line_end}")
            if hasattr(item, "owner"):
                lines.append(f"  - Owner: {getattr(item, 'owner') or 'Unassigned'}")
            if item.needs_review:
                lines.append(f"  - Needs review: {_md(item.review_reason or 'Uncertain extraction')}")
    lines.extend(["", "## Provenance", "", f"- Input SHA-256: `{record.source.checksum_sha256}`",
                  f"- Extractor: `{record.extractor}`", ""])
    return "\n".join(lines)


def render_summary_markdown(record: MeetingRecord) -> str:
    """Render the editable meeting artifact consumed by the Beamer workflow."""
    lines = [
        "---", f"date: {record.date.isoformat()}", f"series: {record.series}",
        f"meeting_id: {record.id}", f"source: {record.source.path}",
        f"source_sha256: {record.source.checksum_sha256}", f"extractor: {record.extractor}",
        "status: draft", "---", "", f"# Meeting Summary — {record.date.isoformat()}", "",
        "## Key outcomes", "", f"- {_md(record.executive_summary)}",
    ]
    for diagnosis in record.diagnoses:
        if diagnosis.category == "progress" and not diagnosis.needs_review:
            lines.append(f"- {_md(diagnosis.finding)} — {_md(diagnosis.reason)}")

    progress_by_speaker: dict[str, list[str]] = {}
    for diagnosis in record.diagnoses:
        if diagnosis.category != "progress" or diagnosis.needs_review:
            continue
        speaker = diagnosis.evidence[0].speaker or "Unattributed"
        progress_by_speaker.setdefault(speaker, []).append(diagnosis.finding)
    if progress_by_speaker:
        lines.extend(["", "## Progress by contributor", ""])
        for speaker, findings in progress_by_speaker.items():
            lines.append(f"### {_md(speaker)}")
            lines.extend(f"- {_md(finding)}" for finding in findings)
            lines.append("")

    lines.extend(["", "## Decisions made", ""])
    decisions = [item for item in record.decisions if not item.needs_review]
    if decisions:
        for item in decisions:
            evidence = item.evidence[0]
            lines.append(f"- {_md(item.description)} _(lines {evidence.line_start}–{evidence.line_end})_")
    else:
        lines.append("- None confirmed.")

    lines.extend(["", "## Open Questions", ""])
    questions = [item for item in record.questions
                 if not item.needs_review and item.status in {"unanswered", "partially_answered", "unknown"}]
    if questions:
        for item in questions:
            evidence = item.evidence[0]
            answer = f" Current understanding: {_md(item.answer)}" if item.answer else ""
            lines.append(f"- {_md(item.text)}{answer} _(lines {evidence.line_start}–{evidence.line_end})_")
    else:
        lines.append("- None confirmed.")

    lines.extend(["", "## Pending Confirmation", ""])
    pending = []
    for label, items, attribute in (
        ("Question", record.questions, "text"), ("Decision", record.decisions, "description"),
        ("Action", record.actions, "description"), ("Blocker", record.blockers, "description"),
        ("Finding", record.diagnoses, "finding"),
    ):
        for item in items:
            if item.needs_review:
                evidence = item.evidence[0]
                pending.append(
                    f"- [ ] **{label}:** {_md(getattr(item, attribute))} "
                    f"_(lines {evidence.line_start}–{evidence.line_end}; "
                    f"{_md(item.review_reason or 'model interpretation needs confirmation')})_"
                )
    lines.extend(pending or ["- None."])

    lines.extend(["", "## Action items", ""])
    actions = [item for item in record.actions if not item.needs_review]
    if actions:
        for item in actions:
            evidence = item.evidence[0]
            lines.append(
                f"- [ ] **{_md(item.owner or 'Unassigned')}** — {_md(item.description)} "
                f"_(status: {item.status}; lines {evidence.line_start}–{evidence.line_end})_"
            )
    else:
        lines.append("- None confirmed.")

    findings = [item for item in record.diagnoses if not item.needs_review and item.category != "progress"]
    blockers = [item for item in record.blockers if not item.needs_review]
    if findings or blockers:
        lines.extend(["", "## Risks, blockers, and reasoning", ""])
        for item in findings:
            lines.append(f"- **{item.severity.title()} {item.category.replace('_', ' ')}:** {_md(item.finding)} — {_md(item.reason)}")
        for item in blockers:
            lines.append(f"- **Blocker:** {_md(item.description)}")

    lines.extend(["", "## Topics discussed", ""])
    lines.extend(f"- {_md(topic)}" for topic in record.topics)
    lines.extend(["", "<!-- Edit this Markdown before using it as slide input. -->", ""])
    return "\n".join(lines)


def _e(value) -> str:
    return html.escape(str(value))


def _badge(value: str, extra: str = "") -> str:
    return f'<span class="badge {extra}">{_e(value.replace("_", " "))}</span>'


def _review_marker(item) -> str:
    if not item.needs_review:
        return _badge("evidence checked", "ok")
    return _badge("needs review", "warn")


def _evidence(item) -> str:
    evidence = item.evidence[0]
    speaker = f" · {_e(evidence.speaker)}" if evidence.speaker else ""
    excerpt = f'<blockquote>{_e(evidence.excerpt)}</blockquote>' if evidence.excerpt else ""
    return f'<small>Transcript lines {evidence.line_start}–{evidence.line_end}{speaker}</small>{excerpt}'


def _item_cards(items, attribute: str, detail=None) -> str:
    if not items:
        return '<p class="empty">None identified.</p>'
    rows = []
    for item in items:
        details = detail(item) if detail else ""
        rows.append(
            f'<article class="item"><div class="item-head"><b>{_e(item.id or "Candidate")}</b>'
            f'<span>{_review_marker(item)} {_badge(item.confidence.value)}</span></div>'
            f'<p>{_e(getattr(item, attribute))}</p>{details}{_evidence(item)}'
            + (f'<p class="reason"><b>Review reason:</b> {_e(item.review_reason)}</p>' if item.needs_review else "")
            + '</article>'
        )
    return "".join(rows)


def render_html(record: MeetingRecord, review_mode: bool = False, warnings: list[str] | None = None) -> str:
    counts = Counter(item.kind for item in record.differential.changes)
    delta_metrics = "".join(
        f'<div class="metric"><b>{count}</b>{_e(kind.replace("_", " "))}</div>'
        for kind, count in sorted(counts.items())
    ) or '<div class="metric"><b>0</b>changes</div>'
    delta_rows = "".join(
        f'<tr><td>{_badge(item.kind, "delta")}</td><td>{_e(item.entity_type)}</td>'
        f'<td>{_e(item.description)}</td><td>{_e(item.reason)}</td></tr>'
        for item in record.differential.changes
    ) or '<tr><td colspan="4">No differential items.</td></tr>'
    attention = "".join(f'<li>{_e(item)}</li>' for item in record.differential.attention) or '<li>None identified.</li>'
    topics = " ".join(_badge(topic) for topic in record.topics)
    diagnoses = _item_cards(record.diagnoses, "finding", lambda item: (
        f'<p><b>{_e(item.severity.title())} {_e(item.category.replace("_", " "))}</b></p>'
        f'<p class="reason"><b>Reason:</b> {_e(item.reason)}</p>'
    ))
    actions = _item_cards(record.actions, "description", lambda item: (
        f'<dl><dt>Owner</dt><dd>{_e(item.owner or "Unassigned")}</dd>'
        f'<dt>Status</dt><dd>{_e(item.status)}</dd><dt>Meeting relation</dt><dd>{_e(item.relation)}</dd></dl>'
    ))
    questions = _item_cards(record.questions, "text", lambda item: (
        f'<dl><dt>Status</dt><dd>{_e(item.status)}</dd><dt>Answer</dt><dd>{_e(item.answer or "Not established")}</dd></dl>'
    ))
    decisions = _item_cards(record.decisions, "description")
    blockers = _item_cards(record.blockers, "description", lambda item: (
        f'<dl><dt>Owner</dt><dd>{_e(item.owner or "Unassigned")}</dd></dl>'
    ))
    warning_html = "".join(f'<li>{_e(item)}</li>' for item in (warnings or []))
    review_banner = (
        f'<div class="banner"><b>Review preview</b> · {record.pending_review_count} ambiguous items must be resolved '
        'before this meeting changes canonical project history. This HTML is read-only; use the review command to approve, edit, or discard candidates.</div>'
        if review_mode else '<div class="banner ok-banner"><b>Approved project record</b></div>'
    )
    baseline = "Baseline—no previous approved meeting." if record.differential.baseline else f"Compared with {_e(record.differential.previous_meeting_id)}"
    if record.differential.provisional:
        baseline += " · Provisional comparison against an unapproved prior review."
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_e(record.title)} · project progress</title><style>
:root {{ color-scheme:light dark; font-family:Inter,ui-sans-serif,system-ui,sans-serif; line-height:1.5; --line:#71809655; --panel:#71809612; --accent:#4f46e5; --warn:#b45309; --ok:#15803d }}
* {{ box-sizing:border-box }} body {{ max-width:1200px; margin:auto; padding:2rem; background:Canvas; color:CanvasText }}
h1 {{ margin-bottom:.2rem }} h2 {{ margin-top:0 }} .subtle,small {{ opacity:.72 }}
.banner {{ border-left:5px solid var(--warn); background:#f59e0b18; padding:1rem; border-radius:.5rem; margin:1rem 0 }} .ok-banner {{ border-color:var(--ok); background:#22c55e16 }}
.metrics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(125px,1fr)); gap:.75rem; margin:1rem 0 }}
.metric,section,.item {{ border:1px solid var(--line); background:var(--panel); border-radius:.8rem; padding:1rem }}
.metric b {{ display:block; font-size:1.8rem }} section {{ margin:1rem 0 }}
.badge {{ display:inline-block; border:1px solid var(--line); border-radius:999px; padding:.15rem .55rem; font-size:.78rem; margin:.12rem }}
.warn {{ color:var(--warn); border-color:var(--warn) }} .ok {{ color:var(--ok); border-color:var(--ok) }} .delta {{ color:var(--accent); border-color:var(--accent) }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:.75rem }} .item {{ margin:.65rem 0 }}
.item-head {{ display:flex; justify-content:space-between; gap:1rem }} dl {{ display:grid; grid-template-columns:max-content 1fr; gap:.2rem .8rem }} dt {{ font-weight:700 }} dd {{ margin:0 }}
blockquote {{ border-left:3px solid var(--line); margin:.5rem 0; padding-left:.8rem }} .reason {{ opacity:.85 }}
table {{ width:100%; border-collapse:collapse }} th,td {{ text-align:left; vertical-align:top; border-bottom:1px solid var(--line); padding:.6rem }}
@media(max-width:700px) {{ body {{ padding:1rem }} table {{ display:block; overflow:auto }} }}
</style></head><body><main>
{review_banner}
<header><h1>{_e(record.title)}</h1><p class="subtle">{record.date.isoformat()} · {_e(record.series)} · {_e(record.id)}</p></header>
<div class="metrics"><div class="metric"><b>{len(record.actions)}</b>to-do items</div><div class="metric"><b>{len(record.questions)}</b>questions</div><div class="metric"><b>{len(record.blockers)}</b>blockers</div><div class="metric"><b>{record.pending_review_count}</b>need review</div></div>
<section><h2>Executive summary</h2><p>{_e(record.executive_summary)}</p><div>{topics}</div></section>
<section><h2>Project diagnosis and reasons</h2><div class="grid">{diagnoses}</div></section>
<section><h2>Meeting-to-meeting differential</h2><p class="subtle">{baseline}</p><div class="metrics">{delta_metrics}</div>
<table><thead><tr><th>Change</th><th>Type</th><th>Item</th><th>Reason</th></tr></thead><tbody>{delta_rows}</tbody></table></section>
<section><h2>Management attention</h2><ul>{attention}</ul></section>
<section><h2>To-do list</h2>{actions}</section>
<section><h2>Questions</h2>{questions}</section>
<section><h2>Decisions</h2>{decisions}</section>
<section><h2>Blockers</h2>{blockers}</section>
{f'<section><h2>Warnings</h2><ul>{warning_html}</ul></section>' if warning_html else ''}
<footer class="subtle"><p>Source: {_e(record.source.path)} · SHA-256 {_e(record.source.checksum_sha256)} · Extractor {_e(record.extractor)}</p></footer>
</main></body></html>"""


def render_review_html(bundle: ReviewBundle) -> str:
    return render_html(bundle.meeting, review_mode=True, warnings=bundle.warnings)
