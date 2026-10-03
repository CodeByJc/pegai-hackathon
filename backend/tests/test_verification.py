"""Tests for ResultParser and VerificationEngine."""
import pytest
from app.execution.result_parser import ResultParser
from app.execution.sandbox import RawExecutionResult
from app.core.verification_engine import VerificationEngine


def make_raw(exit_code=0, stdout="", stderr="", timed_out=False, duration_ms=100):
    return RawExecutionResult(
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_ms=duration_ms,
        timed_out=timed_out,
    )


class TestResultParser:
    def setup_method(self):
        self.parser = ResultParser()

    def test_passes_correctly(self):
        stdout = "3 passed in 0.12s"
        raw = make_raw(exit_code=0, stdout=stdout)
        result = self.parser.parse(raw)
        assert result.status == "verified"
        assert result.passed == 3
        assert result.failed == 0

    def test_fails_correctly(self):
        stdout = "2 passed, 1 failed in 0.08s"
        raw = make_raw(exit_code=1, stdout=stdout)
        result = self.parser.parse(raw)
        assert result.failed == 1
        assert result.status == "failed"

    def test_timeout(self):
        raw = make_raw(exit_code=-1, timed_out=True)
        result = self.parser.parse(raw)
        assert result.status == "timeout"

    def test_execution_error_no_tests(self):
        raw = make_raw(exit_code=1, stdout="", stderr="ImportError: no module named x")
        result = self.parser.parse(raw)
        assert result.status == "execution_error"
        assert result.tests_run == 0

    def test_original_error_absent(self):
        raw = make_raw(exit_code=0, stdout="3 passed")
        result = self.parser.parse(raw, original_error_type="KeyError")
        assert result.original_error_absent is True

    def test_original_error_present(self):
        raw = make_raw(exit_code=1, stdout="KeyError: 'divisor'\n1 failed")
        result = self.parser.parse(raw, original_error_type="KeyError")
        assert result.original_error_absent is False


class TestVerificationEngine:
    def setup_method(self):
        self.engine = VerificationEngine()

    def test_verified(self):
        from app.models.diagnosis import VerificationResult
        vr = VerificationResult(
            status="verified",
            exit_code=0,
            tests_run=3,
            passed=3,
            failed=0,
            original_error_absent=True,
        )
        result = self.engine.evaluate(vr)
        assert result.status == "verified"
        assert self.engine.is_verified(result)

    def test_failed_when_tests_fail(self):
        from app.models.diagnosis import VerificationResult
        vr = VerificationResult(
            status="failed",
            exit_code=1,
            tests_run=3,
            passed=2,
            failed=1,
            original_error_absent=True,
        )
        result = self.engine.evaluate(vr)
        assert result.status == "failed"
        assert not self.engine.is_verified(result)

    def test_not_verified_without_tests(self):
        from app.models.diagnosis import VerificationResult
        vr = VerificationResult(
            status="verified",
            exit_code=0,
            tests_run=0,   # no tests ran
            passed=0,
            failed=0,
            original_error_absent=True,
        )
        result = self.engine.evaluate(vr)
        assert result.status != "verified"
