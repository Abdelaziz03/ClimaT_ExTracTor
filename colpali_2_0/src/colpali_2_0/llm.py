from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LocalLLMConfig:
    provider: str = "ollama"
    model_name: str = "mistral:7b-instruct"


def describe_local_llm(config: LocalLLMConfig | None = None) -> str:
    cfg = config or LocalLLMConfig()
    return (
        f"Local LLM provider={cfg.provider}, model={cfg.model_name}. "
        "This is a medium-sized model suitable for local semantic enrichment."
    )
