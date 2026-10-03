"""
LLM Service — provider-agnostic façade.

DebuggingEngine talks to LLMService only. LLMService delegates to a
concrete provider (GeminiProvider). Swapping providers requires no
changes outside this module.
"""
from __future__ import annotations

import logging
from typing import Any, Optional, Type

from pydantic import BaseModel

from app.llm.gemini_provider import GeminiProvider
from app.llm.schemas import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class LLMService:
    """
    Provider-agnostic LLM façade used by the Debugging Engine.

    To add a new provider (OpenAI, Anthropic, local), implement a class
    with the same `generate(request)` interface and inject it here.
    """

    def __init__(self, provider: Optional[Any] = None) -> None:
        self._provider = provider or GeminiProvider()

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """
        Send a prompt and return a structured response.

        Parameters
        ----------
        system_prompt : str
            Instruction context given to the model.
        user_prompt : str
            The actual task/question.
        response_schema : Pydantic model class, optional
            If provided, the response will be validated against this schema.
        temperature : float, optional
            Override default temperature.
        """
        request = LLMRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=response_schema,
            temperature=temperature,
        )
        logger.debug(
            "LLMService.generate — schema=%s  temperature=%s",
            response_schema.__name__ if response_schema else "None",
            temperature,
        )
        return await self._provider.generate(request)
