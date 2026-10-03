"""
PyDebug Backend — FastAPI application entry point.

Architecture:
  API Layer (thin routes)
    ↓
  Service / Domain Layer (DebuggingEngine, ProjectManager, etc.)
    ↓
  Infrastructure (LLMService → GeminiProvider, ExecutionRunner → Docker)
"""
from __future__ import annotations

import contextlib
import logging
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import diagnosis, health, projects, verification
from app.config.settings import get_settings
from app.core.errors import PyDebugHTTPException

# ── Logging ───────────────────────────────────────────────────────────────────

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)

# ── Lifespan ──────────────────────────────────────────────────────────────────


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI lifespan handler."""
    logger.info("PyDebug backend starting up.")
    logger.info("Model: %s", settings.gemini_model)
    logger.info("Prompt strategy: %s", settings.prompt_strategy)
    logger.info("Workspaces dir: %s", settings.workspaces_dir.resolve())
    logger.info("Max repair attempts: %d", settings.max_repair_attempts)
    yield
    logger.info("PyDebug backend shutting down.")


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="PyDebug — Python Debugging Assistant",
    description=(
        "AI-powered Python debugging backend. "
        "Gemini proposes. The backend executes and verifies."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────


@app.exception_handler(PyDebugHTTPException)
async def pydebug_exception_handler(request: Request, exc: PyDebugHTTPException) -> JSONResponse:
    """Return structured JSON errors — never raw exception tracebacks."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    import traceback
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected server error occurred.",
                "traceback": traceback.format_exc()
            }
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────

PREFIX = settings.api_prefix  # /api

app.include_router(health.router, prefix=PREFIX)
app.include_router(projects.router, prefix=PREFIX)
app.include_router(diagnosis.router, prefix=PREFIX)
app.include_router(verification.router, prefix=PREFIX)
