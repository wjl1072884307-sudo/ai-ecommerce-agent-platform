from pathlib import Path


def test_settings_use_safe_local_defaults(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    from app.core.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()

    assert settings.app_env == "development"
    assert settings.debug is True
    assert settings.database_url == "sqlite:///./data/app.db"
    assert settings.jwt_secret_key == "change-me-in-production"
    assert settings.llm_provider == "mock"
    assert settings.log_level == "INFO"


def test_settings_read_environment_overrides(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_NAME", "Production API")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@db:5432/app")
    monkeypatch.setenv("JWT_SECRET_KEY", "env-secret")
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "120")
    monkeypatch.setenv("LLM_PROVIDER", "openai-compatible")
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "demo-model")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "30")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "http://localhost:5173,https://console.example.com")

    from app.core.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()

    assert settings.app_env == "production"
    assert settings.app_name == "Production API"
    assert settings.debug is False
    assert settings.database_url == "postgresql+psycopg://user:pass@db:5432/app"
    assert settings.jwt_secret_key == "env-secret"
    assert settings.jwt_expire_minutes == 120
    assert settings.llm_provider == "openai-compatible"
    assert settings.llm_base_url == "https://llm.example.com/v1"
    assert settings.llm_api_key == "test-key"
    assert settings.llm_model == "demo-model"
    assert settings.llm_timeout_seconds == 30
    assert settings.log_level == "DEBUG"
    assert settings.backend_cors_origins == ["http://localhost:5173", "https://console.example.com"]


def test_env_examples_document_required_settings():
    root_example = Path(__file__).resolve().parents[2] / ".env.example"
    backend_example = Path(__file__).resolve().parents[1] / ".env.example"

    root_content = root_example.read_text(encoding="utf-8")
    backend_content = backend_example.read_text(encoding="utf-8")
    combined = root_content + "\n" + backend_content

    for key in [
        "APP_ENV",
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "LLM_PROVIDER",
        "LLM_BASE_URL",
        "LLM_API_KEY",
        "LLM_MODEL",
        "LLM_TIMEOUT_SECONDS",
        "LOG_LEVEL",
    ]:
        assert f"{key}=" in combined

    assert "sk-" not in combined
    assert "real" not in combined.lower()

