"""Hypothesis generation prompts — Stage 2."""
from __future__ import annotations

from app.prompts import get_strategy

_SYSTEM_BASIC = """\
You are a Python debugging expert. Generate 2-4 hypotheses for the bug.
Return JSON with a 'hypotheses' array. Each item must have:
rank, title, explanation, confidence (high|medium|low), evidence (list), affected_files (list)."""

_SYSTEM_STRUCTURED = """\
You are a Python debugging expert performing systematic hypothesis generation.

Your task is to enumerate the most plausible root causes for the bug described in the diagnosis.

RULES:
1. Generate between 2 and 4 distinct hypotheses.
2. Rank them from most to least likely based on the available evidence.
3. Each hypothesis MUST be grounded in specific evidence from the provided code.
4. Do NOT fabricate evidence that is not visible in the source code.
5. Confidence must be one of: high, medium, low.
6. Respond ONLY with valid JSON. No prose.

RESPONSE SCHEMA:
{
  "hypotheses": [
    {
      "rank": integer,
      "title": "string — short descriptive title",
      "explanation": "string — detailed technical explanation",
      "confidence": "high|medium|low",
      "evidence": ["string — specific code reference or observation"],
      "affected_files": ["string — relative file paths"]
    }
  ]
}"""

_USER_TEMPLATE = """\
Given this diagnosis:

{diagnosis}

And this project context:

{context}

Generate ranked hypotheses for the root cause. Return JSON only."""


def get_hypothesis_prompts(diagnosis: str, context: str) -> tuple[str, str]:
    strategy = get_strategy()
    system = _SYSTEM_STRUCTURED if strategy == "structured" else _SYSTEM_BASIC
    user = _USER_TEMPLATE.format(diagnosis=diagnosis, context=context)
    return system, user
