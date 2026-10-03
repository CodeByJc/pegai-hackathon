"""Diagnosis prompts — Stage 1 of the debugging pipeline."""
from __future__ import annotations

from app.prompts import get_strategy

# ── System prompts ────────────────────────────────────────────────────────────

_SYSTEM_BASIC = """\
You are an expert Python debugger. Analyse the provided Python project and traceback.
Return a JSON object with fields: error_type, error_message, location (file, line, function),
root_cause, summary."""

_SYSTEM_STRUCTURED = """\
You are an expert Python debugging assistant with deep knowledge of Python internals,
common runtime errors, and software engineering best practices.

Your task is to perform a precise, evidence-based diagnosis of a Python runtime error.

RULES:
1. Read the full traceback carefully — do not skip lines.
2. Identify the exact error type and message.
3. Pinpoint the specific file and line number where the error originates.
4. Identify the function or method involved.
5. Provide a concise but technically accurate root cause explanation.
6. Do NOT invent evidence. Only reference what is visible in the provided code.
7. Respond ONLY with valid JSON matching the schema. No prose, no markdown.

RESPONSE SCHEMA:
{
  "error_type": "string — Python exception class name",
  "error_message": "string — exact error message from the traceback",
  "location": {
    "file": "string — relative file path",
    "line": "integer or null — line number",
    "function": "string or null — function/method name"
  },
  "root_cause": "string — concise technical explanation of the root cause",
  "summary": "string — 1-2 sentence plain-language summary for the developer"
}"""


# ── User prompt ───────────────────────────────────────────────────────────────

_USER_TEMPLATE = """\
Please diagnose the following Python error.

{context}

Respond with a valid JSON object only."""

_USER_TEMPLATE_BASIC = """\
Diagnose this Python error and return JSON.

{context}"""


# ── Few-shot examples (structured strategy only) ──────────────────────────────

_FEW_SHOT = """\

EXAMPLE INPUT:
TRACEBACK
---------
Traceback (most recent call last):
  File "main.py", line 5, in <module>
    result = calculator.divide(10, config["divisor"])
  File "calculator.py", line 12, in divide
    return a / b
KeyError: 'divisor'

FILE: config.py
---------------
config = {"division": 2}

EXAMPLE OUTPUT:
{
  "error_type": "KeyError",
  "error_message": "'divisor'",
  "location": {"file": "calculator.py", "line": 12, "function": "divide"},
  "root_cause": "config.py defines the key as 'division' but calculator.py accesses 'divisor'.",
  "summary": "A KeyError is raised because the configuration dictionary uses the key 'division' but the code looks up 'divisor'."
}
---
"""


# ── Public API ────────────────────────────────────────────────────────────────

def get_diagnosis_prompts(context: str) -> tuple[str, str]:
    """
    Return (system_prompt, user_prompt) for Stage 1 diagnosis.
    Strategy is selected from settings.
    """
    strategy = get_strategy()
    if strategy == "structured":
        system = _SYSTEM_STRUCTURED
        user = _FEW_SHOT + _USER_TEMPLATE.format(context=context)
    else:
        system = _SYSTEM_BASIC
        user = _USER_TEMPLATE_BASIC.format(context=context)

    return system, user
