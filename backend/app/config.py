from pathlib import Path
from typing import Any, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.types import SecretStr
import os
import re


def resolve_env_vars(obj: Any) -> Any:
    """Recursively resolve ${VAR} patterns in config values from environment variables."""
    if isinstance(obj, str):
        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        return re.sub(r'\$\{([^}]+)\}', replace_var, obj)
    elif isinstance(obj, dict):
        return {k: resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_env_vars(item) for item in obj]
    return obj


def load_env_file():
    """Load .env file into os.environ manually."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


class MatchingWeights(BaseSettings):
    amount: float = 0.40
    counterparty: float = 0.25
    reference: float = 0.20
    date: float = 0.15


class MatchingThresholds(BaseSettings):
    auto_match: float = 0.90
    ai_review_min: float = 0.70
    ai_review_max: float = 0.89
    exception: float = 0.70


class MatchingConfig(BaseSettings):
    exact_enabled: bool = True
    strong_enabled: bool = True
    fuzzy_enabled: bool = True
    weights: MatchingWeights = Field(default_factory=MatchingWeights)
    thresholds: MatchingThresholds = Field(default_factory=MatchingThresholds)
    date_window_days: int = 2
    amount_tolerance_pct: float = 0.001


class OllamaConfig(BaseSettings):
    base_url: str = "http://localhost:11434"
    model: str = "llama3.1:8b"
    timeout: int = 30


class GroqConfig(BaseSettings):
    api_key: Optional[SecretStr] = None
    model: str = "openai/gpt-oss-20b"


class OpenAICompatibleConfig(BaseSettings):
    base_url: Optional[str] = None
    api_key: Optional[SecretStr] = None
    model: str = "gpt-4o-mini"


class AIConfig(BaseSettings):
    provider: str = "mock"
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    groq: GroqConfig = Field(default_factory=GroqConfig)
    openai_compatible: OpenAICompatibleConfig = Field(default_factory=OpenAICompatibleConfig)
    confidence_auto_resolve: float = 0.90
    max_tool_calls: int = 3


class ScheduledEvent(BaseSettings):
    name: str
    amount: int
    frequency: str
    next_date: str


class ForecastConfig(BaseSettings):
    horizons_days: List[int] = [7, 14, 30]
    scheduled_events: List[ScheduledEvent] = []


class DatabaseConfig(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    name: str = "ai_finance"
    user: str = "postgres"
    password: SecretStr


class AppConfig(BaseSettings):
    name: str = "AI Finance Controller"
    currency: str = "INR"
    opening_cash: int = 1000000
    debug: bool = False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    matching: MatchingConfig = Field(default_factory=MatchingConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    forecast: ForecastConfig = Field(default_factory=ForecastConfig)


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        load_env_file()
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        if config_path.exists():
            import yaml
            with open(config_path) as f:
                yaml_data = yaml.safe_load(f)
            yaml_data = resolve_env_vars(yaml_data)
            _settings = Settings(**yaml_data)
        else:
            _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    global _settings
    _settings = None
    return get_settings()