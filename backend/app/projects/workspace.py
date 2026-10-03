"""Workspace helpers — manage on-disk layout of a project."""
from __future__ import annotations

import shutil
from pathlib import Path


class ProjectWorkspace:
    """
    Represents the on-disk layout for a single debugging project.

    workspaces/
      <project_id>/
        original/    ← immutable uploaded files
        working/     ← mutable copy where AI fixes are applied
        metadata.json
    """

    def __init__(self, base_dir: Path, project_id: str) -> None:
        self.project_id = project_id
        self.root = base_dir / project_id
        self.original = self.root / "original"
        self.working = self.root / "working"
        self.metadata_path = self.root / "metadata.json"
        self.result_path = self.root / "result.json"

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def create(self) -> None:
        """Create workspace directories on disk."""
        self.original.mkdir(parents=True, exist_ok=True)
        self.working.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self.root.exists()

    # ── File helpers ──────────────────────────────────────────────────────────

    def write_original(self, relative_path: str, content: bytes) -> Path:
        """Write a file into the immutable original/ directory."""
        target = self.original / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def read_original(self, relative_path: str) -> bytes:
        return (self.original / relative_path).read_bytes()

    def write_working(self, relative_path: str, content: bytes) -> Path:
        """Write a file into the mutable working/ directory."""
        target = self.working / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def reset_working(self) -> None:
        """Reset working/ to a clean copy of original/."""
        if self.working.exists():
            shutil.rmtree(self.working)
        shutil.copytree(self.original, self.working)

    def list_original_files(self) -> list[str]:
        """Return relative file paths inside original/."""
        return [
            str(p.relative_to(self.original))
            for p in self.original.rglob("*")
            if p.is_file()
        ]

    def list_working_files(self) -> list[str]:
        """Return relative file paths inside working/."""
        return [
            str(p.relative_to(self.working))
            for p in self.working.rglob("*")
            if p.is_file()
        ]
