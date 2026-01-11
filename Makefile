# ============================================================================
# Claude Plugin Pack Hub - Makefile
# ============================================================================
# Run 'make help' to see all available commands
#
# This Makefile is designed for autonomous development - Claude can run any
# of these commands to develop, test, and deploy the application.
# ============================================================================

.PHONY: help install dev test lint format typecheck check docker-up docker-down docker-logs db-migrate db-seed clean

# Default Python
PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "Claude Plugin Pack Hub - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# Setup & Installation
# =============================================================================

install: ## Create venv and install all dependencies
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Installing dependencies...$(NC)"
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[dev]"
	@echo "$(GREEN)Installation complete!$(NC)"

setup: install docker-up db-migrate ## Full setup: install deps, start services, run migrations
	@echo "$(GREEN)Setup complete! Run 'make dev' to start the development server.$(NC)"

# =============================================================================
# Development
# =============================================================================

dev: ## Start development server with hot reload
	$(BIN)/uvicorn plugpack.main:app --reload --host 0.0.0.0 --port 8000

run: ## Start production server
	$(BIN)/uvicorn plugpack.main:app --host 0.0.0.0 --port 8000

shell: ## Open Python shell with app context
	$(BIN)/python -i -c "from plugpack.main import app; print('App loaded. Use app to access FastAPI instance.')"

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run linter (ruff)
	$(BIN)/ruff check src tests

lint-fix: ## Run linter and auto-fix issues
	$(BIN)/ruff check --fix src tests

format: ## Format code with ruff
	$(BIN)/ruff format src tests

format-check: ## Check code formatting
	$(BIN)/ruff format --check src tests

typecheck: ## Run type checker (pyright)
	$(BIN)/pyright src

check: lint format-check typecheck ## Run all code quality checks
	@echo "$(GREEN)All checks passed!$(NC)"

# =============================================================================
# Testing
# =============================================================================

test: ## Run tests
	$(BIN)/pytest

test-fast: ## Run tests in parallel
	$(BIN)/pytest -n auto

test-cov: ## Run tests with coverage report
	$(BIN)/pytest --cov=src/plugpack --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode
	$(BIN)/ptw -- -v

# =============================================================================
# Database
# =============================================================================

db-migrate: ## Run database migrations
	$(BIN)/alembic upgrade head

db-migration: ## Create a new migration (usage: make db-migration msg="add users table")
	$(BIN)/alembic revision --autogenerate -m "$(msg)"

db-rollback: ## Rollback last migration
	$(BIN)/alembic downgrade -1

db-reset: ## Reset database (drop all and recreate)
	$(BIN)/alembic downgrade base
	$(BIN)/alembic upgrade head

db-seed: ## Seed database with sample data
	$(BIN)/python -m plugpack.scripts.seed

db-shell: ## Open psql shell
	docker exec -it plugpack-postgres psql -U plugpack -d plugpack

# =============================================================================
# Docker Services
# =============================================================================

docker-up: ## Start Docker services (PostgreSQL, Redis, Meilisearch)
	docker compose up -d
	@echo "$(GREEN)Waiting for services to be healthy...$(NC)"
	@sleep 5
	@docker compose ps

docker-down: ## Stop Docker services
	docker compose down

docker-logs: ## View Docker service logs
	docker compose logs -f

docker-reset: ## Reset Docker services (removes volumes)
	docker compose down -v
	docker compose up -d

docker-status: ## Show Docker service status
	docker compose ps

# =============================================================================
# Scraper
# =============================================================================

scrape: ## Run the plugin scraper
	$(BIN)/python -m plugpack.scraper.run

scrape-test: ## Test scraper on a single source
	$(BIN)/python -m plugpack.scraper.test

# =============================================================================
# Utilities
# =============================================================================

clean: ## Remove build artifacts and cache files
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

validate: check test ## Run all validations (lint, format, typecheck, tests)
	@echo "$(GREEN)All validations passed!$(NC)"

ci: validate ## Run CI pipeline locally
	@echo "$(GREEN)CI pipeline passed!$(NC)"
