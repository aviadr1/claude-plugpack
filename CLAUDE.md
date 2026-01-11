# CLAUDE.md - Autonomous Development Guide

> This file provides Claude with all the context needed to work autonomously on this project.

## Project Overview

**Claude Plugin Pack Hub** - The Ultimate Directory for Claude Code Extensions

A community-powered aggregator that solves plugin discovery through rich metadata, curated workflow packs, and smart recommendations. Think "Product Hunt for Claude Code plugins."

### Key Value Proposition
- **For Developers**: Find the perfect Claude Code plugins for your workflow in 5 minutes, not 5 hours
- **For Plugin Creators**: Get your plugins discovered by the right users
- **For the Ecosystem**: Accelerate Claude Code adoption by making customization accessible

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Package Mgmt | uv | Fast Python package manager |
| Framework | FastAPI | Async Python web framework |
| Database | PostgreSQL | Primary data store |
| ORM | SQLModel | SQLAlchemy + Pydantic combined |
| Migrations | Alembic | Database schema versioning |
| Cache | Redis | Caching and rate limiting |
| Search | Meilisearch | Fast, typo-tolerant search |
| Templates | Jinja2 + HTMX | Server-rendered UI with interactivity |
| Styling | Tailwind CSS (CDN) | Utility-first CSS |
| Testing | pytest + pytest-asyncio | Async test framework |
| Linting | ruff | Fast Python linter/formatter |
| Type Check | pyright | Static type checking |

## Quick Commands

All commands use `uv` for fast, reliable package management.

```bash
# SETUP (first time)
make install        # Install deps with uv sync
make setup          # Install deps, start Docker, run migrations

# DEVELOPMENT
make dev            # Start dev server at http://localhost:8000
make shell          # Open Python shell with app context

# CODE QUALITY
make lint           # Run linter (ruff)
make lint-fix       # Auto-fix lint issues
make format         # Format code (ruff)
make typecheck      # Run type checker (pyright)
make check          # Run all quality checks

# TESTING
make test           # Run tests
make test-cov       # Run tests with coverage
make test-fast      # Run tests in parallel

# DATABASE
make db-migrate     # Run migrations
make db-migration msg="description"  # Create new migration
make db-reset       # Reset database
make db-seed        # Seed with sample data

# DOCKER
make docker-up      # Start services (Postgres, Redis, Meilisearch)
make docker-down    # Stop services
make docker-logs    # View logs
make docker-reset   # Reset volumes and restart

# SCRAPING
make scrape         # Run plugin scraper (fetches from official store)

# FULL VALIDATION
make validate       # Run all checks + tests
make ci             # Simulate CI pipeline

# DEPLOYMENT
make deploy         # Deploy to Railway
make deploy-logs    # View production logs
```

## Project Structure

```
claude-plugpack/
├── src/plugpack/              # Main application code
│   ├── __init__.py            # Version info
│   ├── main.py                # FastAPI app entry point
│   ├── config.py              # Settings (Pydantic)
│   ├── database.py            # Database connection
│   ├── api/                   # API routes
│   │   ├── __init__.py        # Route aggregation
│   │   ├── plugins.py         # Plugin endpoints
│   │   ├── packs.py           # Pack endpoints
│   │   └── search.py          # Search endpoints
│   ├── models/                # SQLModel database models
│   │   └── __init__.py        # Plugin, Pack, Review, User
│   ├── scraper/               # Plugin data scraping
│   │   ├── sources.py         # Source configurations
│   │   ├── scraper.py         # Scraper implementation
│   │   └── run.py             # CLI entry point
│   ├── templates/             # Jinja2 templates
│   │   ├── base.html          # Base layout
│   │   └── pages/             # Page templates
│   └── static/                # Static assets
├── tests/                     # Test files
│   ├── conftest.py            # Fixtures
│   ├── test_health.py         # Health check tests
│   ├── test_api_plugins.py    # Plugin API tests
│   └── test_api_search.py     # Search API tests
├── alembic/                   # Database migrations
│   ├── env.py                 # Alembic environment
│   └── versions/              # Migration files
├── pyproject.toml             # Project config and dependencies
├── Makefile                   # Development commands
├── docker-compose.yml         # Local services
├── .env.example               # Environment template
└── CLAUDE.md                  # This file
```

## Core Models

### Plugin
The main entity representing a Claude Code plugin.

Key fields:
- `name`, `slug`: Identification
- `description`: What it does
- `category`: Auto-categorized (devops, testing, frontend, etc.)
- `repository_url`: GitHub/source URL
- `github_stars`, `maintenance_status`: Quality signals
- `is_verified`, `is_featured`: Curation flags

### Pack
A curated collection of plugins for a specific workflow.

Key fields:
- `name`, `slug`, `description`
- `phases`: Ordered plugin groups with instructions
- `difficulty`: beginner/intermediate/advanced
- `curator_name`: Who curated it

### Review
User reviews for plugins and packs.

Key fields:
- `rating`: 1-5 stars
- `body`, `pro_tip`, `gotcha`: Review content
- `frameworks_used`, `team_size`: Usage context

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/plugins/` | List plugins (supports filtering) |
| GET | `/api/plugins/{id}` | Get plugin by ID |
| GET | `/api/plugins/slug/{slug}` | Get plugin by slug |
| GET | `/api/plugins/categories` | List categories with counts |
| GET | `/api/packs/` | List published packs |
| GET | `/api/packs/{id}` | Get pack with plugins |
| GET | `/api/search/?q=` | Search plugins and packs |
| GET | `/health` | Health check |

## Development Workflow

### Adding a New Feature

1. **Create a branch** (if not already on feature branch)
2. **Write tests first** in `tests/`
3. **Implement the feature** in `src/plugpack/`
4. **Run validation**: `make validate`
5. **Commit with descriptive message**

### Adding a New API Endpoint

1. Create route in `src/plugpack/api/`
2. Add to router in `src/plugpack/api/__init__.py`
3. Write tests in `tests/test_api_*.py`
4. Run `make test`

### Adding a Database Model

1. Add model in `src/plugpack/models/__init__.py`
2. Create migration: `make db-migration msg="add_new_model"`
3. Run migration: `make db-migrate`
4. Update seeds if needed in `src/plugpack/scripts/seed.py`

### Adding a Template Page

1. Create template in `src/plugpack/templates/pages/`
2. Add route in `src/plugpack/main.py`
3. Test rendering: `make dev` and visit the page

## Testing Strategy

- **Unit tests**: For scraper logic, model validation
- **API tests**: For endpoint behavior
- **Integration tests**: Full stack with database

```bash
# Run specific test file
pytest tests/test_health.py -v

# Run tests matching pattern
pytest -k "plugin" -v

# Run with debug output
pytest -v --tb=long
```

## Common Tasks

### Scrape New Plugins

```bash
make scrape  # Fetches from configured sources
```

Sources are defined in `src/plugpack/scraper/sources.py`.

### Add a New Plugin Source

1. Add source to `PLUGIN_SOURCES` in `sources.py`
2. Test with `make scrape`

### Update Dependencies

```bash
# Edit pyproject.toml, then:
pip install -e ".[dev]"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | (see .env.example) |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 |
| `MEILISEARCH_URL` | Meilisearch URL | http://localhost:7700 |
| `MEILISEARCH_API_KEY` | Meilisearch API key | plugpack_meili_dev_key |
| `APP_ENV` | development/staging/production | development |
| `APP_DEBUG` | Enable debug mode | true |
| `GITHUB_TOKEN` | For scraping GitHub data | (optional) |

## Error Handling

- All API errors return JSON with `detail` field
- Use FastAPI's `HTTPException` for expected errors
- Log unexpected errors with `structlog`

## Deployment (Railway)

The app deploys to Railway for production. Claude can operate autonomously with a `RAILWAY_TOKEN`.

### Deployment Commands

```bash
# DEPLOY
make deploy              # Deploy to Railway
make deploy-status       # Check deployment status
make deploy-logs         # View production logs

# REMOTE OPERATIONS
make deploy-migrate      # Run migrations on Railway
make deploy-seed         # Seed production database
make deploy-shell        # Open shell on Railway

# ENVIRONMENT
make deploy-env          # List Railway environment variables
make deploy-env-set key=GITHUB_TOKEN value=xxx  # Set env var

# LOCAL DOCKER TEST
make docker-build        # Build production Docker image
make docker-run-local    # Test production image locally
```

### First-Time Railway Setup

1. **Install Railway CLI**: `npm install -g @railway/cli`
2. **Login**: `railway login` or `railway login --token $RAILWAY_TOKEN`
3. **Link project**: `railway link` (select or create project)
4. **Add PostgreSQL**: In Railway dashboard, add PostgreSQL service
5. **Add Redis**: In Railway dashboard, add Redis service
6. **Set environment variables**:
   ```bash
   railway variables set APP_ENV=production
   railway variables set MEILISEARCH_URL=https://your-meili-instance
   railway variables set MEILISEARCH_API_KEY=your-key
   ```
7. **Deploy**: `make deploy`
8. **Run migrations**: `make deploy-migrate`
9. **Seed data**: `make deploy-seed`

### Autonomous Deployment Workflow

When Claude has a `RAILWAY_TOKEN`, it can:

1. **Deploy changes after validation**:
   ```bash
   make validate && make deploy
   ```

2. **Debug production issues**:
   ```bash
   make deploy-logs
   ```

3. **Run database operations**:
   ```bash
   make deploy-migrate
   make deploy-seed
   ```

4. **Manage configuration**:
   ```bash
   make deploy-env
   make deploy-env-set key=NEW_VAR value=xxx
   ```

### Production Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Auto | Set by Railway PostgreSQL addon |
| `REDIS_URL` | Auto | Set by Railway Redis addon |
| `MEILISEARCH_URL` | Yes | Meilisearch Cloud or self-hosted URL |
| `MEILISEARCH_API_KEY` | Yes | Meilisearch API key |
| `APP_ENV` | Yes | Set to `production` |
| `GITHUB_TOKEN` | Optional | For scraping GitHub data |

### Health Monitoring

- Health endpoint: `GET /health`
- Railway auto-restarts on failure
- Logs available via `make deploy-logs`

## Current Status

### What's Implemented
- [x] FastAPI application structure
- [x] Database models (Plugin, Pack, Review, User)
- [x] Basic API endpoints for plugins and packs
- [x] Search with database fallback
- [x] Plugin scraper (Anthropic + jeremylongshore sources)
- [x] Server-rendered templates with HTMX
- [x] Development tooling (make, ruff, pytest)
- [x] Docker Compose for local services
- [x] Railway deployment configuration
- [x] Production Dockerfile
- [x] CI/CD with GitHub Actions

### What's Next (PRD Priorities)
1. [ ] Seed database with scraped plugins
2. [ ] Implement Meilisearch indexing
3. [ ] Add GitHub OAuth authentication
4. [ ] Create review submission flow
5. [ ] Build pack creation UI
6. [ ] Add quality badges and scoring

## Tips for Claude

1. **Always run `make validate`** before considering work complete
2. **Check test output carefully** - fix any failures
3. **Use the scraper** to get real data when testing
4. **Templates use HTMX** - partial responses work best
5. **Database changes need migrations** - don't modify models without `make db-migration`

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [HTMX Docs](https://htmx.org/docs/)
- [PRD](./README.md) - Full product requirements
