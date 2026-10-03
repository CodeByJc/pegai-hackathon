"""
Result Parser — converts raw sandbox output into structured
verification information.
"""
from __future__ import annotations

import re
import logging

from app.execution.sandbox import RawExecutionResult
from app.models.diagnosis import VerificationResult

logger = logging.getLogger(__name__)

# Regex patterns for pytest output
_PASSED_RE = re.compile(r"(\d+) passed")
_FAILED_RE = re.compile(r"(\d+) failed")
_ERROR_RE = re.compile(r"(\d+) error")


class ResultParser:
    """
    Parses raw sandbox execution output into a VerificationResult.

    The values come ONLY from actual execution — never from LLM output.
    """

    def parse(
        self,
        raw: RawExecutionResult,
        original_error_type: str = "",
    ) -> VerificationResult:
        if raw.timed_out:
            return VerificationResult(
                status="timeout",
                exit_code=-1,
                stdout=raw.stdout,
                stderr=raw.stderr,
                duration_ms=raw.duration_ms,
            )

        tests_run, passed, failed = self._parse_pytest_summary(raw.stdout + raw.stderr)
        original_error_absent = self._check_error_absent(
            raw.stdout + raw.stderr, original_error_type
        )

        if "No module named pytest" in (raw.stdout + raw.stderr) or "pytest: command not found" in (raw.stdout + raw.stderr):
            status = "infrastructure_error"
        elif raw.exit_code == 0 and failed == 0:
            status = "verified"
        elif raw.exit_code != 0 and tests_run == 0:
            # No tests ran — sandbox / import error
            status = "execution_failed"
        else:
            status = "test_failed"

        return VerificationResult(
            status=status,
            exit_code=raw.exit_code,
            tests_run=tests_run,
            passed=passed,
            failed=failed,
            stdout=raw.stdout,
            stderr=raw.stderr,
            duration_ms=raw.duration_ms,
            original_error_absent=original_error_absent,
        )

    @staticmethod
    def _parse_pytest_summary(output: str) -> tuple[int, int, int]:
        passed = 0
        failed = 0
        m = _PASSED_RE.search(output)
        if m:
            passed = int(m.group(1))
        m = _FAILED_RE.search(output)
        if m:
            failed = int(m.group(1))
        return passed + failed, passed, failed

    @staticmethod
    def _check_error_absent(output: str, original_error_type: str) -> bool:
        if not original_error_type:
            return True
        return original_error_type not in output
