"""
Projects API — project creation, file upload, traceback management.

Routes are thin: they validate input and delegate to ProjectManager.
No business logic lives here.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from app.core.errors import ErrorCode, PyDebugHTTPException
from app.models.project import (
    ProjectCreateRequest,
    ProjectCreateResponse,
    ProjectStatus,
    ProjectSummaryResponse,
    TracebackRequest,
)
from app.projects.manager import ProjectManager
from app.projects.validator import validate_file_count, validate_python_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_manager() -> ProjectManager:
    return ProjectManager()


@router.post("", response_model=ProjectCreateResponse, status_code=201)
async def create_project(
    body: Optional[ProjectCreateRequest] = None,
    pm: ProjectManager = Depends(get_project_manager),
) -> ProjectCreateResponse:
    """Create a new debugging project."""
    meta = pm.create_project()
    return ProjectCreateResponse(
        project_id=meta.project_id,
        status=meta.status,
        created_at=meta.created_at,
    )


@router.get("/{project_id}", response_model=ProjectSummaryResponse)
async def get_project(project_id: str, pm: ProjectManager = Depends(get_project_manager)) -> ProjectSummaryResponse:
    """Return metadata summary for a project."""
    try:
        meta = pm.get_project(project_id)
    except FileNotFoundError:
        raise PyDebugHTTPException(
            status_code=404,
            code=ErrorCode.PROJECT_NOT_FOUND,
            message=f"Project '{project_id}' not found.",
        )
    return ProjectSummaryResponse(
        project_id=meta.project_id,
        status=meta.status,
        created_at=meta.created_at,
        updated_at=meta.updated_at,
        file_count=len(meta.files),
        has_traceback=bool(meta.traceback),
    )


@router.post("/{project_id}/files", status_code=200)
async def upload_files(
    project_id: str,
    files: list[UploadFile] = File(...),
    pm: ProjectManager = Depends(get_project_manager),
) -> dict:
    """
    Upload one or more Python .py files to the project.
    Validation is performed server-side regardless of what the frontend sends.
    """
    try:
        meta = pm.get_project(project_id)
    except FileNotFoundError:
        raise PyDebugHTTPException(
            status_code=404,
            code=ErrorCode.PROJECT_NOT_FOUND,
            message=f"Project '{project_id}' not found.",
        )

    validate_file_count(current=len(meta.files), adding=len(files))

    uploaded = []
    for upload in files:
        content = await upload.read()
        filename = upload.filename or "unnamed.py"
        validate_python_file(filename, content)
        pm.add_file(project_id, filename, content)
        uploaded.append(filename)
        logger.info("Uploaded '%s' to project %s", filename, project_id)

    return {
        "project_id": project_id,
        "uploaded": uploaded,
        "total_files": len(meta.files) + len(uploaded),
    }


@router.post("/{project_id}/traceback", status_code=200)
async def set_traceback(project_id: str, body: TracebackRequest, pm: ProjectManager = Depends(get_project_manager)) -> dict:
    """Store/update the traceback for a project."""
    try:
        meta = pm.set_traceback(project_id, body.traceback)
    except FileNotFoundError:
        raise PyDebugHTTPException(
            status_code=404,
            code=ErrorCode.PROJECT_NOT_FOUND,
            message=f"Project '{project_id}' not found.",
        )
    return {
        "project_id": project_id,
        "status": meta.status,
        "traceback_length": len(body.traceback),
    }


@router.get("/{project_id}/result")
async def get_result(project_id: str, pm: ProjectManager = Depends(get_project_manager)) -> JSONResponse:
    """Return the latest debugging result report for a project."""
    if not pm.project_exists(project_id):
        raise PyDebugHTTPException(
            status_code=404,
            code=ErrorCode.PROJECT_NOT_FOUND,
            message=f"Project '{project_id}' not found.",
        )
    result_json = pm.get_result(project_id)
    if result_json is None:
        raise PyDebugHTTPException(
            status_code=404,
            code=ErrorCode.PROJECT_NOT_FOUND,
            message="No result available yet. Run /diagnose first.",
        )
    import json
    return JSONResponse(content=json.loads(result_json))
