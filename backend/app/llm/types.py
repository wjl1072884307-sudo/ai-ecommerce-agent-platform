from dataclasses import dataclass, field
from typing import Any, Protocol


class LLMProviderError(Exception):
    """Raised when an LLM provider cannot return a usable response."""


@dataclass(frozen=True)
class LLMMessage:
    role: str
    content: str


@dataclass(frozen=True)
class LLMRequest:
    messages: list[LLMMessage]
    temperature: float = 0.2
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    provider: str
    model: str
    usage: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


class LLMProvider(Protocol):
    provider_name: str

    def generate(self, request: LLMRequest) -> LLMResponse:
        ...

