# Multi-stage build for MeccaAI
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --no-dev

# Copy application code
COPY . .

# Install the package
RUN uv pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash meccaai
RUN chown -R meccaai:meccaai /app
USER meccaai

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "meccaai.apps.openai_app", "--chat"]