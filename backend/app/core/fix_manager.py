"""
Fix Manager — applies AI-proposed fixes to the working copy.

CRITICAL:
  - original/ is NEVER modified.
  - All changes go into working/ only.
"""
from __future__ import annotations

import logging
from pathlib import PurePosixPath

from app.core.errors import ErrorCode, PyDebugHTTPException
from app.models.diagnosis import FixProposal, GeneratedTestFile
from app.projects.workspace import ProjectWorkspace

logger = logging.getLogger(__name__)


def _safe_relative(path_str: str) -> str:
    """Reject path traversal attempts in AI-provided file paths."""
    p = PurePosixPath(path_str)
    if p.is_absolute() or ".." in p.parts:
        raise PyDebugHTTPException(
            status_code=422,
            code=ErrorCode.PATH_TRAVERSAL,
            message=f"LLM proposed unsafe file path: '{path_str}'",
        )
    return str(p)


class FixManager:
    """
    Applies a validated FixProposal to the working/ workspace and
    writes AI-generated test files.
    """

    def apply_fix(
        self,
        workspace: ProjectWorkspace,
        fix: FixProposal,
        tests: list[GeneratedTestFile],
    ) -> None:
        """
        1. Reset working/ from original/.
        2. Apply each file patch from the FixProposal.
        3. Write generated test files.
        """
        logger.info(
            "Applying fix to workspace %s — %d file(s) to modify, %d test(s)",
            workspace.project_id,
            len(fix.files_to_modify),
            len(tests),
        )

        # Step 1: clean working/ copy from original/
        workspace.reset_working()

        # Step 2: apply proposed file changes
        for file_patch in fix.files_to_modify:
            safe_path = _safe_relative(file_patch.path)
            content = file_patch.patch.encode("utf-8")
            workspace.write_working(safe_path, content)
            logger.debug("Applied patch to: %s", safe_path)

        # Step 3: write generated tests
        for test_file in tests:
            safe_path = _safe_relative(test_file.path)
            content = test_file.content.encode("utf-8")
            workspace.write_working(safe_path, content)
            logger.debug("Wrote test file: %s", safe_path)

        logger.info("Fix applied successfully to %s", workspace.project_id)
