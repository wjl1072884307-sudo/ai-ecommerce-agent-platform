import httpx
import pytest


def test_openai_compatible_provider_calls_chat_completions():
    from app.llm.openai_compatible_provider import OpenAICompatibleProvider
    from app.llm.types import LLMMessage, LLMRequest

    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers.get("Authorization")
        captured["json"] = request.read().decode("utf-8")
        return httpx.Response(
            200,
            json={
                "model": "demo-model",
                "choices": [{"message": {"content": "provider reply"}}],
                "usage": {"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6},
            },
        )

    provider = OpenAICompatibleProvider(
        base_url="https://llm.example.com/v1",
        api_key="test-key",
        model="demo-model",
        timeout_seconds=3,
        transport=httpx.MockTransport(handler),
    )

    response = provider.generate(LLMRequest(messages=[LLMMessage(role="user", content="hello")]))

    assert captured["url"] == "https://llm.example.com/v1/chat/completions"
    assert captured["authorization"] == "Bearer test-key"
    assert '"model":"demo-model"' in captured["json"]
    assert response.provider == "openai-compatible"
    assert response.model == "demo-model"
    assert response.content == "provider reply"
    assert response.usage["total_tokens"] == 6


def test_openai_compatible_provider_wraps_http_errors():
    from app.llm.openai_compatible_provider import OpenAICompatibleProvider
    from app.llm.types import LLMMessage, LLMProviderError, LLMRequest

    provider = OpenAICompatibleProvider(
        base_url="https://llm.example.com/v1",
        api_key="test-key",
        model="demo-model",
        timeout_seconds=3,
        transport=httpx.MockTransport(lambda request: httpx.Response(500, json={"error": "failed"})),
    )

    with pytest.raises(LLMProviderError):
        provider.generate(LLMRequest(messages=[LLMMessage(role="user", content="hello")]))


def test_openai_compatible_provider_requires_base_url_and_api_key():
    from app.llm.openai_compatible_provider import OpenAICompatibleProvider
    from app.llm.types import LLMProviderError

    with pytest.raises(LLMProviderError):
        OpenAICompatibleProvider(base_url="", api_key="test-key", model="demo-model")

    with pytest.raises(LLMProviderError):
        OpenAICompatibleProvider(base_url="https://llm.example.com/v1", api_key="", model="demo-model")

