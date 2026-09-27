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

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


KNOWN_PROVIDERS = ("nvidia_nim", "openrouter", "gemini", "deepseek_direct")


class ProviderConfig(BaseModel):
    """Configuration object for a single LLM provider."""
    name: str
    api_key: str = ""
    base_url: str = ""
    model: str = ""


def parse_provider_chain(chain: str | list[str]) -> list[str]:
    """Parse and validate an LLM provider chain string or sequence.

    Parameters
    ----------
    chain:
        A comma-separated string (e.g. "nvidia_nim,openrouter,gemini,deepseek_direct")
        or a list of provider names.

    Returns
    -------
    list[str]
        Normalized list of provider names.

    Raises
    ------
    ValueError
        If the chain is empty or contains unknown provider names.
    """
    if isinstance(chain, str):
        raw_items = [item.strip().lower() for item in chain.split(",") if item.strip()]
    elif isinstance(chain, (list, tuple)):
        raw_items = [str(item).strip().lower() for item in chain if str(item).strip()]
    else:
        raise ValueError(f"Invalid provider chain type: {type(chain).__name__}. Expected str or list.")

    if not raw_items:
        raise ValueError("LLM_PROVIDER_CHAIN cannot be empty.")

    invalid = [p for p in raw_items if p not in KNOWN_PROVIDERS]
    if invalid:
        raise ValueError(
            f"Unknown provider(s) in LLM_PROVIDER_CHAIN: {', '.join(invalid)}. "
            f"Known providers are: {', '.join(KNOWN_PROVIDERS)}"
        )

    return raw_items


class Settings(BaseSettings):
    # --- Multi-Provider Fallback Configuration ---
    llm_provider_mode: str = "auto"
    llm_provider_chain: str = "nvidia_nim,openrouter,gemini,deepseek_direct"
    llm_provider_cooldown_sec: int = 60
    llm_provider_max_retries_per_call: int = 4

    # --- Active LLM Provider (manual mode legacy) ---
    llm_provider: str = "deepseek"

    # --- NVIDIA NIM (OpenAI-compatible API) ---
    nvidia_nim_api_key: str = ""
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_nim_model: str = "deepseek-ai/deepseek-v4.1-flash"

    # --- OpenRouter (OpenAI-compatible API) ---
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "deepseek/deepseek-chat:free"

    # --- Gemini (OpenAI-compatible API via Google AI Studio) ---
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_model: str = "gemini-3.5-flash"

    # --- DeepSeek Direct ---
    deepseek_direct_api_key: str = ""
    deepseek_direct_base_url: str = "https://api.deepseek.com/v1"
    deepseek_direct_model: str = "deepseek-chat"

    # --- DeepSeek Legacy (OpenAI-compatible API) ---
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"

    # Default model identifier — pinned to model in use.
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

    @field_validator("llm_provider_chain")
    @classmethod
    def validate_provider_chain(cls, v: str) -> str:
        parse_provider_chain(v)
        return v

    @property
    def provider_chain(self) -> list[str]:
        return parse_provider_chain(self.llm_provider_chain)

    def get_provider_config(self, provider: str) -> ProviderConfig:
        p = (provider or "").strip().lower()
        if p == "nvidia_nim":
            return ProviderConfig(
                name="nvidia_nim",
                api_key=self.nvidia_nim_api_key,
                base_url=self.nvidia_nim_base_url,
                model=self.nvidia_nim_model,
            )
        elif p == "openrouter":
            return ProviderConfig(
                name="openrouter",
                api_key=self.openrouter_api_key,
                base_url=self.openrouter_base_url,
                model=self.openrouter_model,
            )
        elif p == "gemini":
            return ProviderConfig(
                name="gemini",
                api_key=self.gemini_api_key,
                base_url=self.gemini_base_url,
                model=self.gemini_model,
            )
        elif p in ("deepseek_direct", "deepseek"):
            return ProviderConfig(
                name="deepseek_direct",
                api_key=self.deepseek_direct_api_key or self.deepseek_api_key,
                base_url=self.deepseek_direct_base_url or self.deepseek_base_url,
                model=self.deepseek_direct_model or self.default_model,
            )
        else:
            raise ValueError(
                f"Unknown provider '{provider}'. Known providers are: {', '.join(KNOWN_PROVIDERS)}"
            )

    @property
    def providers(self) -> dict[str, ProviderConfig]:
        """Dictionary of ProviderConfig objects for all known providers."""
        return {p: self.get_provider_config(p) for p in KNOWN_PROVIDERS}

    @property
    def llm_api_key(self) -> str:
        provider = (self.llm_provider or "").lower()
        if provider == "nvidia_nim":
            return self.nvidia_nim_api_key or self.openrouter_api_key or self.gemini_api_key or self.deepseek_api_key
        if provider == "gemini":
            return self.gemini_api_key or self.openrouter_api_key or self.deepseek_api_key
        if provider == "openrouter":
            return self.openrouter_api_key or self.deepseek_api_key
        return self.deepseek_direct_api_key or self.deepseek_api_key or self.openrouter_api_key or self.gemini_api_key

    @property
    def llm_base_url(self) -> str:
        provider = (self.llm_provider or "").lower()
        if provider == "nvidia_nim":
            return self.nvidia_nim_base_url
        if provider == "gemini":
            return self.gemini_base_url
        if provider == "openrouter":
            return self.openrouter_base_url
        return self.deepseek_direct_base_url or self.deepseek_base_url

    model_config = SettingsConfigDict(
        env_file=".env",           # load from .env if present
        env_file_encoding="utf-8",
        case_sensitive=False,      # DEEPSEEK_API_KEY == deepseek_api_key
        extra="ignore",            # silently ignore unknown env vars
    )


# Single shared instance — import this everywhere rather than instantiating Settings() again.
settings = Settings()
