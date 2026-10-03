"""File validation — backend-side, never trust the frontend."""
from __future__ import annotations

import re
from pathlib import PurePosixPath

from app.config.settings import get_settings
from app.core.errors import ErrorCode, PyDebugHTTPException

# Only pure Python source files accepted for v1
ALLOWED_EXTENSIONS = {".py"}

# Reject filenames that could be dangerous
_SAFE_FILENAME_RE = re.compile(r"^[\w\-. ]+$")


def validate_python_file(
    filename: str,
    content: bytes,
) -> None:
    """
    Raise PyDebugHTTPException if the file does not pass all safety checks.
    Called before any bytes are written to disk.
    """
    settings = get_settings()

    # 1. Extension check
    suffix = PurePosixPath(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise PyDebugHTTPException(
            status_code=422,
            code=ErrorCode.INVALID_FILE_TYPE,
            message=f"Only Python .py files are accepted. Got: '{suffix or 'no extension'}'",
        )

    # 2. Safe filename characters (no shell metacharacters etc.)
    base = PurePosixPath(filename).name
    if not _SAFE_FILENAME_RE.match(base):
        raise PyDebugHTTPException(
            status_code=422,
            code=ErrorCode.INVALID_FILENAME,
            message=f"Filename contains invalid characters: '{base}'",
        )

    # 3. Path traversal
    if ".." in filename or filename.startswith("/"):
        raise PyDebugHTTPException(
            status_code=422,
            code=ErrorCode.PATH_TRAVERSAL,
            message="Filename must not contain path traversal sequences.",
        )

    # 4. File size
    if len(content) > settings.max_file_size_bytes:
        raise PyDebugHTTPException(
            status_code=413,
            code=ErrorCode.FILE_TOO_LARGE,
            message=(
                f"File '{filename}' exceeds maximum size of "
                f"{settings.max_file_size_bytes // 1024} KB."
            ),
        )


def validate_file_count(current: int, adding: int) -> None:
    settings = get_settings()
    if current + adding > settings.max_files_per_project:
        raise PyDebugHTTPException(
            status_code=422,
            code=ErrorCode.TOO_MANY_FILES,
            message=(
                f"Project cannot have more than {settings.max_files_per_project} files."
            ),
        )
