"""Fix generation prompts — Stage 3."""
from __future__ import annotations

from app.prompts import get_strategy

_SYSTEM_BASIC = """\
You are a Python debugging expert. Propose the smallest safe fix for the bug.
Return JSON with: root_cause, description, files_to_modify (list with path, description, patch)."""

_SYSTEM_STRUCTURED = """\
You are a senior Python engineer tasked with generating a precise, minimal fix for a diagnosed bug.

RULES:
1. Apply the smallest change that resolves the root cause.
2. Do NOT refactor unrelated code.
3. For each file that must change, provide the full corrected file content in 'patch'.
4. List ONLY files that actually need modification.
5. Respond ONLY with valid JSON. No prose, no markdown.

RESPONSE SCHEMA:
{
  "root_cause": "string — one-sentence root cause",
  "description": "string — explanation of what the fix does and why",
  "files_to_modify": [
    {
      "path": "string — relative file path",
      "description": "string — what changed in this file",
      "patch": "string — full corrected file content"
    }
  ]
}"""

_USER_TEMPLATE = """\
Project context:
{context}

Diagnosis:
{diagnosis}

Top hypothesis:
{hypothesis}

Generate the fix. Return JSON only."""


def get_fix_prompts(context: str, diagnosis: str, hypothesis: str) -> tuple[str, str]:
    strategy = get_strategy()
    system = _SYSTEM_STRUCTURED if strategy == "structured" else _SYSTEM_BASIC
    user = _USER_TEMPLATE.format(
        context=context, diagnosis=diagnosis, hypothesis=hypothesis
    )
    return system, user
