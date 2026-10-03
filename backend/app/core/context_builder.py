"""
Context Builder — transforms uploaded files + traceback into a
structured text context suitable for Gemini prompts.

Designed as an abstraction: future versions can do smarter selection
(traceback analysis → relevant files only), but the interface stays stable.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Maximum total context characters to send to the LLM
MAX_CONTEXT_CHARS = 80_000


@dataclass
class ProjectContext:
    """Immutable context object passed to the LLM layer."""

    project_id: str
    traceback: str
    files: dict[str, str]          # relative_path -> source code
    structure_summary: str         # formatted file list
    full_context: str              # complete formatted context block

    # Optional enriched fields (populated by smarter future versions)
    primary_file: Optional[str] = None
    primary_function: Optional[str] = None


class ContextBuilder:
    """
    v1 strategy: include all uploaded .py files, no filtering.

    Design allows future strategies to be swapped in:
      - traceback → failing file → imports → related files
    """

    def build(
        self,
        project_id: str,
        files: dict[str, str],
        traceback: str,
    ) -> ProjectContext:
        """
        Build a ProjectContext from the raw project data.

        Parameters
        ----------
        project_id : str
        files : dict[str, str]
            {relative_path: source_code} for every uploaded file.
        traceback : str
            Raw Python traceback string.
        """
        if not files:
            raise ValueError("No Python files provided for context building.")
        if not traceback.strip():
            raise ValueError("Traceback cannot be empty.")

        structure_summary = self._build_structure(files)
        full_context = self._build_full_context(structure_summary, traceback, files)
        primary_file = self._infer_primary_file(traceback, files)

        logger.debug(
            "Context built for project %s: %d files, %d chars",
            project_id, len(files), len(full_context),
        )

        return ProjectContext(
            project_id=project_id,
            traceback=traceback,
            files=files,
            structure_summary=structure_summary,
            full_context=full_context,
            primary_file=primary_file,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _build_structure(files: dict[str, str]) -> str:
        lines = ["PROJECT STRUCTURE", "─" * 40]
        for path in sorted(files):
            lines.append(f"  {path}")
        return "\n".join(lines)

    @staticmethod
    def _build_full_context(
        structure_summary: str,
        traceback: str,
        files: dict[str, str],
    ) -> str:
        parts: list[str] = [structure_summary]

        parts.append("\n\nTRACEBACK\n" + "─" * 40)
        parts.append(traceback.strip())

        total_chars = sum(len(p) for p in parts)

        for path in sorted(files):
            source = files[path]
            header = f"\n\nFILE: {path}\n" + "─" * 40 + "\n"
            block = header + source
            if total_chars + len(block) > MAX_CONTEXT_CHARS:
                logger.warning(
                    "Context truncation: skipping '%s' (total chars would exceed %d)",
                    path, MAX_CONTEXT_CHARS,
                )
                parts.append(f"\n\n[FILE OMITTED DUE TO SIZE LIMIT: {path}]")
                continue
            parts.append(block)
            total_chars += len(block)

        return "\n".join(parts)

    @staticmethod
    def _infer_primary_file(traceback: str, files: dict[str, str]) -> Optional[str]:
        """Heuristic: find the last 'File "..." line in the traceback."""
        import re
        matches = re.findall(r'File "([^"]+)"', traceback)
        for candidate in reversed(matches):
            # strip leading ./ or path prefixes to match relative file keys
            for key in files:
                if candidate.endswith(key) or key.endswith(candidate.lstrip("./")):
                    return key
        return None
