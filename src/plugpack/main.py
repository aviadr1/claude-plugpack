"""
Claude Plugin Pack Hub - FastAPI Application

The Ultimate Directory for Claude Code Extensions.
"""

import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Request
from fastapi import Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from plugpack import __version__
from plugpack.api import router as api_router
from plugpack.config import settings
from plugpack.database import close_db, init_db

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Slug validation pattern
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$")


def validate_slug(slug: str) -> str:
    """Validate and sanitize a slug parameter."""
    if len(slug) > 100:
        slug = slug[:100]
    # Remove any potentially dangerous characters
    return re.sub(r"[^a-z0-9-]", "", slug.lower())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    if settings.is_development:
        # In development, create tables automatically
        await init_db()

    yield

    # Shutdown
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Claude Plugin Pack Hub",
    description="The Ultimate Directory for Claude Code Extensions",
    version=__version__,
    docs_url="/api/docs" if settings.app_debug else None,
    redoc_url="/api/redoc" if settings.app_debug else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup templates with auto-escaping enabled (default in Jinja2)
templates = Jinja2Templates(directory=TEMPLATES_DIR, autoescape=True)

# Include API routes
app.include_router(api_router, prefix="/api")


# Type alias for validated slug
SlugParam = Annotated[
    str, PathParam(min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
]


# =============================================================================
# Page Routes (Server-Side Rendered)
# =============================================================================


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    """Homepage with featured plugins and packs."""
    return templates.TemplateResponse(
        request,
        "pages/home.html",
        {
            "title": "Claude Plugin Pack Hub",
            "description": "Find the perfect Claude Code plugins in 5 minutes, not 5 hours",
        },
    )


@app.get("/plugins", response_class=HTMLResponse)
async def plugins_list(request: Request) -> Response:
    """Plugin listing page."""
    return templates.TemplateResponse(
        request,
        "pages/plugins.html",
        {"title": "Browse Plugins"},
    )


@app.get("/plugins/{slug}", response_class=HTMLResponse)
async def plugin_detail(request: Request, slug: SlugParam) -> Response:
    """Plugin detail page."""
    safe_slug = validate_slug(slug)
    return templates.TemplateResponse(
        request,
        "pages/plugin_detail.html",
        {"title": f"Plugin: {safe_slug}", "slug": safe_slug},
    )


@app.get("/packs", response_class=HTMLResponse)
async def packs_list(request: Request) -> Response:
    """Pack listing page."""
    return templates.TemplateResponse(
        request,
        "pages/packs.html",
        {"title": "Browse Packs"},
    )


@app.get("/packs/{slug}", response_class=HTMLResponse)
async def pack_detail(request: Request, slug: SlugParam) -> Response:
    """Pack detail page."""
    safe_slug = validate_slug(slug)
    return templates.TemplateResponse(
        request,
        "pages/pack_detail.html",
        {"title": f"Pack: {safe_slug}", "slug": safe_slug},
    )


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = "") -> Response:
    """Search results page."""
    # Sanitize search query for display
    safe_query = q[:200] if len(q) > 200 else q
    return templates.TemplateResponse(
        request,
        "pages/search.html",
        {"title": f"Search: {safe_query}" if safe_query else "Search", "query": safe_query},
    )


# =============================================================================
# Health Check
# =============================================================================


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "version": __version__}


@app.get("/api/health")
async def api_health_check() -> dict[str, str]:
    """API health check endpoint."""
    return {"status": "healthy", "version": __version__}
