from app.llm.types import LLMRequest, LLMResponse


class MockProvider:
    provider_name = "mock"

    def __init__(self, model: str = "mock-agent") -> None:
        self.model = model

    def generate(self, request: LLMRequest) -> LLMResponse:
        user_message = next((message.content for message in reversed(request.messages) if message.role == "user"), "")
        content = f"Mock LLM reply: {user_message[:120]}"
        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=self.model,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            raw={"mock": True},
        )

