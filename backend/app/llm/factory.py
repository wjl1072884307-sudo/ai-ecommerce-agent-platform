from app.core.config import get_settings
from app.llm.mock_provider import MockProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider
from app.llm.types import LLMProvider


class LLMProviderConfigError(ValueError):
    pass


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    provider = settings.llm_provider.lower()
    if provider == "mock":
        return MockProvider(model=settings.llm_model)
    if provider in {"openai-compatible", "openai_compatible"}:
        return OpenAICompatibleProvider(
            base_url=settings.llm_base_url or "",
            api_key=settings.llm_api_key or "",
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    raise LLMProviderConfigError(f"Unsupported LLM provider: {settings.llm_provider}")

