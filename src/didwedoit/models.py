from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceRef(StrictModel):
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)
    speaker: str | None = None
    timestamp_start: str | None = None
    timestamp_end: str | None = None
    excerpt: str | None = None

    @model_validator(mode="after")
    def valid_range(self) -> "EvidenceRef":
        if self.line_end < self.line_start:
            raise ValueError("line_end must be at or after line_start")
        return self


class Reviewable(StrictModel):
    confidence: Confidence = Confidence.MEDIUM
    needs_review: bool = False
    review_reason: str | None = None
    evidence: list[EvidenceRef] = Field(min_length=1)


class Question(Reviewable):
    id: str | None = None
    text: str
    status: Literal["answered", "partially_answered", "unanswered", "unknown"] = "unknown"
    answer: str | None = None


class ActionItem(Reviewable):
    id: str | None = None
    description: str
    owner: str | None = None
    status: Literal["open", "in_progress", "blocked", "completed", "cancelled", "unknown"] = "open"
    prior_id: str | None = None
    relation: Literal["new", "same", "progressed", "blocked", "completed", "changed", "cancelled"] = "new"


class Decision(Reviewable):
    id: str | None = None
    description: str


class Blocker(Reviewable):
    id: str | None = None
    description: str
    owner: str | None = None


class Diagnosis(Reviewable):
    id: str | None = None
    category: Literal["progress", "risk", "root_cause", "attention"]
    severity: Literal["low", "medium", "high", "critical"]
    finding: str
    reason: str


class DeltaItem(StrictModel):
    kind: Literal[
        "baseline", "new", "progressed", "still_open", "blocked", "unblocked",
        "completed", "changed", "cancelled", "not_discussed", "resolved", "reopened"
    ]
    entity_type: Literal["action", "question", "decision", "blocker", "diagnosis"]
    description: str
    reason: str
    prior_id: str | None = None
    current_id: str | None = None
    confidence: Confidence = Confidence.HIGH


class MeetingDifferential(StrictModel):
    previous_meeting_id: str | None = None
    baseline: bool = True
    provisional: bool = False
    changes: list[DeltaItem] = Field(default_factory=list)
    attention: list[str] = Field(default_factory=list)


class SourceInfo(StrictModel):
    path: str
    checksum_sha256: str
    line_count: int = Field(ge=1)
    format: Literal["zoom_txt"] = "zoom_txt"


class MeetingRecord(StrictModel):
    schema_version: int = 1
    id: str
    series: str
    title: str
    date: date
    participants: list[str]
    executive_summary: str
    topics: list[str]
    questions: list[Question]
    actions: list[ActionItem]
    decisions: list[Decision]
    blockers: list[Blocker]
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    differential: MeetingDifferential = Field(default_factory=MeetingDifferential)
    source: SourceInfo
    previous_meeting_id: str | None = None
    not_discussed_action_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    extractor: str = "heuristic-v1"

    @property
    def pending_review_count(self) -> int:
        collections = (self.questions, self.actions, self.decisions, self.blockers, self.diagnoses)
        return sum(item.needs_review for items in collections for item in items)


class MeetingExtraction(StrictModel):
    """Provider-produced content before trusted source metadata is attached."""

    executive_summary: str
    topics: list[str] = Field(default_factory=list)
    questions: list[Question] = Field(default_factory=list)
    actions: list[ActionItem] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    blockers: list[Blocker] = Field(default_factory=list)
    diagnoses: list[Diagnosis] = Field(default_factory=list)


class ProviderQuestion(StrictModel):
    text: str
    status: Literal["answered", "partially_answered", "unanswered", "unknown"]
    answer: str | None = None
    confidence: Confidence
    evidence: list[EvidenceRef] = Field(min_length=1, max_length=3)


class ProviderAction(StrictModel):
    description: str
    owner: str | None = None
    status: Literal["open", "in_progress", "blocked", "completed", "cancelled", "unknown"]
    confidence: Confidence
    evidence: list[EvidenceRef] = Field(min_length=1, max_length=3)


class ProviderDecision(StrictModel):
    description: str
    confidence: Confidence
    evidence: list[EvidenceRef] = Field(min_length=1, max_length=3)


class ProviderBlocker(StrictModel):
    description: str
    owner: str | None = None
    confidence: Confidence
    evidence: list[EvidenceRef] = Field(min_length=1, max_length=3)


class ProviderDiagnosis(StrictModel):
    category: Literal["progress", "risk", "root_cause", "attention"]
    severity: Literal["low", "medium", "high", "critical"]
    finding: str
    reason: str
    confidence: Confidence
    evidence: list[EvidenceRef] = Field(min_length=1, max_length=3)


class ProviderExtraction(StrictModel):
    """Small schema sent to a model; application-owned fields are excluded."""

    executive_summary: str
    topics: list[str] = Field(default_factory=list, max_length=10)
    questions: list[ProviderQuestion] = Field(default_factory=list, max_length=20)
    actions: list[ProviderAction] = Field(default_factory=list, max_length=20)
    decisions: list[ProviderDecision] = Field(default_factory=list, max_length=12)
    blockers: list[ProviderBlocker] = Field(default_factory=list, max_length=12)
    diagnoses: list[ProviderDiagnosis] = Field(default_factory=list, max_length=10)


class ProviderSynthesis(StrictModel):
    executive_summary: str = Field(max_length=1_200)
    topics: list[str] = Field(min_length=1, max_length=10)


class ProviderDeltaItem(StrictModel):
    kind: Literal[
        "new", "progressed", "still_open", "blocked", "unblocked", "completed", "changed",
        "cancelled", "not_discussed", "resolved", "reopened"
    ]
    entity_type: Literal["action", "question", "decision", "blocker", "diagnosis"]
    description: str
    reason: str
    current_index: int | None = Field(default=None, ge=0)
    prior_id: str | None = None
    confidence: Confidence


class ProviderComparison(StrictModel):
    changes: list[ProviderDeltaItem] = Field(default_factory=list, max_length=100)
    attention: list[str] = Field(default_factory=list, max_length=20)


class ReviewBundle(StrictModel):
    schema_version: int = 1
    status: Literal["pending_review", "approved"] = "pending_review"
    meeting: MeetingRecord
    warnings: list[str] = Field(default_factory=list)
