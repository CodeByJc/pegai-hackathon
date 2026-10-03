"""Pydantic models for Diagnosis, Hypotheses, Fix, Tests."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ── Diagnosis ─────────────────────────────────────────────────────────────────

class ErrorLocation(BaseModel):
    file: str
    line: Optional[int] = None
    function: Optional[str] = None


class DiagnosisResult(BaseModel):
    error_type: str
    error_message: str
    location: ErrorLocation
    root_cause: str
    summary: str


# ── Hypotheses ────────────────────────────────────────────────────────────────

class Hypothesis(BaseModel):
    rank: int
    title: str
    explanation: str
    confidence: str = Field(..., pattern="^(high|medium|low)$")
    evidence: list[str] = Field(default_factory=list)
    affected_files: list[str] = Field(default_factory=list)


class HypothesisResult(BaseModel):
    hypotheses: list[Hypothesis]


# ── Fix ───────────────────────────────────────────────────────────────────────

class FilePatch(BaseModel):
    path: str
    description: str
    patch: str       # unified diff or full file content depending on strategy


class FixProposal(BaseModel):
    root_cause: str
    description: str
    files_to_modify: list[FilePatch]


# ── Tests ─────────────────────────────────────────────────────────────────────

class GeneratedTestFile(BaseModel):
    path: str
    content: str


class GeneratedTests(BaseModel):
    tests: list[GeneratedTestFile]


# ── Failure analysis (retry) ──────────────────────────────────────────────────

class FailureAnalysis(BaseModel):
    failure_reason: str
    revised_root_cause: str
    revised_fix: FixProposal


# ── Final debugging report ────────────────────────────────────────────────────

class DebugReport(BaseModel):
    project_id: str
    diagnosis: Optional[DiagnosisResult] = None
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    fix: Optional[FixProposal] = None
    tests: list[GeneratedTestFile] = Field(default_factory=list)
    verification: Optional["VerificationResult"] = None
    repair_attempts: int = 0
    status: str = "pending"       # verified | failed | unverified | error


# ── Verification ──────────────────────────────────────────────────────────────

class VerificationResult(BaseModel):
    status: str   # verified | failed | not_verified | not_run | timeout | execution_error
    exit_code: Optional[int] = None
    tests_run: int = 0
    passed: int = 0
    failed: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    original_error_absent: bool = False


# resolve forward ref
DebugReport.model_rebuild()
