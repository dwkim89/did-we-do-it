import json
from pathlib import Path

from didwedoit.ingest import load_transcript
from didwedoit.providers.cborg import CborgProvider


ZOOM = """10:00:00 --> 10:00:05
Alice: Why does validation fail in the forward region?

10:00:06 --> 10:00:12
Bob: I will check the input coordinates tomorrow because the data may be shifted.
"""


class ReplayCborg(CborgProvider):
    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        if path == "/models":
            return {"data": [{"id": "gpt-5.6-luna-medium"}]}
        name = body["response_format"]["json_schema"]["name"]
        if name == "meeting_synthesis":
            content = {"executive_summary": "The team investigated a forward validation failure and assigned a coordinate check.",
                       "topics": ["forward validation", "input coordinates"]}
        elif name == "meeting_comparison":
            content = {"changes": [
                {"kind": "progressed", "entity_type": "action", "description": "Coordinate check progressed.",
                 "reason": "The same coordinate investigation recurs with a concrete check.",
                 "current_index": 0, "prior_id": "AI-0001", "confidence": "high"},
                {"kind": "still_open", "entity_type": "question", "description": "The failure remains under study.",
                 "reason": "No conclusive answer was recorded.", "current_index": 0,
                 "prior_id": "Q-0001", "confidence": "high"},
                {"kind": "new", "entity_type": "diagnosis", "description": "Possible coordinate shift.",
                 "reason": "The current meeting states a possible cause.", "current_index": 0,
                 "prior_id": None, "confidence": "medium"}],
                "attention": ["Confirm whether the coordinate shift explains the validation failure."]}
        else:
            content = {
                "executive_summary": "A forward validation failure may involve shifted input coordinates.",
                "topics": ["forward validation"],
                "questions": [{"text": "Why does validation fail in the forward region?", "status": "unanswered",
                               "answer": None, "confidence": "high", "evidence": [{"line_start": 1, "line_end": 2,
                               "speaker": "Alice", "timestamp_start": "10:00:00", "timestamp_end": "10:00:05",
                               "excerpt": "Why does validation fail in the forward region?"}]}],
                "actions": [{"description": "Check the input coordinates tomorrow.", "owner": "Bob", "status": "open",
                             "confidence": "high", "evidence": [{"line_start": 4, "line_end": 5, "speaker": "Bob",
                             "timestamp_start": "10:00:06", "timestamp_end": "10:00:12",
                             "excerpt": "I will check the input coordinates tomorrow."}]}],
                "decisions": [], "blockers": [],
                "diagnoses": [{"category": "root_cause", "severity": "medium",
                               "finding": "Input coordinates may be shifted.",
                               "reason": "Bob explicitly identified a possible data shift.", "confidence": "medium",
                               "evidence": [{"line_start": 4, "line_end": 5, "speaker": "Bob",
                               "timestamp_start": "10:00:06", "timestamp_end": "10:00:12",
                               "excerpt": "because the data may be shifted"}]}],
            }
        return {"choices": [{"message": {"content": json.dumps(content)}}]}


def test_cborg_structured_extraction_and_diagnosis(tmp_path: Path):
    path = tmp_path / "20260808_remote.txt"
    path.write_text(ZOOM, encoding="utf-8")
    provider = ReplayCborg(base_url="https://cborg.example/v1")
    assert provider.health()["model_ready"] is True
    record = provider.analyze(load_transcript(path), "detector")
    assert record.extractor == "cborg-v1:gpt-5.6-luna-medium"
    assert record.actions[0].owner == "Bob"
    assert record.diagnoses[0].category == "root_cause"
    assert record.diagnoses[0].needs_review is True
    assert provider.requires_confirmation is True

    prior = record.model_copy(deep=True)
    prior.id = "M-20260801-prior"
    prior.actions[0].id = "AI-0001"
    prior.questions[0].id = "Q-0001"
    current = record.model_copy(deep=True)
    current.actions[0].id = None
    current.questions[0].id = None
    differential = provider.compare(current, prior, provisional=True)
    assert differential.provisional is True
    assert differential.changes[0].kind == "progressed"
    assert current.actions[0].prior_id == "AI-0001"
