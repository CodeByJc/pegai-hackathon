"""Test generation prompts — Stage 4."""
from __future__ import annotations

from app.prompts import get_strategy

_SYSTEM_BASIC = """\
You are a Python test engineer. Write pytest tests for the bugfix.
Return JSON with a 'tests' array. Each item: path, content."""

_SYSTEM_STRUCTURED = """\
You are a senior Python test engineer specialising in regression testing.

Your task is to write pytest tests that:
1. Reproduce the original bug (verify it was actually broken before the fix).
2. Confirm the fix works correctly.
3. Test edge cases related to the root cause.

RULES:
1. Tests must be runnable with: pytest <path>
2. Use standard pytest conventions (no class required).
3. Test function names must be descriptive (e.g., test_divide_with_valid_divisor).
4. Import from the project modules using relative paths available in the project.
5. Keep tests focused on the reported bug and fix — do not over-test.
6. Respond ONLY with valid JSON. No prose.

RESPONSE SCHEMA:
{
  "tests": [
    {
      "path": "string — relative path like tests/test_<module>.py",
      "content": "string — full pytest file content"
    }
  ]
}"""

_USER_TEMPLATE = """\
Project context:
{context}

Root cause:
{root_cause}

Applied fix description:
{fix_description}

Write regression tests. Return JSON only."""


def get_test_prompts(context: str, root_cause: str, fix_description: str) -> tuple[str, str]:
    strategy = get_strategy()
    system = _SYSTEM_STRUCTURED if strategy == "structured" else _SYSTEM_BASIC
    user = _USER_TEMPLATE.format(
        context=context,
        root_cause=root_cause,
        fix_description=fix_description,
    )
    return system, user
