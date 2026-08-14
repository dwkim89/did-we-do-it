from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .models import EvidenceRef, SourceInfo

TIMESTAMP_RE = re.compile(
    r"^(?P<start>\d{2}:\d{2}:\d{2}(?:\.\d{3})?)\s*-->\s*"
    r"(?P<end>\d{2}:\d{2}:\d{2}(?:\.\d{3})?)\s*$"
)
SPEAKER_RE = re.compile(r"^(?P<speaker>[^:\n]{1,100}):\s*(?P<text>.*)$")
FILENAME_DATE_RE = re.compile(r"(?<!\d)(?P<date>20\d{6})(?!\d)")


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class Turn:
    speaker: str
    text: str
    line_start: int
    line_end: int
    timestamp_start: str
    timestamp_end: str

    def evidence(self) -> EvidenceRef:
        return EvidenceRef(
            line_start=self.line_start,
            line_end=self.line_end,
            speaker=self.speaker,
            timestamp_start=self.timestamp_start,
            timestamp_end=self.timestamp_end,
            excerpt=self.text[:280],
        )


@dataclass(frozen=True)
class Transcript:
    path: Path
    meeting_date: date
    turns: tuple[Turn, ...]
    source: SourceInfo


def infer_date(path: Path) -> date:
    match = FILENAME_DATE_RE.search(path.name)
    if not match:
        raise InputError(
            "No unambiguous YYYYMMDD date was found in the transcript filename. "
            "Rename the file to include its meeting date."
        )
    raw = match.group("date")
    try:
        return date(int(raw[:4]), int(raw[4:6]), int(raw[6:8]))
    except ValueError as exc:
        raise InputError(f"Invalid date {raw!r} in transcript filename") from exc


def _parse_turns(lines: list[str]) -> list[Turn]:
    turns: list[Turn] = []
    index = 0
    while index < len(lines):
        stamp = TIMESTAMP_RE.match(lines[index].strip())
        if not stamp:
            index += 1
            continue
        cursor = index + 1
        while cursor < len(lines) and not lines[cursor].strip():
            cursor += 1
        if cursor >= len(lines):
            break
        speaker = SPEAKER_RE.match(lines[cursor].strip())
        if not speaker:
            index = cursor + 1
            continue
        text_parts = [speaker.group("text").strip()]
        end_line = cursor + 1
        lookahead = cursor + 1
        while lookahead < len(lines):
            if TIMESTAMP_RE.match(lines[lookahead].strip()):
                break
            if lines[lookahead].strip():
                text_parts.append(lines[lookahead].strip())
                end_line = lookahead + 1
            lookahead += 1
        text = " ".join(part for part in text_parts if part).strip()
        if text:
            turns.append(
                Turn(
                    speaker=speaker.group("speaker").strip(),
                    text=text,
                    line_start=index + 1,
                    line_end=end_line,
                    timestamp_start=stamp.group("start"),
                    timestamp_end=stamp.group("end"),
                )
            )
        index = lookahead
    return turns


def load_transcript(path: Path, max_bytes: int = 5_000_000) -> Transcript:
    path = path.expanduser().resolve()
    if path.suffix.lower() != ".txt":
        raise InputError("MVP input must be a .txt file")
    if not path.is_file():
        raise InputError(f"Transcript does not exist: {path}")
    data = path.read_bytes()
    if not data:
        raise InputError("Transcript is empty")
    if len(data) > max_bytes:
        raise InputError(f"Transcript exceeds the {max_bytes:,}-byte safety limit")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError("Transcript must be UTF-8 encoded") from exc
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    turns = _parse_turns(lines)
    if not turns:
        raise InputError("No Zoom timestamp/speaker blocks were found")
    source = SourceInfo(
        path=str(path),
        checksum_sha256=hashlib.sha256(data).hexdigest(),
        line_count=len(lines),
    )
    return Transcript(path, infer_date(path), tuple(turns), source)
