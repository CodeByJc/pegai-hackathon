"""
Google Gemini provider — concrete implementation of the LLM interface.

Uses the official google-genai SDK with structured JSON output when a
response_schema is provided.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional, Type

import google.generativeai as genai
from google.generativeai import types as gtypes
from pydantic import BaseModel

from app.config.settings import get_settings
from app.core.errors import ErrorCode, PyDebugHTTPException
from app.llm.schemas import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class GeminiProvider:
    """
    Wraps the Google Gemini API.

    Responsibilities:
    - Authentication
    - Prompt formatting (system + user)
    - Structured JSON output enforcement
    - Response parsing and Pydantic validation
    """

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Please add it to your .env file."
            )
        genai.configure(api_key=settings.gemini_api_key)
        self._model_name = settings.gemini_model
        self._temperature = settings.gemini_temperature
        self._max_output_tokens = settings.gemini_max_output_tokens
        logger.info("GeminiProvider initialised with model: %s", self._model_name)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Send a prompt to Gemini and return a structured LLMResponse.
        Raises PyDebugHTTPException on failure.
        """
        settings = get_settings()
        temperature = request.temperature if request.temperature is not None else self._temperature

        generation_config = gtypes.GenerationConfig(
            temperature=temperature,
            max_output_tokens=settings.gemini_max_output_tokens,
        )

        # Build the model — add JSON response_mime_type when schema is provided
        model_kwargs: dict[str, Any] = {
            "model_name": self._model_name,
            "generation_config": generation_config,
            "system_instruction": request.system_prompt,
        }

        if request.response_schema is not None:
            generation_config = gtypes.GenerationConfig(
                temperature=temperature,
                max_output_tokens=settings.gemini_max_output_tokens,
                response_mime_type="application/json",
            )
            model_kwargs["generation_config"] = generation_config

        model = genai.GenerativeModel(**model_kwargs)

        logger.debug("Gemini request to model '%s' (schema=%s)",
                     self._model_name, request.response_schema)

        try:
            response = await model.generate_content_async(request.user_prompt)
        except Exception as exc:
            logger.error("Gemini API error: %s", exc, exc_info=True)
            raise PyDebugHTTPException(
                status_code=502,
                code=ErrorCode.LLM_ERROR,
                message=f"Gemini API request failed: {exc}",
            ) from exc

        raw_text = response.text.strip()
        logger.debug("Gemini raw response length: %d chars", len(raw_text))

        parsed: Optional[BaseModel] = None
        if request.response_schema is not None:
            parsed = self._parse_structured(raw_text, request.response_schema)

        # Extract token counts if available
        usage = getattr(response, "usage_metadata", None)
        input_tokens = getattr(usage, "prompt_token_count", 0) or 0
        output_tokens = getattr(usage, "candidates_token_count", 0) or 0

        return LLMResponse(
            raw_text=raw_text,
            parsed=parsed,
            model_used=self._model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    def _parse_structured(self, raw_text: str, schema: Type[BaseModel]) -> BaseModel:
        """Parse JSON text into the given Pydantic schema. Raises on failure."""
        # Strip possible markdown code fences
        text = raw_text
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(
                line for line in lines
                if not line.startswith("```")
            ).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error("Gemini response is not valid JSON: %s", exc)
            raise PyDebugHTTPException(
                status_code=422,
                code=ErrorCode.INVALID_LLM_RESPONSE,
                message=f"LLM response could not be parsed as JSON: {exc}",
            ) from exc

        try:
            return schema.model_validate(data)
        except Exception as exc:
            logger.error("Gemini response failed Pydantic validation: %s", exc)
            raise PyDebugHTTPException(
                status_code=422,
                code=ErrorCode.INVALID_LLM_RESPONSE,
                message=f"LLM response did not match expected schema: {exc}",
            ) from exc
