"""Retry / repair prompts — used when a fix attempt fails."""
from __future__ import annotations

from app.prompts import get_strategy

_SYSTEM = """\
You are a Python debugging expert performing iterative fix analysis.

A previous fix attempt FAILED. You are provided with the actual execution results.

RULES:
1. Study the actual stdout, stderr, exit code and test failures carefully.
2. Do NOT assume the fix was partially correct — analyse the hard evidence.
3. Propose a revised root cause if necessary.
4. Propose a new minimal fix.
5. Respond ONLY with valid JSON.

RESPONSE SCHEMA:
{
  "failure_reason": "string — why the previous fix failed based on actual output",
  "revised_root_cause": "string — updated root cause analysis",
  "revised_fix": {
    "root_cause": "string",
    "description": "string",
    "files_to_modify": [
      {
        "path": "string",
        "description": "string",
        "patch": "string — full corrected file content"
      }
    ]
  }
}"""

_USER_TEMPLATE = """\
ORIGINAL TRACEBACK:
{traceback}

PROJECT CONTEXT:
{context}

PREVIOUS HYPOTHESIS:
{hypothesis}

PREVIOUS FIX DESCRIPTION:
{previous_fix}

ACTUAL EXECUTION RESULT:
Exit code: {exit_code}

STDOUT:
{stdout}

STDERR:
{stderr}

FAILED TESTS:
{failed_tests}

Analyse why the fix failed and propose a revised fix. Return JSON only."""


def get_retry_prompts(
    traceback: str,
    context: str,
    hypothesis: str,
    previous_fix: str,
    exit_code: int,
    stdout: str,
    stderr: str,
    failed_tests: str,
) -> tuple[str, str]:
    user = _USER_TEMPLATE.format(
        traceback=traceback,
        context=context,
        hypothesis=hypothesis,
        previous_fix=previous_fix,
        exit_code=exit_code,
        stdout=stdout or "(no stdout)",
        stderr=stderr or "(no stderr)",
        failed_tests=failed_tests or "(no failed test details)",
    )
    return _SYSTEM, user
