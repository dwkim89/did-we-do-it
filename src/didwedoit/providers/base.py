from __future__ import annotations

from typing import Protocol

from ..ingest import Transcript
from ..models import MeetingRecord


class AnalysisProvider(Protocol):
    name: str

    def analyze(self, transcript: Transcript, series: str) -> MeetingRecord: ...
