"""Hypothesis Engine — Stage 2 wrapper."""
from __future__ import annotations

import json
import logging

from app.llm.service import LLMService
from app.models.diagnosis import DiagnosisResult, Hypothesis, HypothesisResult
from app.prompts.hypotheses import get_hypothesis_prompts

logger = logging.getLogger(__name__)


class HypothesisEngine:
    def __init__(self, llm: LLMService) -> None:
        self._llm = llm

    async def generate(
        self,
        diagnosis: DiagnosisResult,
        context: str,
    ) -> list[Hypothesis]:
        diagnosis_text = diagnosis.model_dump_json(indent=2)
        system, user = get_hypothesis_prompts(diagnosis_text, context)
        response = await self._llm.generate(
            system_prompt=system,
            user_prompt=user,
            response_schema=HypothesisResult,
        )
        result: HypothesisResult = response.parsed  # type: ignore[assignment]
        logger.info("Generated %d hypotheses", len(result.hypotheses))
        return result.hypotheses
