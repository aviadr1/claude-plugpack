# Ticket #001: Infrastructure Setup & External Services Configuration

**Status:** In Progress
**Priority:** Critical
**Type:** Infrastructure
**Branch:** `feature/infrastructure-setup`

---

## Summary

Configure all external tools and services required to get Claude Plugin Pack Hub operational for both local development and production deployment.

## Background

The codebase is well-structured with FastAPI, SQLModel, and full tooling, but critical infrastructure pieces are missing:

- No `.env` file (only `.env.example` exists)
- No database migrations generated (`alembic/versions/` is empty)
- Docker services not accessible in WSL2
- Railway CLI not installed
- No GitHub tokens configured for scraper/OAuth

## Current State

| Component | Status | Blocker |
|-----------|--------|---------|
| GitHub CLI (`gh`) | Authenticated as `aviadr1` | None |
| Railway CLI | Not installed | Blocks deployment |
| Docker | WSL2 integration disabled | Blocks local dev |
| `.env` file | Missing | Blocks local dev |
| Database migrations | Empty | Blocks deployment |
| GitHub Secrets | Only `RAILWAY_TOKEN` exists | Partial |

## Scope

### In Scope

1. **Local Environment Setup**
   - Create `.env` from `.env.example`
   - Enable Docker Desktop WSL2 integration
   - Start local services (Postgres, Redis, Meilisearch)

2. **Database Setup**
   - Generate initial Alembic migration
   - Run migrations locally
   - Seed database with scraped plugins

3. **Railway Deployment Setup**
   - Install Railway CLI
   - Link project to Railway
   - Configure production environment variables
   - Deploy and verify

4. **GitHub Integration**
   - Create GitHub Personal Access Token for scraper
   - (Future) Create GitHub OAuth App for user authentication

### Out of Scope

- Implementing new features (authentication, reviews, etc.)
- Meilisearch Cloud setup (can use local for now)
- GitHub OAuth implementation (token creation only)

## Tasks

### Phase 1: Local Development Environment

- [ ] Create `.env` file from `.env.example`
- [ ] Verify Docker Desktop WSL2 integration status
- [ ] Start Docker services with `make docker-up`
- [ ] Verify all services healthy

### Phase 2: Database Bootstrap

- [ ] Generate initial migration: `make db-migration msg="initial_schema"`
- [ ] Run migration: `make db-migrate`
- [ ] Run scraper: `make scrape`
- [ ] Seed database: `make db-seed`
- [ ] Verify data: `curl localhost:8000/api/plugins/count`

### Phase 3: Code Validation

- [ ] Run full validation: `make validate`
- [ ] Fix any lint/type/test issues
- [ ] Commit migration files

### Phase 4: Railway Setup

- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Login to Railway: `railway login`
- [ ] Link project: `railway link`
- [ ] Verify PostgreSQL addon exists
- [ ] Verify Redis addon exists
- [ ] Set production environment variables
- [ ] Deploy: `make deploy`
- [ ] Run production migrations: `make deploy-migrate`
- [ ] Verify health: `curl <railway-url>/health`

### Phase 5: GitHub Token Setup

- [ ] Create GitHub PAT with `public_repo` scope
- [ ] Add to `.env` locally
- [ ] Add to Railway environment
- [ ] Test scraper with token: `make scrape`

## Acceptance Criteria

1. `make dev` starts server successfully at http://localhost:8000
2. `/api/plugins/count` returns non-zero count
3. `/api/search?q=claude` returns results
4. `make validate` passes with no errors
5. Railway deployment accessible at public URL
6. Production `/health` endpoint returns 200

## Technical Notes

### Environment Variables Required

```bash
# Local (.env)
DATABASE_URL=postgresql+asyncpg://plugpack:plugpack_dev_password@localhost:5432/plugpack
REDIS_URL=redis://localhost:6379/0
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=plugpack_meili_dev_key
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=dev-secret-key-change-in-production-must-be-32-chars
GITHUB_TOKEN=ghp_xxxxx  # For scraper

# Production (Railway)
DATABASE_URL=<auto-set by Railway PostgreSQL>
REDIS_URL=<auto-set by Railway Redis>
APP_ENV=production
APP_SECRET_KEY=<generate with: openssl rand -hex 32>
MEILISEARCH_URL=<meilisearch cloud or self-hosted>
MEILISEARCH_API_KEY=<meilisearch api key>
GITHUB_TOKEN=<github pat>
```

### Commands Reference

```bash
# Docker
make docker-up          # Start services
make docker-logs        # View logs
make docker-down        # Stop services

# Database
make db-migration msg="description"  # Create migration
make db-migrate         # Run migrations
make db-seed            # Seed data

# Validation
make validate           # Full validation (lint + typecheck + test)

# Deployment
make deploy             # Deploy to Railway
make deploy-migrate     # Run migrations on Railway
make deploy-logs        # View Railway logs
```

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Docker not available in WSL2 | High | Document manual Docker Desktop setup steps |
| Railway services not provisioned | High | Provide dashboard instructions |
| Scraper rate limited by GitHub | Medium | Add GITHUB_TOKEN to increase limits |

## Definition of Done

- [ ] All tasks completed
- [ ] Acceptance criteria met
- [ ] PR merged to main
- [ ] Production deployment verified
- [ ] Documentation updated if needed

---

**Created:** 2025-01-11
**Author:** Claude (automated infrastructure analysis)
