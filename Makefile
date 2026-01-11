# ============================================================================
# Claude Plugin Pack Hub - Makefile
# ============================================================================
# Run 'make help' to see all available commands
#
# This Makefile is designed for autonomous development - Claude can run any
# of these commands to develop, test, and deploy the application.
# ============================================================================

.PHONY: help install dev test lint format typecheck check docker-up docker-down docker-logs db-migrate db-seed clean deploy deploy-logs deploy-status deploy-run deploy-migrate deploy-seed deploy-shell deploy-env deploy-env-set docker-build docker-run-local

# Use uv for package management
UV := uv
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
# Setup & Installation (using uv)
# =============================================================================

install: ## Install all dependencies using uv
	@echo "$(GREEN)Installing dependencies with uv...$(NC)"
	$(UV) sync
	@echo "$(GREEN)Installation complete!$(NC)"

setup: install docker-up db-migrate ## Full setup: install deps, start services, run migrations
	@echo "$(GREEN)Setup complete! Run 'make dev' to start the development server.$(NC)"

# =============================================================================
# Development
# =============================================================================

dev: ## Start development server with hot reload
	$(UV) run uvicorn plugpack.main:app --reload --host 0.0.0.0 --port 8000

run: ## Start production server
	$(UV) run uvicorn plugpack.main:app --host 0.0.0.0 --port 8000

shell: ## Open Python shell with app context
	$(UV) run python -i -c "from plugpack.main import app; print('App loaded. Use app to access FastAPI instance.')"

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run linter (ruff)
	$(UV) run ruff check src tests

lint-fix: ## Run linter and auto-fix issues
	$(UV) run ruff check --fix src tests

format: ## Format code with ruff
	$(UV) run ruff format src tests

format-check: ## Check code formatting
	$(UV) run ruff format --check src tests

typecheck: ## Run type checker (pyright)
	$(UV) run pyright src

check: lint format-check typecheck ## Run all code quality checks
	@echo "$(GREEN)All checks passed!$(NC)"

# =============================================================================
# Testing
# =============================================================================

test: ## Run tests
	$(UV) run pytest

test-fast: ## Run tests in parallel
	$(UV) run pytest -n auto

test-cov: ## Run tests with coverage report
	$(UV) run pytest --cov=src/plugpack --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode
	$(UV) run ptw -- -v

# =============================================================================
# Database
# =============================================================================

db-migrate: ## Run database migrations
	$(UV) run alembic upgrade head

db-migration: ## Create a new migration (usage: make db-migration msg="add users table")
	$(UV) run alembic revision --autogenerate -m "$(msg)"

db-rollback: ## Rollback last migration
	$(UV) run alembic downgrade -1

db-reset: ## Reset database (drop all and recreate)
	$(UV) run alembic downgrade base
	$(UV) run alembic upgrade head

db-seed: ## Seed database with sample data
	$(UV) run python -m plugpack.scripts.seed

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
	$(UV) run python -m plugpack.scraper.run

scrape-test: ## Test scraper on a single source
	$(UV) run python -m plugpack.scraper.test

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

# =============================================================================
# Deployment (Railway)
# =============================================================================

deploy: ## Deploy to Railway
	@echo "$(GREEN)Deploying to Railway...$(NC)"
	railway up

deploy-logs: ## View Railway deployment logs
	railway logs

deploy-status: ## Check Railway deployment status
	railway status

deploy-run: ## Run a command on Railway (usage: make deploy-run cmd="alembic upgrade head")
	railway run $(cmd)

deploy-migrate: ## Run migrations on Railway
	railway run alembic upgrade head

deploy-seed: ## Seed production database
	railway run python -m plugpack.scripts.seed

deploy-shell: ## Open shell on Railway
	railway shell

deploy-env: ## List Railway environment variables
	railway variables

deploy-env-set: ## Set Railway env var (usage: make deploy-env-set key=GITHUB_TOKEN value=xxx)
	railway variables set $(key)=$(value)

# =============================================================================
# Docker Build (for testing production image locally)
# =============================================================================

docker-build: ## Build production Docker image
	docker build -t plugpack:latest .

docker-run-local: ## Run production image locally
	docker run -p 8000:8000 --env-file .env plugpack:latest
