"""
Application configuration.

All settings are loaded from environment variables.
Never hardcode secrets or API keys — set them in a .env file locally
(excluded from version control via .gitignore) or as real env vars in
production.

Required env vars for the agent pipeline (set before running):
  DEEPSEEK_API_KEY    — DeepSeek API key (default LLM — DeepSeek V4 Flash)
  TAVILY_API_KEY      — Tavily web-search API key (retrieval augmentation)

Optional LLM fallbacks:
  ANTHROPIC_API_KEY   — Claude API key (alternative provider)
  OPENAI_API_KEY      — OpenAI API key (alternative provider)

Model selection:
  DEFAULT_MODEL       — model identifier passed to the LLM client
                        (default: "deepseek-chat", i.e. DeepSeek V4 Flash-0731)
  DEEPSEEK_BASE_URL   — base URL for DeepSeek's OpenAI-compatible API
                        (default: "https://api.deepseek.com/v1")

Runtime:
  APP_ENV             — "development" | "production" (default: "development")
  LOG_LEVEL           — "DEBUG" | "INFO" | "WARNING" | "ERROR" (default: "INFO")
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Primary LLM: DeepSeek (OpenAI-compatible API) ---
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"

    # Default model identifier — pinned to DeepSeek V4 Flash.
    # Override via DEFAULT_MODEL env var to swap models without touching code.
    default_model: str = "deepseek-chat"

    # --- Fallback / alternative LLM providers ---
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # --- Retrieval ---
    tavily_api_key: str = ""

    # --- Runtime environment ---
    app_env: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",           # load from .env if present
        env_file_encoding="utf-8",
        case_sensitive=False,      # DEEPSEEK_API_KEY == deepseek_api_key
        extra="ignore",            # silently ignore unknown env vars
    )


# Single shared instance — import this everywhere rather than instantiating Settings() again.
settings = Settings()
