from typing import Any

import httpx

from app.llm.types import LLMProviderError, LLMRequest, LLMResponse


class OpenAICompatibleProvider:
    provider_name = "openai-compatible"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: int = 15,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not base_url:
            raise LLMProviderError("LLM_BASE_URL is required for openai-compatible provider.")
        if not api_key:
            raise LLMProviderError("LLM_API_KEY is required for openai-compatible provider.")

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    def generate(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": [{"role": message.role, "content": message.content} for message in request.messages],
            "temperature": request.temperature,
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds, transport=self.transport) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise LLMProviderError(f"OpenAI-compatible provider request failed: {exc}") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError("OpenAI-compatible provider returned an invalid response.") from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError("OpenAI-compatible provider returned empty content.")

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=str(data.get("model") or self.model),
            usage=_usage_dict(data.get("usage")),
            raw=data,
        )


def _usage_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}

