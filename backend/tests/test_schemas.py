"""Tests for Pydantic schemas (models)."""
import pytest
from pydantic import ValidationError
from app.models.diagnosis import (
    DiagnosisResult,
    ErrorLocation,
    Hypothesis,
    HypothesisResult,
    FixProposal,
    FilePatch,
    GeneratedTests,
    GeneratedTestFile,
    FailureAnalysis,
    VerificationResult,
)


class TestDiagnosisResult:
    def test_valid(self):
        d = DiagnosisResult(
            error_type="KeyError",
            error_message="'divisor'",
            location=ErrorLocation(file="calc.py", line=12),
            root_cause="Config key mismatch",
            summary="A KeyError occurred.",
        )
        assert d.error_type == "KeyError"

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            DiagnosisResult(
                error_type="KeyError",
                error_message="'x'",
                # missing location
                root_cause="...",
                summary="...",
            )


class TestHypothesisResult:
    def test_valid(self):
        h = Hypothesis(
            rank=1, title="T", explanation="E",
            confidence="high", evidence=["a"], affected_files=["f.py"],
        )
        result = HypothesisResult(hypotheses=[h])
        assert len(result.hypotheses) == 1

    def test_invalid_confidence(self):
        with pytest.raises(ValidationError):
            Hypothesis(rank=1, title="T", explanation="E", confidence="very_high")


class TestFixProposal:
    def test_valid(self):
        fp = FixProposal(
            root_cause="rc",
            description="desc",
            files_to_modify=[FilePatch(path="a.py", description="fix", patch="x=1")],
        )
        assert len(fp.files_to_modify) == 1


class TestVerificationResult:
    def test_default_status(self):
        vr = VerificationResult(status="verified", exit_code=0, tests_run=3, passed=3)
        assert vr.failed == 0

    def test_timeout_status(self):
        vr = VerificationResult(status="timeout", exit_code=-1)
        assert vr.status == "timeout"
