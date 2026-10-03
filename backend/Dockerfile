# PyDebug Backend Dockerfile
# Multi-stage: build → runtime (no dev dependencies in production image)

FROM python:3.12-slim AS base

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Dependencies layer ────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application layer ─────────────────────────────────────────────────────────
COPY app/ ./app/
COPY workspaces/ ./workspaces/ 2>/dev/null || true

# ── Runtime config ────────────────────────────────────────────────────────────
ENV WORKSPACES_DIR=/app/workspaces
ENV LOG_LEVEL=INFO

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
