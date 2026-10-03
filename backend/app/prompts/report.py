"""Report summary prompts — final stage."""
from __future__ import annotations


SYSTEM = """\
You are a Python debugging assistant. Generate a concise, developer-friendly
summary of the debugging session. Be factual and accurate."""

USER_TEMPLATE = """\
Summarise the following debugging session in 2-3 short paragraphs for the developer.

Diagnosis: {diagnosis}
Fix applied: {fix}
Verification status: {status}
Tests run: {tests_run}  Passed: {passed}  Failed: {failed}

Be concise and clear."""


def get_report_prompts(
    diagnosis: str,
    fix: str,
    status: str,
    tests_run: int,
    passed: int,
    failed: int,
) -> tuple[str, str]:
    user = USER_TEMPLATE.format(
        diagnosis=diagnosis,
        fix=fix,
        status=status,
        tests_run=tests_run,
        passed=passed,
        failed=failed,
    )
    return SYSTEM, user
