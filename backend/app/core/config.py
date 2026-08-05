"""
Application configuration.

All settings are loaded from environment variables.
Never hardcode secrets or API keys — set them in a .env file locally
(excluded from version control via .gitignore) or as real env vars in
production.

Required env vars for the agent pipeline (set before running):
  ANTHROPIC_API_KEY   — Claude API key (primary LLM)
  OPENAI_API_KEY      — OpenAI API key (fallback / alternative LLM)

Optional:
  APP_ENV             — "development" | "production" (default: "development")
  LOG_LEVEL           — "DEBUG" | "INFO" | "WARNING" | "ERROR" (default: "INFO")
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM API keys — loaded from env vars, never hardcoded
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Runtime environment
    app_env: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",          # load from .env if present
        env_file_encoding="utf-8",
        case_sensitive=False,     # ANTHROPIC_API_KEY == anthropic_api_key
        extra="ignore",           # silently ignore unknown env vars
    )


# Single shared instance — import this everywhere rather than instantiating Settings() again.
settings = Settings()
