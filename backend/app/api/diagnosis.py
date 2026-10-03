"""
Diagnosis API — starts the debugging pipeline.

Delegates entirely to DebuggingEngine. Route stays thin.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.core.debugging_engine import DebuggingEngine
from app.core.errors import ErrorCode, PyDebugHTTPException
from app.models.diagnosis import DebugReport

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["diagnosis"])


def get_engine() -> DebuggingEngine:
    return DebuggingEngine()


@router.post("/{project_id}/diagnose", response_model=DebugReport)
async def diagnose(
    project_id: str,
    engine: DebuggingEngine = Depends(get_engine),
) -> DebugReport:
    """
    Start the full debugging pipeline for the project.

    Returns the complete DebugReport after:
    - Context building
    - Gemini diagnosis
    - Hypothesis generation
    - Fix generation
    - Test generation
    - Sandbox execution
    - Verification
    - Repair retry loop (if needed)
    """
    logger.info("Diagnose requested for project: %s", project_id)
    return await engine.debug(project_id)
