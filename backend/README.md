# PyDebug — Python Debugging Assistant: Backend

A production-minded modular FastAPI backend for AI-powered Python debugging.

**Principle: Gemini proposes. The backend executes and verifies.**

---

## Architecture

```
Frontend (React/TS)
       │ REST/JSON
       ▼
FastAPI API Layer (thin routes)
       │
       ▼
Application / Service Layer
       │
       ├── ProjectManager      ← project lifecycle, file storage
       ├── DebuggingEngine     ← pipeline orchestrator
       │       │
       │       ├── ContextBuilder       ← multi-file context assembly
       │       ├── HypothesisEngine     ← ranked root-cause hypotheses
       │       ├── LLMService           ← provider-agnostic Gemini facade
       │       │       └── GeminiProvider
       │       ├── FixManager           ← applies fixes to working/ only
       │       ├── ExecutionRunner      ← delegates to DockerSandbox
       │       │       └── DockerSandbox
       │       ├── ResultParser         ← parses real execution output
       │       └── VerificationEngine   ← determines VERIFIED/FAILED/etc.
       │
       └── Evaluator           ← independent evaluation framework
```

---

## Debugging Pipeline

| Stage | Name | Description |
|-------|------|-------------|
| 1 | Context Build | Assembles all .py files + traceback into structured context |
| 2 | Diagnosis | Gemini identifies error type, location, root cause |
| 3 | Hypotheses | Gemini generates 2-4 ranked evidence-based hypotheses |
| 4 | Fix Generation | Gemini proposes minimal fix (full file content) |
| 5 | Test Generation | Gemini writes regression pytest tests |
| 6 | Fix Application | Backend applies fix to `working/` only |
| 7 | Sandbox Execution | Docker runs pytest in isolated container |
| 8 | Verification | VerificationEngine evaluates real results |
| 9 | Retry Loop | If failed: provide actual output to Gemini, retry up to 3× |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                   # FastAPI application
│   ├── api/
│   │   ├── health.py
│   │   ├── projects.py
│   │   ├── diagnosis.py
│   │   └── verification.py
│   ├── core/
│   │   ├── debugging_engine.py   # Pipeline orchestrator
│   │   ├── context_builder.py
│   │   ├── hypothesis_engine.py
│   │   ├── fix_manager.py
│   │   └── verification_engine.py
│   ├── projects/
│   │   ├── manager.py
│   │   ├── validator.py
│   │   └── workspace.py
│   ├── llm/
│   │   ├── service.py            # Provider-agnostic facade
│   │   ├── gemini_provider.py
│   │   └── schemas.py
│   ├── prompts/
│   │   ├── diagnosis.py
│   │   ├── hypotheses.py
│   │   ├── fix.py
│   │   ├── tests.py
│   │   ├── retry.py
│   │   └── report.py
│   ├── execution/
│   │   ├── sandbox.py            # Docker sandbox
│   │   ├── runner.py
│   │   └── result_parser.py
│   ├── evaluation/
│   │   ├── evaluator.py
│   │   └── metrics.py
│   ├── models/
│   │   ├── project.py
│   │   ├── diagnosis.py
│   │   └── verification.py
│   └── config/
│       └── settings.py
├── tests/
│   ├── test_file_validation.py
│   ├── test_project_manager.py
│   ├── test_context_builder.py
│   ├── test_schemas.py
│   ├── test_fix_manager.py
│   ├── test_verification.py
│   └── test_api.py
├── evaluation/
│   ├── cases/          # 10 labelled test cases
│   └── results/        # timestamped evaluation reports
├── prompts_history/
│   └── PROMPT_HISTORY.md
├── workspaces/         # project workspaces (gitignored)
├── requirements.txt
├── .env.example
├── pytest.ini
├── Dockerfile
└── docker-compose.yml
```

---

## Quick Start

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set GEMINI_API_KEY

# 4. Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Run tests
pytest
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/{id}` | Get project metadata |
| POST | `/api/projects/{id}/files` | Upload .py files |
| POST | `/api/projects/{id}/traceback` | Set traceback |
| POST | `/api/projects/{id}/diagnose` | Run full debug pipeline |
| GET | `/api/projects/{id}/result` | Get latest result |
| POST | `/api/projects/{id}/verify` | Re-run verification |

---

## Frontend API Contract

```json
{
  "project_id": "project_abc123",
  "status": "verified",
  "repair_attempts": 1,
  "diagnosis": {
    "error_type": "KeyError",
    "error_message": "'divisor'",
    "location": { "file": "calculator.py", "line": 12, "function": "run" },
    "root_cause": "Config defines 'division' but code accesses 'divisor'",
    "summary": "A KeyError is raised due to a key name mismatch."
  },
  "hypotheses": [
    {
      "rank": 1,
      "title": "Configuration key mismatch",
      "confidence": "high",
      "evidence": ["config.py line 1: key='division'", "calculator.py line 5: access='divisor'"],
      "affected_files": ["config.py", "calculator.py"]
    }
  ],
  "fix": {
    "root_cause": "Key name mismatch",
    "description": "Rename 'division' to 'divisor' in config.py",
    "files_to_modify": [
      { "path": "config.py", "description": "Rename key", "patch": "config = {'divisor': 2}" }
    ]
  },
  "tests": [
    { "path": "tests/test_calculator.py", "content": "def test_run_with_valid_divisor():..." }
  ],
  "verification": {
    "status": "verified",
    "exit_code": 0,
    "tests_run": 3,
    "passed": 3,
    "failed": 0,
    "duration_ms": 412,
    "original_error_absent": true
  }
}
```

---

## Security

- All uploaded files validated server-side (extension, path traversal, size)
- User code **never** executed in the FastAPI process
- Docker sandbox: `--network=none`, memory/CPU limits, read-only mounts
- AI-proposed file paths validated before write
- `.env` / `GEMINI_API_KEY` never exposed to sandbox containers

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | _(required)_ | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Model name |
| `GEMINI_TEMPERATURE` | `0.2` | Generation temperature |
| `MAX_REPAIR_ATTEMPTS` | `3` | Max fix retries |
| `EXECUTION_TIMEOUT_SECONDS` | `30` | Sandbox timeout |
| `SANDBOX_MEMORY_LIMIT` | `256m` | Container memory limit |
| `SANDBOX_IMAGE` | `python:3.12-slim` | Execution container image |
| `PROMPT_STRATEGY` | `structured` | `basic` or `structured` |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Prompt Strategies

Two strategies for evaluation comparison:

| Strategy | Description |
|----------|-------------|
| `basic` | Direct instruction prompts |
| `structured` | Decomposition + few-shot examples + strict schema constraints |

Set via `PROMPT_STRATEGY` environment variable.
