# ==============================================================================
# AnumatiSetu - Production Dockerfile
# Multi-stage optimized production image with non-root security context
# ==============================================================================

FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies for compiling database drivers
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create isolated virtual environment in /opt/venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final runtime image
FROM python:3.12-slim AS runner

WORKDIR /app

# Install runtime dependencies for PostgreSQL, MySQL client and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    default-mysql-client \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed virtual environment from builder (accessible by non-root users)
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Create an unprivileged user and directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R appuser:appuser /app

# Copy application source code
COPY --chown=appuser:appuser . /app

# Switch to non-root user
USER appuser

# Pre-collect static files for WhiteNoise into staticfiles directory
RUN python manage.py collectstatic --noinput --clear

# Health check using the /health/ endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health/ || exit 1

EXPOSE 8000

# Apply migrations if database is accessible, then start Gunicorn server
CMD ["sh", "-c", "python manage.py migrate --noinput; gunicorn config.wsgi:application -c gunicorn.conf.py"]

