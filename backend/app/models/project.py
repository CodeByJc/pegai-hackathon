"""Pydantic models for Projects."""
from __future__ import annotations

import enum
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class ProjectStatus(str, enum.Enum):
    CREATED = "created"
    FILES_UPLOADED = "files_uploaded"
    TRACEBACK_SET = "traceback_set"
    DIAGNOSING = "diagnosing"
    FIXING = "fixing"
    EXECUTING = "executing"
    VERIFIED = "verified"
    FAILED = "failed"
    UNVERIFIED = "unverified"
    ERROR = "error"


class UploadedFile(BaseModel):
    path: str
    size_bytes: int
    sha256: str


class ProjectMetadata(BaseModel):
    project_id: str
    status: ProjectStatus = ProjectStatus.CREATED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    files: list[UploadedFile] = Field(default_factory=list)
    traceback: Optional[str] = None
    error_type: Optional[str] = None
    repair_attempts: int = 0
    max_repair_attempts: int = 3
    result_path: Optional[str] = None   # relative path to final report JSON

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


class ProjectCreateRequest(BaseModel):
    description: Optional[str] = Field(
        default=None, max_length=1000, description="Optional human description"
    )


class ProjectCreateResponse(BaseModel):
    project_id: str
    status: ProjectStatus
    created_at: datetime


class TracebackRequest(BaseModel):
    traceback: str = Field(..., min_length=1, max_length=50_000)


class ProjectSummaryResponse(BaseModel):
    project_id: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    file_count: int
    has_traceback: bool
