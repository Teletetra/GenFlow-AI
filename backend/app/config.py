from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite:///./genflow.db"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-latest"
    llm_provider: str = "openai"
    cors_origins: str = "http://localhost:5173"
    cache_ttl_seconds: int = 900

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
