"""
Application configuration using Pydantic Settings.
All secrets and tunables come from environment variables / .env file.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Gemini ───────────────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model name (overridden via GEMINI_MODEL env var)",
    )
    gemini_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    gemini_max_output_tokens: int = Field(default=8192)

    # ── Repair loop ──────────────────────────────────────────────────────────
    max_repair_attempts: int = Field(default=3, ge=1, le=10)

    # ── Execution sandbox ────────────────────────────────────────────────────
    execution_timeout_seconds: int = Field(default=30, ge=5, le=300)
    sandbox_memory_limit: str = Field(default="256m")
    sandbox_cpu_quota: int = Field(default=50000)   # 50% of 1 CPU (Docker units)
    sandbox_image: str = Field(default="python:3.12-slim")

    # ── Project storage ──────────────────────────────────────────────────────
    workspaces_dir: Path = Field(default=Path("workspaces"))
    max_file_size_bytes: int = Field(default=1_000_000)   # 1 MB per file
    max_files_per_project: int = Field(default=20)

    # ── API ──────────────────────────────────────────────────────────────────
    api_prefix: str = Field(default="/api")
    cors_origins: list[str] = Field(default=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"])

    # ── Prompt strategy ──────────────────────────────────────────────────────
    prompt_strategy: str = Field(default="structured", pattern="^(basic|structured)$")

    # ── Logging ──────────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached singleton settings instance."""
    return Settings()
