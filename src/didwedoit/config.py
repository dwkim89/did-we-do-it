from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    provider: str = "cborg"
    model: str = ""
    chunk_chars: int = 40_000
    context_tokens: int = 16_384
    ollama_url: str = "http://127.0.0.1:11434"
    timeout_seconds: int = 300
    cborg_url: str = ""
    cborg_timeout_seconds: int = 300


def load_settings(workspace: Path) -> Settings:
    values: dict = {}
    config_path = workspace.expanduser().resolve() / "didwedoit.toml"
    if config_path.is_file():
        with config_path.open("rb") as handle:
            values = tomllib.load(handle)
    analysis = values.get("analysis", {})
    ollama = values.get("ollama", {})
    cborg = values.get("cborg", {})
    settings = Settings(
        provider=os.getenv("DIDWEDOIT_PROVIDER", analysis.get("provider", "cborg")),
        model=os.getenv("DIDWEDOIT_MODEL", analysis.get("model", "")),
        chunk_chars=int(os.getenv("DIDWEDOIT_CHUNK_CHARS", analysis.get("chunk_chars", 40_000))),
        context_tokens=int(os.getenv("DIDWEDOIT_CONTEXT_TOKENS", analysis.get("context_tokens", 16_384))),
        ollama_url=os.getenv("DIDWEDOIT_OLLAMA_URL", ollama.get("url", "http://127.0.0.1:11434")),
        timeout_seconds=int(os.getenv("DIDWEDOIT_TIMEOUT_SECONDS", ollama.get("timeout_seconds", 300))),
        cborg_url=os.getenv("CBORG_BASE_URL", os.getenv("OPENAI_BASE_URL", cborg.get("url", ""))),
        cborg_timeout_seconds=int(os.getenv("DIDWEDOIT_CBORG_TIMEOUT_SECONDS", cborg.get("timeout_seconds", 300))),
    )
    if settings.provider not in {"cborg", "ollama", "heuristic"}:
        raise ValueError(f"Unsupported provider: {settings.provider}")
    if settings.chunk_chars < 2_000 or settings.chunk_chars > 100_000:
        raise ValueError("chunk_chars must be between 2,000 and 100,000")
    if settings.context_tokens < 4_096 or settings.context_tokens > 40_960:
        raise ValueError("context_tokens must be between 4,096 and 40,960")
    if settings.provider == "ollama":
        parsed_url = urlparse(settings.ollama_url)
        if parsed_url.scheme != "http" or parsed_url.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("The Ollama adapter only permits a localhost URL")
    if settings.provider == "cborg":
        parsed_url = urlparse(settings.cborg_url)
        if parsed_url.scheme != "https" or not parsed_url.hostname:
            raise ValueError("CBORG requires CBORG_BASE_URL or OPENAI_BASE_URL with an HTTPS URL")
    return settings
