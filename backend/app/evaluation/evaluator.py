"""
Evaluation framework — independent from the user debugging workflow.

Runs labelled test cases through the debugging pipeline and measures:
- Diagnosis accuracy
- Fix verification rate
- Prompt strategy comparison
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

CASES_DIR = Path(__file__).parent.parent.parent / "evaluation" / "cases"
RESULTS_DIR = Path(__file__).parent.parent.parent / "evaluation" / "results"


@dataclass
class EvaluationCase:
    case_id: str
    files: dict[str, str]         # filename → source
    traceback: str
    expected_error_type: str
    expected_fix_verified: bool
    description: str = ""


@dataclass
class CaseResult:
    case_id: str
    strategy: str
    diagnosed_correctly: bool
    fix_verified: bool
    repair_attempts: int
    status: str
    notes: str = ""


@dataclass
class EvaluationReport:
    strategy: str
    total_cases: int
    correct_diagnoses: int
    verified_fixes: int
    results: list[CaseResult] = field(default_factory=list)

    @property
    def diagnosis_accuracy(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return self.correct_diagnoses / self.total_cases

    @property
    def fix_verification_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return self.verified_fixes / self.total_cases


class Evaluator:
    """
    Runs evaluation cases against the debugging pipeline.
    Used only for prompt strategy comparison and accuracy measurement.
    """

    def __init__(self, strategy: str = "structured") -> None:
        self._strategy = strategy
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def load_cases(self) -> list[EvaluationCase]:
        """Load all cases from evaluation/cases/."""
        cases: list[EvaluationCase] = []
        if not CASES_DIR.exists():
            logger.warning("No evaluation cases directory found at %s", CASES_DIR)
            return cases

        for case_dir in sorted(CASES_DIR.iterdir()):
            if not case_dir.is_dir():
                continue
            meta_file = case_dir / "case.json"
            if not meta_file.exists():
                continue
            try:
                meta = json.loads(meta_file.read_text())
                files: dict[str, str] = {}
                for fname in meta.get("files", []):
                    fpath = case_dir / fname
                    if fpath.exists():
                        files[fname] = fpath.read_text()
                traceback_file = case_dir / "traceback.txt"
                traceback = traceback_file.read_text() if traceback_file.exists() else ""
                cases.append(
                    EvaluationCase(
                        case_id=case_dir.name,
                        files=files,
                        traceback=traceback,
                        expected_error_type=meta.get("expected_error_type", ""),
                        expected_fix_verified=meta.get("expected_fix_verified", True),
                        description=meta.get("description", ""),
                    )
                )
            except Exception as exc:
                logger.error("Failed to load case %s: %s", case_dir.name, exc)

        logger.info("Loaded %d evaluation cases", len(cases))
        return cases

    async def run_case(
        self,
        case: EvaluationCase,
        project_manager,
        engine,
    ) -> CaseResult:
        """Run a single evaluation case through the debugging pipeline."""
        from app.models.project import ProjectStatus

        try:
            # Create project
            meta = project_manager.create_project()
            pid = meta.project_id

            # Upload files
            for filename, content in case.files.items():
                project_manager.add_file(pid, filename, content.encode())

            # Set traceback
            project_manager.set_traceback(pid, case.traceback)

            # Run pipeline
            report = await engine.debug(pid)

            diagnosed_correctly = (
                report.diagnosis is not None
                and report.diagnosis.error_type.lower()
                == case.expected_error_type.lower()
            )
            fix_verified = report.status == "verified"

            return CaseResult(
                case_id=case.case_id,
                strategy=self._strategy,
                diagnosed_correctly=diagnosed_correctly,
                fix_verified=fix_verified,
                repair_attempts=report.repair_attempts,
                status=report.status,
            )
        except Exception as exc:
            logger.error("Case %s failed: %s", case.case_id, exc, exc_info=True)
            return CaseResult(
                case_id=case.case_id,
                strategy=self._strategy,
                diagnosed_correctly=False,
                fix_verified=False,
                repair_attempts=0,
                status="error",
                notes=str(exc),
            )

    async def run_all(self, project_manager, engine) -> EvaluationReport:
        cases = self.load_cases()
        report = EvaluationReport(
            strategy=self._strategy,
            total_cases=len(cases),
            correct_diagnoses=0,
            verified_fixes=0,
        )

        for case in cases:
            result = await self.run_case(case, project_manager, engine)
            report.results.append(result)
            if result.diagnosed_correctly:
                report.correct_diagnoses += 1
            if result.fix_verified:
                report.verified_fixes += 1

        self._save_report(report)
        return report

    def _save_report(self, report: EvaluationReport) -> None:
        from datetime import datetime
        filename = f"eval_{report.strategy}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        path = RESULTS_DIR / filename
        data = {
            "strategy": report.strategy,
            "total_cases": report.total_cases,
            "correct_diagnoses": report.correct_diagnoses,
            "verified_fixes": report.verified_fixes,
            "diagnosis_accuracy": report.diagnosis_accuracy,
            "fix_verification_rate": report.fix_verification_rate,
            "results": [
                {
                    "case_id": r.case_id,
                    "diagnosed_correctly": r.diagnosed_correctly,
                    "fix_verified": r.fix_verified,
                    "repair_attempts": r.repair_attempts,
                    "status": r.status,
                    "notes": r.notes,
                }
                for r in report.results
            ],
        }
        path.write_text(json.dumps(data, indent=2))
        logger.info("Evaluation report saved to %s", path)
