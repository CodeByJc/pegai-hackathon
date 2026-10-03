"""
Execution Runner — orchestrates sandbox execution for a project workspace.

Responsibilities:
- Determine which command to run (pytest vs plain python).
- Call DockerSandbox.
- Return raw execution result.
"""
from __future__ import annotations

import logging
from pathlib import Path

from app.config.settings import get_settings
from app.execution.sandbox import DockerSandbox, RawExecutionResult

logger = logging.getLogger(__name__)


class ExecutionRunner:
    """Coordinates sandbox execution for a working project directory."""

    def __init__(self) -> None:
        self._sandbox = DockerSandbox()

    async def run_tests(
        self,
        working_dir: Path,
        test_paths: list[str] | None = None,
    ) -> RawExecutionResult:
        """
        Run pytest inside the sandbox.

        Parameters
        ----------
        working_dir : Path
            The working/ directory of the project.
        test_paths : list[str], optional
            Specific test file paths relative to working_dir.
            Defaults to discovering all tests in 'tests/'.
        """
        settings = get_settings()

        if test_paths:
            cmd = ["python", "-m", "pytest", *test_paths, "-v", "--tb=short"]
        else:
            cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]

        logger.info("ExecutionRunner: pytest on %s", working_dir)
        return await self._sandbox.run(
            working_dir=working_dir,
            command=cmd,
            timeout_seconds=settings.execution_timeout_seconds,
        )

    async def run_python(
        self,
        working_dir: Path,
        entry_point: str = "main.py",
    ) -> RawExecutionResult:
        """Run a Python entry point (non-test)."""
        settings = get_settings()
        cmd = ["python", entry_point]
        logger.info("ExecutionRunner: python %s in %s", entry_point, working_dir)
        return await self._sandbox.run(
            working_dir=working_dir,
            command=cmd,
            timeout_seconds=settings.execution_timeout_seconds,
        )
