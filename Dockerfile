FROM python:3.11-slim

LABEL maintainer="MiniRack Team"
LABEL description="MiniRack AI Lab Management Portal"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml requirements.txt* ./
COPY minirack_ai_lab_management/ ./minirack_ai_lab_management/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/health', timeout=5)" || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "minirack_ai_lab_management.main:app", \
     "--host", "0.0.0.0", "--port", "8080"]
