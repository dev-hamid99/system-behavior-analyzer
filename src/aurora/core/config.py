from __future__ import annotations

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class AppConfig:
    dark_mode: bool = True
    ai_local_only: bool = True
    update_channel: str = "stable"
    default_scan_timeout_s: int = 30


@dataclass(frozen=True)
class RuntimeConfig:
    llm_provider: str = getenv("AURORA_LLM_PROVIDER", "local")
    llm_api_key: str | None = getenv("AURORA_LLM_API_KEY")


APP_CONFIG = AppConfig()
RUNTIME_CONFIG = RuntimeConfig()
