"""LLM-layer Pydantic schemas (provider-agnostic)."""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel


class LLMRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    response_schema: Optional[Any] = None    # Pydantic model class for structured output
    temperature: Optional[float] = None


class LLMResponse(BaseModel):
    model_config = {"protected_namespaces": ()}   # suppress 'model_used' warning
    raw_text: str
    parsed: Optional[Any] = None             # validated Pydantic model instance
    model_used: str
    input_tokens: int = 0
    output_tokens: int = 0
