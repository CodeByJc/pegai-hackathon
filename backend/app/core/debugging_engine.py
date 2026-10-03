"""
Debugging Engine — the central orchestrator.

Coordinates all pipeline stages:
  1. Context Building
  2. Diagnosis
  3. Hypothesis Generation
  4. Fix Generation
  5. Test Generation
  6. Fix Application
  7. Sandbox Execution
  8. Verification
  9. Retry Loop (up to MAX_REPAIR_ATTEMPTS)
 10. Final Report
"""
from __future__ import annotations

import json
import logging

from app.config.settings import get_settings
from app.core.context_builder import ContextBuilder
from app.core.errors import ErrorCode, PyDebugHTTPException
from app.core.fix_manager import FixManager
from app.core.hypothesis_engine import HypothesisEngine
from app.core.verification_engine import VerificationEngine
from app.execution.result_parser import ResultParser
from app.execution.runner import ExecutionRunner
from app.llm.service import LLMService
from app.models.diagnosis import (
    DebugReport,
    DiagnosisResult,
    FailureAnalysis,
    FixProposal,
    GeneratedTests,
    Hypothesis,
    VerificationResult,
)
from app.models.project import ProjectStatus
from app.projects.manager import ProjectManager
from app.prompts.diagnosis import get_diagnosis_prompts
from app.prompts.fix import get_fix_prompts
from app.prompts.retry import get_retry_prompts
from app.prompts.tests import get_test_prompts

logger = logging.getLogger(__name__)


class DebuggingEngine:
    """
    Orchestrates the full debugging pipeline for a given project.

    Call: await engine.debug(project_id) → DebugReport
    """

    def __init__(self) -> None:
        self._project_manager = ProjectManager()
        self._context_builder = ContextBuilder()
        self._llm = LLMService()
        self._hypothesis_engine = HypothesisEngine(self._llm)
        self._fix_manager = FixManager()
        self._runner = ExecutionRunner()
        self._result_parser = ResultParser()
        self._verification = VerificationEngine()

    # ── Main entry point ──────────────────────────────────────────────────────

    async def debug(self, project_id: str) -> DebugReport:
        settings = get_settings()
        pm = self._project_manager

        # ── Guard: project must exist with files + traceback ──────────────────
        try:
            meta = pm.get_project(project_id)
        except FileNotFoundError:
            raise PyDebugHTTPException(
                status_code=404,
                code=ErrorCode.PROJECT_NOT_FOUND,
                message=f"Project '{project_id}' not found.",
            )

        if not meta.files:
            raise PyDebugHTTPException(
                status_code=422,
                code=ErrorCode.FILES_REQUIRED,
                message="Upload Python files before starting diagnosis.",
            )
        if not meta.traceback:
            raise PyDebugHTTPException(
                status_code=422,
                code=ErrorCode.TRACEBACK_REQUIRED,
                message="Provide a traceback before starting diagnosis.",
            )

        pm.update_status(project_id, ProjectStatus.DIAGNOSING)
        report = DebugReport(project_id=project_id, status="pending")

        try:
            # ── Stage 1: Build context ────────────────────────────────────────
            files = pm.read_original_files(project_id)
            ctx = self._context_builder.build(
                project_id=project_id,
                files=files,
                traceback=meta.traceback,
            )
            logger.info("[%s] Context built — %d files", project_id, len(files))

            # ── Stage 2: Diagnosis ────────────────────────────────────────────
            logger.info("[%s] Stage 1: Diagnosis", project_id)
            diagnosis = await self._diagnose(ctx.full_context)
            report.diagnosis = diagnosis
            logger.info("[%s] Diagnosed: %s", project_id, diagnosis.error_type)

            # ── Stage 3: Hypothesis generation ───────────────────────────────
            logger.info("[%s] Stage 2: Hypothesis generation", project_id)
            hypotheses = await self._hypothesis_engine.generate(diagnosis, ctx.full_context)
            report.hypotheses = hypotheses

            # ── Iterate fix → execute → verify (with bounded retry) ───────────
            workspace = pm.get_workspace(project_id)
            pm.update_status(project_id, ProjectStatus.FIXING)

            fix: FixProposal | None = None
            verification: VerificationResult | None = None
            top_hypothesis = hypotheses[0] if hypotheses else None

            for attempt in range(1, settings.max_repair_attempts + 1):
                logger.info("[%s] Fix attempt %d/%d", project_id, attempt, settings.max_repair_attempts)

                # ── Stage 4: Fix generation ───────────────────────────────────
                if attempt == 1:
                    fix = await self._generate_fix(
                        context=ctx.full_context,
                        diagnosis=diagnosis,
                        hypothesis=top_hypothesis,
                    )
                else:
                    # Use retry prompt with actual execution results
                    fix = await self._retry_fix(
                        traceback=meta.traceback,
                        context=ctx.full_context,
                        hypothesis=top_hypothesis,
                        previous_fix=fix,
                        verification=verification,
                    )

                report.fix = fix

                # ── Stage 5: Test generation ──────────────────────────────────
                logger.info("[%s] Stage 5: Test generation", project_id)
                generated_tests = await self._generate_tests(
                    context=ctx.full_context,
                    root_cause=fix.root_cause,
                    fix_description=fix.description,
                )
                report.tests = generated_tests.tests

                # ── Stage 6: Apply fix ────────────────────────────────────────
                logger.info("[%s] Stage 6: Applying fix", project_id)
                self._fix_manager.apply_fix(workspace, fix, generated_tests.tests)

                # ── Stage 7: Execute ──────────────────────────────────────────
                pm.update_status(project_id, ProjectStatus.EXECUTING)
                logger.info("[%s] Stage 7: Sandbox execution", project_id)

                test_paths = [t.path for t in generated_tests.tests]
                raw_result = await self._runner.run_tests(
                    working_dir=workspace.working,
                    test_paths=test_paths or None,
                )

                # ── Stage 8: Verify ───────────────────────────────────────────
                verification = self._result_parser.parse(
                    raw_result, original_error_type=diagnosis.error_type
                )
                verification = self._verification.evaluate(verification)
                report.verification = verification
                report.repair_attempts = attempt

                if self._verification.is_verified(verification):
                    logger.info("[%s] VERIFIED on attempt %d", project_id, attempt)
                    report.status = "verified"
                    pm.update_status(project_id, ProjectStatus.VERIFIED)
                    break

                logger.warning(
                    "[%s] Attempt %d failed. status=%s",
                    project_id, attempt, verification.status,
                )

                if attempt == settings.max_repair_attempts:
                    report.status = "unverified"
                    pm.update_status(project_id, ProjectStatus.UNVERIFIED)
                    logger.error(
                        "[%s] All %d repair attempts exhausted.",
                        project_id, settings.max_repair_attempts,
                    )

        except PyDebugHTTPException:
            report.status = "error"
            pm.update_status(project_id, ProjectStatus.ERROR)
            raise

        except Exception as exc:
            report.status = "error"
            pm.update_status(project_id, ProjectStatus.ERROR)
            logger.error("[%s] Unexpected error: %s", project_id, exc, exc_info=True)
            raise PyDebugHTTPException(
                status_code=500,
                code=ErrorCode.INTERNAL_ERROR,
                message="An unexpected error occurred during debugging.",
            ) from exc

        # ── Persist final report ──────────────────────────────────────────────
        pm.save_result(project_id, report.model_dump_json(indent=2))
        logger.info("[%s] Debug pipeline complete. status=%s", project_id, report.status)
        return report

    # ── Private stage helpers ─────────────────────────────────────────────────

    async def _diagnose(self, context: str) -> DiagnosisResult:
        system, user = get_diagnosis_prompts(context)
        response = await self._llm.generate(
            system_prompt=system,
            user_prompt=user,
            response_schema=DiagnosisResult,
        )
        return response.parsed  # type: ignore[return-value]

    async def _generate_fix(
        self,
        context: str,
        diagnosis: DiagnosisResult,
        hypothesis: Hypothesis | None,
    ) -> FixProposal:
        hypothesis_text = hypothesis.model_dump_json(indent=2) if hypothesis else "No hypothesis."
        system, user = get_fix_prompts(
            context=context,
            diagnosis=diagnosis.model_dump_json(indent=2),
            hypothesis=hypothesis_text,
        )
        response = await self._llm.generate(
            system_prompt=system,
            user_prompt=user,
            response_schema=FixProposal,
        )
        return response.parsed  # type: ignore[return-value]

    async def _generate_tests(
        self,
        context: str,
        root_cause: str,
        fix_description: str,
    ) -> GeneratedTests:
        system, user = get_test_prompts(
            context=context,
            root_cause=root_cause,
            fix_description=fix_description,
        )
        response = await self._llm.generate(
            system_prompt=system,
            user_prompt=user,
            response_schema=GeneratedTests,
        )
        return response.parsed  # type: ignore[return-value]

    async def _retry_fix(
        self,
        traceback: str,
        context: str,
        hypothesis: Hypothesis | None,
        previous_fix: FixProposal | None,
        verification: VerificationResult | None,
    ) -> FixProposal:
        hypothesis_text = hypothesis.model_dump_json(indent=2) if hypothesis else "No hypothesis."
        previous_fix_text = previous_fix.description if previous_fix else "No previous fix."
        v = verification

        system, user = get_retry_prompts(
            traceback=traceback,
            context=context,
            hypothesis=hypothesis_text,
            previous_fix=previous_fix_text,
            exit_code=v.exit_code if v else -1,
            stdout=(v.stdout[:4000] if v else ""),
            stderr=(v.stderr[:4000] if v else ""),
            failed_tests=f"{v.failed} tests failed" if v else "",
        )
        response = await self._llm.generate(
            system_prompt=system,
            user_prompt=user,
            response_schema=FailureAnalysis,
        )
        analysis: FailureAnalysis = response.parsed  # type: ignore[assignment]
        return analysis.revised_fix
