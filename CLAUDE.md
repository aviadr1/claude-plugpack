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

```bash
# SETUP (first time)
make setup          # Install deps, start Docker, run migrations

# DEVELOPMENT
make dev            # Start dev server at http://localhost:8000
make shell          # Open Python shell with app context

# CODE QUALITY
make lint           # Run linter
make lint-fix       # Auto-fix lint issues
make format         # Format code
make typecheck      # Run type checker
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
make scrape         # Run plugin scraper

# FULL VALIDATION
make validate       # Run all checks + tests
make ci             # Simulate CI pipeline
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

## Deployment Notes

The app is designed for easy deployment:

1. **Vercel/Railway**: Works out of the box
2. **Docker**: Can containerize with standard Python image
3. **VPS**: `uvicorn plugpack.main:app --host 0.0.0.0 --port 8000`

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
