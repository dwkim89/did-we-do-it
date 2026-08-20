from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .config import load_settings
from .history import (commit_record, initialize_workspace, load_review, meeting_records, previous_record,
                      previous_review_record, reconcile, safe_slug, workspace_paths, write_review,
                      write_review_preview)
from .ingest import InputError, load_transcript
from .models import ActionItem, Question, ReviewBundle
from .providers import CborgProvider, HeuristicProvider, OllamaProvider, ProviderError
from .render import render_html, render_markdown, render_review_html, render_summary_markdown


def _collections(record):
    return (
        ("question", record.questions, "text"),
        ("action", record.actions, "description"),
        ("decision", record.decisions, "description"),
        ("blocker", record.blockers, "description"),
        ("diagnosis", record.diagnoses, "finding"),
    )


def interactive_review(bundle: ReviewBundle) -> ReviewBundle:
    print(f"\n{bundle.meeting.pending_review_count} items need review.")
    for kind, items, field in _collections(bundle.meeting):
        kept = []
        for item in items:
            if not item.needs_review:
                kept.append(item)
                continue
            evidence = item.evidence[0]
            print(f"\n[{kind}] {getattr(item, field)}")
            print(f"Evidence: lines {evidence.line_start}-{evidence.line_end}, {evidence.speaker}: {evidence.excerpt}")
            print(f"Reason: {item.review_reason}")
            while True:
                choice = input("Approve, edit, or discard? [a/e/d]: ").strip().lower()
                if choice in {"a", "e", "d"}:
                    break
            if choice == "d":
                continue
            if choice == "e":
                revised = input(f"Revised {kind} text: ").strip()
                if revised:
                    setattr(item, field, revised)
                if isinstance(item, ActionItem):
                    owner = input("Owner (blank for Unassigned): ").strip()
                    item.owner = owner or None
                if isinstance(item, Question):
                    status = input("Status [answered/partially_answered/unanswered/unknown]: ").strip()
                    if status in {"answered", "partially_answered", "unanswered", "unknown"}:
                        item.status = status
                    answer = input("Answer (blank for none): ").strip()
                    item.answer = answer or None
            item.needs_review = False
            item.review_reason = None
            kept.append(item)
        items[:] = kept
    bundle.status = "approved"
    return bundle


def _commit(workspace: Path, bundle: ReviewBundle) -> Path:
    if bundle.meeting.differential.provisional:
        approved_prior = previous_record(workspace, bundle.meeting)
        if approved_prior is None or approved_prior.id != bundle.meeting.differential.previous_meeting_id:
            raise ValueError("Approve the prior meeting before committing this provisional differential")
    record = reconcile(workspace, bundle.meeting)
    if record.pending_review_count:
        raise ValueError(f"{record.pending_review_count} items still require review")
    return commit_record(workspace, record, render_markdown(record), render_html(record))


def cmd_init(args) -> int:
    paths = initialize_workspace(args.workspace)
    print(f"Initialized workspace: {paths['root']}")
    return 0


def cmd_process(args) -> int:
    initialize_workspace(args.workspace)
    transcript = load_transcript(args.transcript)
    settings = load_settings(args.workspace)
    series = safe_slug(args.series or "default")
    duplicate = [record for record in meeting_records(args.workspace, series)
                 if record.source.checksum_sha256 == transcript.source.checksum_sha256]
    if duplicate:
        print(f"Already processed as {duplicate[0].id}")
        return 0
    provider_name = args.provider or settings.provider
    if provider_name == "heuristic":
        provider = HeuristicProvider()
    elif provider_name == "cborg":
        provider = CborgProvider(
            model=args.model or settings.model or "gpt-5.6-luna-medium",
            base_url=settings.cborg_url,
            timeout=settings.cborg_timeout_seconds,
            chunk_chars=settings.chunk_chars,
        )
        health = provider.health()
        if not health["model_ready"]:
            raise ProviderError(f"CBORG model {provider.model!r} is not available")
        print(f"Provider: remote CBORG model {provider.model}. Transcript content will leave this machine.")
    elif provider_name == "ollama":
        provider = OllamaProvider(
            model=args.model or settings.model,
            base_url=settings.ollama_url,
            timeout=settings.timeout_seconds,
            chunk_chars=settings.chunk_chars,
            context_tokens=settings.context_tokens,
        )
        health = provider.health()
        if not health["model_ready"]:
            installed = ", ".join(health["installed_models"]) or "none"
            raise ProviderError(f"Local model {provider.model!r} is not installed. Installed models: {installed}")
        print(f"Provider: local Ollama model {provider.model} at {settings.ollama_url}; transcript stays on this machine.")
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")
    record = provider.analyze(transcript, series)
    approved_prior = previous_record(args.workspace, record)
    provisional_prior = None if approved_prior else previous_review_record(args.workspace, record)
    record = reconcile(args.workspace, record, prior_override=provisional_prior,
                       assign_ids=provisional_prior is None)
    comparison_prior = approved_prior or provisional_prior
    if comparison_prior and hasattr(provider, "compare"):
        record.differential = provider.compare(record, comparison_prior, provisional=provisional_prior is not None)
    if record.pending_review_count or getattr(provider, "requires_confirmation", False):
        warnings = ["Confirm every review-marked item before history changes; model confidence is not a substitute for evidence."]
        if provisional_prior:
            warnings.append("The differential uses an unapproved prior review and will be revalidated at commit time.")
        review_path = write_review(
            args.workspace, record,
            warnings,
        )
        bundle = load_review(review_path)
        preview_path = write_review_preview(review_path, render_review_html(bundle))
        print(f"Review required before history can change: {review_path}")
        print(f"Visual review dashboard: {preview_path}")
        if sys.stdin.isatty() and input("Review now? [y/N]: ").strip().lower() == "y":
            bundle = interactive_review(load_review(review_path))
            directory = _commit(args.workspace, bundle)
            review_path.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
            print(f"Meeting committed: {directory}")
            return 0
        print(f"Run `didwedoit review {review_path}` in an interactive terminal, or edit it and run `didwedoit approve {review_path}`.")
        return 6
    bundle = ReviewBundle(status="approved", meeting=record)
    directory = _commit(args.workspace, bundle)
    print(f"Meeting committed: {directory}")
    return 0


def cmd_summarize(args) -> int:
    """Create the simple dated Markdown handoff without mutating meeting history."""
    initialize_workspace(args.workspace)
    transcript = load_transcript(args.transcript)
    settings = load_settings(args.workspace)
    series = safe_slug(args.series or "default")
    provider_name = args.provider or settings.provider
    if provider_name == "cborg":
        provider = CborgProvider(
            model=args.model or settings.model or "gpt-5.6-luna-medium",
            base_url=settings.cborg_url,
            timeout=settings.cborg_timeout_seconds,
            chunk_chars=settings.chunk_chars,
        )
        health = provider.health()
        if not health["model_ready"]:
            raise ProviderError(f"CBORG model {provider.model!r} is not available")
        print(f"Provider: remote CBORG model {provider.model}. Transcript content will leave this machine.")
    elif provider_name == "ollama":
        provider = OllamaProvider(
            model=args.model or settings.model, base_url=settings.ollama_url,
            timeout=settings.timeout_seconds, chunk_chars=settings.chunk_chars,
            context_tokens=settings.context_tokens,
        )
    elif provider_name == "heuristic":
        provider = HeuristicProvider()
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")
    record = provider.analyze(transcript, series)
    output_dir = args.workspace.resolve() / "summaries"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{transcript.meeting_date.strftime('%Y%m%d')}_{series}.md"
    if output_path.exists() and not args.force:
        raise ValueError(f"Summary already exists: {output_path}. Use --force to replace it.")
    content = render_summary_markdown(record)
    temporary = output_path.with_suffix(".md.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(output_path)
    print(f"Meeting summary: {output_path}")
    print(f"Pending confirmation: {record.pending_review_count} items")
    if record.pending_review_count:
        print("Review the unchecked Pending Confirmation items with the user before using this summary for slides.")
    return 0


def cmd_doctor(args) -> int:
    initialize_workspace(args.workspace)
    settings = load_settings(args.workspace)
    provider_name = args.provider or settings.provider
    if provider_name == "heuristic":
        result = {"ok": True, "provider": "heuristic", "network": "unused"}
    elif provider_name == "cborg":
        provider = CborgProvider(
            model=args.model or settings.model or "gpt-5.6-luna-medium",
            base_url=settings.cborg_url,
            timeout=min(settings.cborg_timeout_seconds, 20),
            chunk_chars=settings.chunk_chars,
        )
        health = provider.health()
        result = {"ok": health["model_ready"], "provider": "cborg", "model": provider.model,
                  "model_ready": health["model_ready"]}
    elif provider_name == "ollama":
        provider = OllamaProvider(
            model=args.model or settings.model,
            base_url=settings.ollama_url,
            timeout=min(settings.timeout_seconds, 10),
            chunk_chars=settings.chunk_chars,
            context_tokens=settings.context_tokens,
        )
        health = provider.health()
        result = {"ok": health["model_ready"], "provider": "ollama", "url": settings.ollama_url,
                  "model": provider.model, **health}
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Provider: {result['provider']}")
        if provider_name == "cborg":
            print(f"Remote CBORG model: {result['model']} ({'ready' if result['model_ready'] else 'not available'})")
            print("Privacy: transcript content is sent to the configured CBORG endpoint.")
        elif provider_name == "ollama":
            print(f"Local server: {result['url']} (version {result['version']})")
            print(f"Configured model: {result['model']} ({'ready' if result['model_ready'] else 'not installed'})")
            print(f"Installed models: {', '.join(result['installed_models']) or 'none'}")
        else:
            print("Heuristic fallback is ready; it does not use a language model.")
    return 0 if result["ok"] else 4


def cmd_review(args) -> int:
    bundle = interactive_review(load_review(args.review_file))
    directory = _commit(args.workspace, bundle)
    args.review_file.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
    print(f"Meeting committed: {directory}")
    return 0


def cmd_approve(args) -> int:
    bundle = load_review(args.review_file)
    if bundle.meeting.pending_review_count:
        print("Approval refused: edit the review file and set needs_review=false only after resolving each ambiguity.", file=sys.stderr)
        return 6
    bundle.status = "approved"
    directory = _commit(args.workspace, bundle)
    args.review_file.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
    print(f"Meeting committed: {directory}")
    return 0


def cmd_list(args) -> int:
    records = meeting_records(args.workspace, args.series)
    if args.json:
        print(json.dumps([{"id": item.id, "date": str(item.date), "series": item.series, "title": item.title} for item in records], indent=2))
    else:
        for item in records:
            print(f"{item.date}  {item.id}  {item.series}  {item.title}")
    return 0


def cmd_show(args) -> int:
    matches = [record for record in meeting_records(args.workspace) if record.id == args.meeting_id]
    if not matches:
        print(f"Meeting not found: {args.meeting_id}", file=sys.stderr)
        return 2
    print(matches[0].model_dump_json(indent=2) if args.json else render_markdown(matches[0]))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="didwedoit", description="Evidence-backed meeting continuity from Zoom TXT transcripts")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Initialize an inspectable local workspace")
    init.add_argument("workspace", nargs="?", type=Path, default=Path.cwd())
    init.set_defaults(func=cmd_init)

    process = subparsers.add_parser("process", help="Extract a transcript and require review before uncertain data is committed")
    process.add_argument("transcript", type=Path)
    process.add_argument("--series", help="Meeting series; defaults to 'default'")
    process.add_argument("--workspace", type=Path, default=Path.cwd())
    process.add_argument("--provider", choices=("cborg", "ollama", "heuristic"), help="Override configured provider")
    process.add_argument("--model", help="Override the configured model name")
    process.set_defaults(func=cmd_process)

    summarize = subparsers.add_parser("summarize", help="Write a dated, editable Markdown meeting summary")
    summarize.add_argument("transcript", type=Path)
    summarize.add_argument("--series", help="Meeting series used in the output filename")
    summarize.add_argument("--workspace", type=Path, default=Path.cwd())
    summarize.add_argument("--provider", choices=("cborg", "ollama", "heuristic"))
    summarize.add_argument("--model", help="Override the configured model")
    summarize.add_argument("--force", action="store_true", help="Replace an existing same-date summary")
    summarize.set_defaults(func=cmd_summarize)

    doctor = subparsers.add_parser("doctor", help="Check the configured provider and model")
    doctor.add_argument("--workspace", type=Path, default=Path.cwd())
    doctor.add_argument("--provider", choices=("cborg", "ollama", "heuristic"))
    doctor.add_argument("--model")
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(func=cmd_doctor)

    for name, function, help_text in (
        ("review", cmd_review, "Interactively resolve a pending review"),
        ("approve", cmd_approve, "Commit a manually resolved review file"),
    ):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("review_file", type=Path)
        command.add_argument("--workspace", type=Path, default=Path.cwd())
        command.set_defaults(func=function)

    listing = subparsers.add_parser("list", help="List committed meetings")
    listing.add_argument("--series")
    listing.add_argument("--workspace", type=Path, default=Path.cwd())
    listing.add_argument("--json", action="store_true")
    listing.set_defaults(func=cmd_list)

    show = subparsers.add_parser("show", help="Show one committed meeting")
    show.add_argument("meeting_id")
    show.add_argument("--workspace", type=Path, default=Path.cwd())
    show.add_argument("--json", action="store_true")
    show.set_defaults(func=cmd_show)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        return args.func(args)
    except ProviderError as exc:
        print(f"Provider error: {exc}", file=sys.stderr)
        return 4
    except (InputError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
