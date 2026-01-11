# Infrastructure Overview

This document describes the production infrastructure for the Claude Plugin Pack Hub.

## Production Environment

### Railway Deployment

The application is deployed on [Railway](https://railway.app) with the following services:

| Service | Purpose | URL |
|---------|---------|-----|
| **plugpack-api** | FastAPI application | https://plugpack-api-production.up.railway.app |
| **Postgres** | PostgreSQL 16 database | Internal: `postgres.railway.internal:5432` |
| **Redis** | Redis 7 cache/rate limiting | Internal: `redis.railway.internal:6379` |

### API Endpoints

The production API is available at `https://plugpack-api-production.up.railway.app`:

```bash
# Health check
curl https://plugpack-api-production.up.railway.app/health

# List plugins
curl https://plugpack-api-production.up.railway.app/api/plugins/

# Search
curl "https://plugpack-api-production.up.railway.app/api/search/?q=docker"
```

## Database

### Schema

The database includes the following tables:

- **plugins** - Plugin metadata, GitHub stats, quality signals
- **packs** - Curated plugin collections
- **pack_plugins** - Many-to-many relationship for pack contents
- **users** - GitHub OAuth users (future)
- **reviews** - User reviews (future)

### Migrations

Migrations are managed with Alembic and run automatically on deployment:

```bash
# Generate new migration
make db-migration msg="description"

# Run migrations locally
make db-migrate

# Migrations run automatically on Railway deploy via railway.json startCommand
```

## Environment Variables

### Required for Production

| Variable | Description | Source |
|----------|-------------|--------|
| `DATABASE_URL` | PostgreSQL connection | Auto-set by Railway |
| `REDIS_URL` | Redis connection | Auto-set by Railway |
| `APP_ENV` | Must be `production` | Set manually |
| `APP_SECRET_KEY` | 32+ char secret | Generate with `openssl rand -hex 32` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub API token for scraper | None (uses unauthenticated rate limits) |
| `MEILISEARCH_URL` | Meilisearch search engine | Falls back to database search |
| `MEILISEARCH_API_KEY` | Meilisearch API key | Required if URL set |

## Deployment

### Automatic Deployment

Push to `main` branch triggers:
1. GitHub Actions CI (lint, typecheck, test, build)
2. Railway deployment via `RAILWAY_TOKEN` secret

### Manual Deployment

```bash
# Deploy current branch
railway up

# Check deployment status
railway service status --all

# View logs
railway logs
```

### Deployment Configuration

The `railway.json` file configures:
- Docker build using `Dockerfile`
- Start command: `alembic upgrade head && uvicorn ...`
- Health check: `/health` endpoint with 120s timeout
- Restart policy: ON_FAILURE with 3 retries

## Local Development

### Prerequisites

- Docker Desktop (for PostgreSQL, Redis, Meilisearch)
- Python 3.11+
- uv (package manager)

### Setup

```bash
# Install dependencies
uv sync --group dev

# Copy environment template
cp .env.example .env

# Start local services
make docker-up

# Run migrations
make db-migrate

# Start development server
make dev
```

### Available Commands

```bash
make dev          # Start dev server at http://localhost:8000
make test         # Run tests
make validate     # Run lint + typecheck + tests
make scrape       # Fetch plugins from sources
make db-seed      # Seed database with scraped plugins
```

## Monitoring

### Health Checks

- **Endpoint**: `GET /health`
- **Response**: `{"status": "healthy", "version": "0.1.0"}`
- Railway auto-restarts on health check failure

### Logs

```bash
# View Railway logs
railway logs

# Or via make command
make deploy-logs
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Railway                             │
│  ┌─────────────────┐  ┌──────────┐  ┌──────────┐       │
│  │  plugpack-api   │  │ Postgres │  │  Redis   │       │
│  │  (FastAPI)      │──│  (DB)    │  │ (Cache)  │       │
│  │  Port: dynamic  │  │  :5432   │  │  :6379   │       │
│  └────────┬────────┘  └──────────┘  └──────────┘       │
│           │                                              │
│           │ /health                                      │
└───────────┼──────────────────────────────────────────────┘
            │
            ▼
    Public URL: https://plugpack-api-production.up.railway.app
```

## Security

- Non-root Docker user (`appuser`)
- CORS configured for allowed origins
- Rate limiting via SlowAPI + Redis
- Production secrets via Railway environment variables
- GitHub OAuth for user authentication (planned)
