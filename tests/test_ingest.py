from pathlib import Path

import pytest

from didwedoit.ingest import InputError, load_transcript


ZOOM = """07:00:02 --> 07:00:04
Alice Example: Hello everyone.

07:00:05 --> 07:00:09
Bob Example: Why is the result different?
"""


def test_zoom_parse_preserves_original_lines_and_filename_date(tmp_path: Path):
    path = tmp_path / "20260808_weekly.txt"
    path.write_text(ZOOM, encoding="utf-8")
    transcript = load_transcript(path)
    assert str(transcript.meeting_date) == "2026-08-08"
    assert [turn.speaker for turn in transcript.turns] == ["Alice Example", "Bob Example"]
    assert transcript.turns[1].line_start == 4
    assert transcript.turns[1].evidence().excerpt == "Why is the result different?"


def test_zoom_parse_accepts_webvtt_millisecond_timestamps(tmp_path: Path):
    path = tmp_path / "20260402_weekly.txt"
    path.write_text(
        "WEBVTT\n\n00:01:49.000 --> 00:01:50.000\nAlice Example: Hello.\n",
        encoding="utf-8",
    )
    transcript = load_transcript(path)
    assert len(transcript.turns) == 1
    assert transcript.turns[0].timestamp_start == "00:01:49.000"
    assert transcript.turns[0].timestamp_end == "00:01:50.000"


def test_date_is_required_in_filename(tmp_path: Path):
    path = tmp_path / "meeting.txt"
    path.write_text(ZOOM, encoding="utf-8")
    with pytest.raises(InputError, match="YYYYMMDD"):
        load_transcript(path)
