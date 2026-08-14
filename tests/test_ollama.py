from pathlib import Path

from didwedoit.ingest import load_transcript
from didwedoit.providers.ollama import OllamaProvider


ZOOM = """10:00:00 --> 10:00:05
Alice: Why does the validation fail in the forward region?

10:00:06 --> 10:00:12
Bob: I will check the input coordinates tomorrow.
"""


class ReplayOllama(OllamaProvider):
    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        if path == "/api/version":
            return {"version": "test"}
        if path == "/api/tags":
            return {"models": [{"name": "test-model"}]}
        return {
            "message": {
                "content": """{
                  "executive_summary": "The team discussed a forward-region validation failure.",
                  "topics": ["forward-region validation"],
                  "questions": [{
                    "text": "Why does the validation fail in the forward region?",
                    "status": "unknown", "answer": null,
                    "confidence": "medium",
                    "evidence": [{"line_start": 1, "line_end": 2, "speaker": "Alice",
                      "timestamp_start": "10:00:00", "timestamp_end": "10:00:05",
                      "excerpt": "Why does the validation fail in the forward region?"}]
                  }],
                  "actions": [{
                    "description": "Check the input coordinates tomorrow.",
                    "owner": "Bob", "status": "open", "confidence": "high",
                    "evidence": [{"line_start": 4, "line_end": 5, "speaker": "Bob",
                      "timestamp_start": "10:00:06", "timestamp_end": "10:00:12",
                      "excerpt": "I will check the input coordinates tomorrow."}]
                  }],
                  "decisions": [], "blockers": []
                }"""
            }
        }


def test_ollama_health_and_schema_validated_extraction(tmp_path: Path):
    path = tmp_path / "20260808_local.txt"
    path.write_text(ZOOM, encoding="utf-8")
    provider = ReplayOllama("test-model", chunk_chars=2_000)
    assert provider.health()["model_ready"] is True
    record = provider.analyze(load_transcript(path), "local")
    assert record.extractor == "ollama-v1:test-model"
    assert record.actions[0].owner == "Bob"
    assert record.actions[0].needs_review is True
    assert record.questions[0].needs_review is True
    assert "could not establish" in record.questions[0].review_reason


def test_ollama_rejects_non_loopback_url():
    for url in ("http://example.com:11434", "http://localhost.evil.example:11434"):
        try:
            OllamaProvider("model", base_url=url)
        except RuntimeError as exc:
            assert "localhost" in str(exc)
        else:
            raise AssertionError("remote Ollama URL was accepted")
