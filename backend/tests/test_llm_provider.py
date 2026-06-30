import pytest


def test_mock_provider_returns_stable_response():
    from app.llm.mock_provider import MockProvider
    from app.llm.types import LLMMessage, LLMRequest

    provider = MockProvider(model="mock-agent")
    response = provider.generate(
        LLMRequest(
            messages=[
                LLMMessage(role="system", content="You are a support agent."),
                LLMMessage(role="user", content="Can I return this order?"),
            ]
        )
    )

    assert response.provider == "mock"
    assert response.model == "mock-agent"
    assert "Mock LLM reply" in response.content


def test_llm_factory_builds_mock_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_MODEL", "factory-mock")

    from app.core.config import get_settings
    from app.llm.factory import get_llm_provider
    from app.llm.mock_provider import MockProvider

    get_settings.cache_clear()
    provider = get_llm_provider()

    assert isinstance(provider, MockProvider)
    assert provider.model == "factory-mock"


def test_llm_factory_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "unknown-provider")

    from app.core.config import get_settings
    from app.llm.factory import LLMProviderConfigError, get_llm_provider

    get_settings.cache_clear()

    with pytest.raises(LLMProviderConfigError):
        get_llm_provider()
    get_settings.cache_clear()
