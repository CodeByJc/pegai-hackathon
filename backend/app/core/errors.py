"""Structured API error handling."""
from __future__ import annotations

from fastapi import HTTPException
from pydantic import BaseModel


class APIErrorDetail(BaseModel):
    code: str
    message: str


class APIError(BaseModel):
    error: APIErrorDetail


# ── Convenience exception ─────────────────────────────────────────────────────

class PyDebugHTTPException(HTTPException):
    """FastAPI HTTPException with a structured error body."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message},
        )


# ── Error code constants ──────────────────────────────────────────────────────

class ErrorCode:
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    TOO_MANY_FILES = "TOO_MANY_FILES"
    INVALID_FILENAME = "INVALID_FILENAME"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    INVALID_PROJECT = "INVALID_PROJECT"
    TRACEBACK_REQUIRED = "TRACEBACK_REQUIRED"
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    FILES_REQUIRED = "FILES_REQUIRED"
    LLM_ERROR = "LLM_ERROR"
    INVALID_LLM_RESPONSE = "INVALID_LLM_RESPONSE"
    SANDBOX_ERROR = "SANDBOX_ERROR"
    EXECUTION_TIMEOUT = "EXECUTION_TIMEOUT"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
