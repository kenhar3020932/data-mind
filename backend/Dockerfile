"""Multi-stage Dockerfile for DataMind-King backend.

Targets ≤450MB using python:3.12-slim → install deps → copy code → non-root user.
"""

# --- Build stage ---
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY backend/requirements/base.txt .
COPY backend/requirements/data.txt .
COPY backend/requirements/ml.txt .
COPY backend/requirements/viz_report.txt .
COPY backend/requirements/connectors.txt .

RUN pip install --no-cache-dir -r base.txt && \
    pip install --no-cache-dir -r data.txt && \
    pip install --no-cache-dir -r ml.txt && \
    pip install --no-cache-dir -r viz_report.txt && \
    pip install --no-cache-dir -r connectors.txt && \
    rm -rf ~/.cache

# --- Runtime stage ---
FROM python:3.12-slim AS runtime

RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -s /sbin/nologin appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY backend/app ./app
COPY backend/alembic.ini ./alembic.ini
COPY backend/alembic/ ./alembic/

ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app
ENV PATH="/app/scripts:${PATH}"

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
