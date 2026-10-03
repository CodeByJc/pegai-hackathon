"""
Verification API — re-run verification on demand.

Useful for the frontend to trigger a fresh sandbox run without
re-running the full diagnosis pipeline.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter

from app.core.errors import ErrorCode, PyDebugHTTPException
from app.core.verification_engine import VerificationEngine
from app.execution.result_parser import ResultParser
from app.execution.runner import ExecutionRunner
from app.models.diagnosis import VerificationResult
from app.projects.manager import ProjectManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["verification"])

_pm = ProjectManager()
_runner = ExecutionRunner()
_parser = ResultParser()
_verifier = VerificationEngine()


@router.post("/{project_id}/verify", response_model=VerificationResult)
async def verify(project_id: str) -> VerificationResult:
    """
    Re-run sandbox execution on the current working/ copy and return
    an updated VerificationResult.
    """
    try:
        meta = _pm.get_project(project_id)
    except FileNotFoundError:
        raise PyDebugHTTPException(
            status_code=404,
            code=ErrorCode.PROJECT_NOT_FOUND,
            message=f"Project '{project_id}' not found.",
        )

    workspace = _pm.get_workspace(project_id)
    if not workspace.working.exists():
        raise PyDebugHTTPException(
            status_code=422,
            code=ErrorCode.INVALID_PROJECT,
            message="No working copy found. Run /diagnose first.",
        )

    raw = await _runner.run_tests(working_dir=workspace.working)
    result = _parser.parse(raw, original_error_type=meta.error_type or "")
    return _verifier.evaluate(result)
