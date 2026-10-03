"""Project Manager — single source of truth for project lifecycle."""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from app.config.settings import get_settings
from app.models.project import (
    ProjectMetadata,
    ProjectStatus,
    UploadedFile,
)
from app.projects.workspace import ProjectWorkspace

logger = logging.getLogger(__name__)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ProjectManager:
    """
    Manages project creation, metadata persistence, file storage,
    and workspace management. Does NOT contain AI or execution logic.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._base: Path = settings.workspaces_dir.resolve()
        self._base.mkdir(parents=True, exist_ok=True)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _workspace(self, project_id: str) -> ProjectWorkspace:
        return ProjectWorkspace(self._base, project_id)

    def _meta_path(self, project_id: str) -> Path:
        return self._base / project_id / "metadata.json"

    def _save_metadata(self, meta: ProjectMetadata) -> None:
        path = self._meta_path(meta.project_id)
        path.write_text(meta.model_dump_json(indent=2), encoding="utf-8")

    def _load_metadata(self, project_id: str) -> ProjectMetadata:
        path = self._meta_path(project_id)
        if not path.exists():
            raise FileNotFoundError(project_id)
        raw = path.read_text(encoding="utf-8")
        return ProjectMetadata.model_validate_json(raw)

    # ── Public API ────────────────────────────────────────────────────────────

    def create_project(self) -> ProjectMetadata:
        """Create a new project workspace and persist metadata."""
        project_id = f"project_{uuid.uuid4().hex[:12]}"
        ws = self._workspace(project_id)
        ws.create()

        meta = ProjectMetadata(
            project_id=project_id,
            status=ProjectStatus.CREATED,
        )
        self._save_metadata(meta)
        logger.info("Project created: %s", project_id)
        return meta

    def get_project(self, project_id: str) -> ProjectMetadata:
        """Load and return project metadata. Raises FileNotFoundError if absent."""
        return self._load_metadata(project_id)

    def project_exists(self, project_id: str) -> bool:
        return self._meta_path(project_id).exists()

    def add_file(
        self,
        project_id: str,
        filename: str,
        content: bytes,
    ) -> ProjectMetadata:
        """
        Store a validated Python file in the project's original/ workspace
        and update metadata. Caller is responsible for validation.
        """
        meta = self._load_metadata(project_id)
        ws = self._workspace(project_id)

        ws.write_original(filename, content)

        # Replace or append file record
        new_entry = UploadedFile(
            path=filename,
            size_bytes=len(content),
            sha256=_sha256(content),
        )
        meta.files = [f for f in meta.files if f.path != filename]
        meta.files.append(new_entry)
        meta.status = ProjectStatus.FILES_UPLOADED
        meta.touch()
        self._save_metadata(meta)
        logger.info("File '%s' added to project %s", filename, project_id)
        return meta

    def set_traceback(self, project_id: str, traceback: str) -> ProjectMetadata:
        """Store / update the traceback for a project."""
        meta = self._load_metadata(project_id)
        if not meta.files:
            from app.core.errors import ErrorCode, PyDebugHTTPException
            raise PyDebugHTTPException(
                status_code=422,
                code=ErrorCode.FILES_REQUIRED,
                message="Upload Python files before setting a traceback.",
            )
        meta.traceback = traceback.strip()
        meta.status = ProjectStatus.TRACEBACK_SET
        meta.touch()
        self._save_metadata(meta)
        logger.info("Traceback set for project %s", project_id)
        return meta

    def update_status(self, project_id: str, status: ProjectStatus) -> None:
        meta = self._load_metadata(project_id)
        meta.status = status
        meta.touch()
        self._save_metadata(meta)

    def get_workspace(self, project_id: str) -> ProjectWorkspace:
        return self._workspace(project_id)

    def read_original_files(self, project_id: str) -> dict[str, str]:
        """
        Return a mapping of relative_path -> decoded source text for all
        files in the original/ workspace.
        """
        meta = self._load_metadata(project_id)
        ws = self._workspace(project_id)
        result: dict[str, str] = {}
        for f in meta.files:
            raw = ws.read_original(f.path)
            result[f.path] = raw.decode("utf-8", errors="replace")
        return result

    def save_result(self, project_id: str, report_json: str) -> None:
        """Persist the final debug report JSON next to the workspace."""
        ws = self._workspace(project_id)
        ws.result_path.write_text(report_json, encoding="utf-8")
        meta = self._load_metadata(project_id)
        meta.result_path = str(ws.result_path)
        meta.touch()
        self._save_metadata(meta)

    def get_result(self, project_id: str) -> str | None:
        """Return the final report JSON if it exists, else None."""
        ws = self._workspace(project_id)
        if ws.result_path.exists():
            return ws.result_path.read_text(encoding="utf-8")
        return None

    def list_projects(self) -> list[ProjectMetadata]:
        """Return metadata for all known projects (sorted newest first)."""
        projects: list[ProjectMetadata] = []
        for path in sorted(self._base.iterdir(), reverse=True):
            meta_file = path / "metadata.json"
            if meta_file.exists():
                try:
                    projects.append(ProjectMetadata.model_validate_json(meta_file.read_text()))
                except Exception:  # noqa: BLE001
                    pass
        return projects
