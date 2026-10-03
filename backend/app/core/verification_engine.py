"""
Verification Engine — source of truth for fix verification.

Does NOT call Gemini. Uses only real execution results.
"""
from __future__ import annotations

import logging

from app.models.diagnosis import VerificationResult

logger = logging.getLogger(__name__)


class VerificationEngine:
    """
    Determines whether the proposed fix actually resolved the bug.

    Decision criteria (all must be true for VERIFIED):
    1. Sandbox executed without timeout/infrastructure error.
    2. Exit code is 0.
    3. No tests failed.
    4. Original error is no longer present in output.
    """

    def evaluate(self, result: VerificationResult) -> VerificationResult:
        """
        Evaluate the result and potentially upgrade/downgrade the status.

        The ResultParser does the initial status assignment; this engine
        applies any additional cross-field logic.
        """
        logger.info(
            "VerificationEngine: status=%s exit_code=%s tests_run=%s "
            "passed=%s failed=%s original_error_absent=%s",
            result.status, result.exit_code, result.tests_run,
            result.passed, result.failed, result.original_error_absent,
        )

        # Promote to verified only when all conditions are met
        if (
            result.exit_code == 0
            and result.failed == 0
            and result.tests_run > 0          # must have actually run tests
            and result.original_error_absent
        ):
            result.status = "verified"
        elif result.status not in ("timeout", "execution_error"):
            if result.tests_run == 0 and result.exit_code == 0:
                # Nothing ran — treat as not verified (no evidence either way)
                result.status = "not_verified"
            elif result.failed > 0 or result.exit_code != 0:
                result.status = "failed"

        logger.info("VerificationEngine final status: %s", result.status)
        return result

    def is_verified(self, result: VerificationResult) -> bool:
        return result.status == "verified"
