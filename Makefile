# Makefile for Semantic Search Notes

.PHONY: help install install-dev test lint format clean index serve build

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package for production use
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=src/semantic_notes --cov-report=html --cov-report=term

lint:  ## Run linting tools
	flake8 src/
	mypy src/

format:  ## Format code
	black src/ tests/
	isort src/ tests/

format-check:  ## Check code formatting without making changes
	black --check src/ tests/
	isort --check-only src/ tests/

clean:  ## Clean up build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

index:  ## Index notes (requires NOTES_DIR or --notes-dir)
	semantic-notes-index

reindex:  ## Reindex all notes (deletes existing collection)
	semantic-notes-index --reindex

serve:  ## Start development server
	semantic-notes-serve --debug

serve-prod:  ## Start production server with Gunicorn
	gunicorn -c deployment/gunicorn.conf.py semantic_notes.api:create_app

build:  ## Build package for distribution
	python -m build

check:  ## Run all quality checks
	make format-check
	make lint
	make test

setup-dev:  ## Full development environment setup
	make install-dev
	pre-commit install
	@echo "Development environment ready!"

# Docker commands
docker-build:  ## Build Docker image
	docker build -t semantic-search-notes .

docker-run:  ## Run Docker container
	docker run -d -p 5000:5000 \
		-v $(PWD)/notes:/app/notes \
		-e NOTES_DIR=/app/notes \
		semantic-search-notes