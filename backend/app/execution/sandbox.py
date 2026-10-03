"""
Docker sandbox — isolated execution environment for untrusted code.

SECURITY PRINCIPLES:
- Never execute code inside the FastAPI process.
- No network access in the container.
- CPU and memory limits enforced.
- No access to host .env or secrets.
- Container is always destroyed after execution.
"""
from __future__ import annotations

import asyncio
import logging
import shlex
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from app.config.settings import get_settings
from app.core.errors import ErrorCode, PyDebugHTTPException

logger = logging.getLogger(__name__)


@dataclass
class RawExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool = False
    error: str = ""


class DockerSandbox:
    """
    Runs code in an isolated Docker container.

    Uses `docker run --rm` with:
      - read-only bind mount of the working directory
      - no network
      - CPU and memory limits
      - configurable timeout
    """

    async def run(
        self,
        working_dir: Path,
        command: list[str],
        timeout_seconds: int | None = None,
    ) -> RawExecutionResult:
        """
        Execute `command` inside a Docker container with `working_dir` mounted.

        Parameters
        ----------
        working_dir : Path
            The project directory to mount into /workspace.
        command : list[str]
            Command to run inside the container, e.g. ["pytest", "tests/", "-v"].
        timeout_seconds : int, optional
            Override the default execution timeout.
        """
        settings = get_settings()
        timeout = timeout_seconds or settings.execution_timeout_seconds

        docker_cmd = self._build_docker_command(
            working_dir=working_dir,
            command=command,
            settings=settings,
        )

        logger.info(
            "Sandbox: running %s in container (timeout=%ds)",
            " ".join(shlex.quote(c) for c in command),
            timeout,
        )

        start = time.monotonic()
        try:
            proc = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=float(timeout),
                )
                timed_out = False
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                timed_out = True
                stdout_bytes, stderr_bytes = b"", b"(execution timed out)"

        except FileNotFoundError as exc:
            raise PyDebugHTTPException(
                status_code=500,
                code=ErrorCode.SANDBOX_ERROR,
                message="Docker is not available. Ensure Docker is installed and running.",
            ) from exc
        except Exception as exc:
            logger.error("Sandbox execution error: %s", exc, exc_info=True)
            raise PyDebugHTTPException(
                status_code=500,
                code=ErrorCode.SANDBOX_ERROR,
                message=f"Sandbox execution failed: {exc}",
            ) from exc

        elapsed_ms = int((time.monotonic() - start) * 1000)

        result = RawExecutionResult(
            exit_code=proc.returncode if not timed_out else -1,
            stdout=stdout_bytes.decode("utf-8", errors="replace"),
            stderr=stderr_bytes.decode("utf-8", errors="replace"),
            duration_ms=elapsed_ms,
            timed_out=timed_out,
        )

        logger.info(
            "Sandbox finished: exit_code=%s  duration=%dms  timed_out=%s",
            result.exit_code, result.duration_ms, result.timed_out,
        )
        return result

    @staticmethod
    def _build_docker_command(
        working_dir: Path,
        command: list[str],
        settings,
    ) -> list[str]:
        """Build the full `docker run` command with all security flags."""
        return [
            "docker", "run",
            "--rm",
            "--network=none",
            f"--memory={settings.sandbox_memory_limit}",
            f"--cpu-quota={settings.sandbox_cpu_quota}",
            "--read-only",
            "--tmpfs=/tmp:rw,size=64m",
            "--tmpfs=/root:rw,size=16m",
            "--security-opt=no-new-privileges",
            "-v", f"{working_dir.resolve()}:/workspace:ro",
            "-w", "/workspace",
            settings.sandbox_image,
            *command,
        ]
