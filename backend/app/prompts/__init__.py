"""
Prompt strategy abstraction.

Strategy A (basic): direct instructions.
Strategy B (structured): decomposition + few-shot examples + strict schema.

The active strategy is set via PROMPT_STRATEGY env var.
"""
from __future__ import annotations

from app.config.settings import get_settings


def get_strategy() -> str:
    return get_settings().prompt_strategy
