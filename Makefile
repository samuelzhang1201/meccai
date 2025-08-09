.PHONY: install dev test lint format typecheck clean docker-build docker-run

# Development
install:
	uv sync

dev:
	uv sync --dev

# Testing
test:
	uv run pytest

test-cov:
	uv run pytest --cov=meccaai --cov-report=html --cov-report=term

# Code Quality
lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run pyright

check: format lint typecheck test

# Docker
docker-build:
	docker build -f docker/Dockerfile -t meccaai .

docker-run:
	docker run -p 8000:8000 --env-file .env meccaai

# Cleanup
clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/

# Pre-commit
pre-commit-install:
	uv run pre-commit install

pre-commit-run:
	uv run pre-commit run --all-files