"""
API Routes for Claude Plugin Pack Hub.

All API routes are prefixed with /api.
"""

from fastapi import APIRouter

from plugpack.api.packs import router as packs_router
from plugpack.api.plugins import router as plugins_router
from plugpack.api.search import router as search_router

router = APIRouter()

# Include sub-routers
router.include_router(plugins_router, prefix="/plugins", tags=["plugins"])
router.include_router(packs_router, prefix="/packs", tags=["packs"])
router.include_router(search_router, prefix="/search", tags=["search"])


@router.get("/")
async def api_root() -> dict[str, str]:
    """API root endpoint."""
    return {
        "message": "Claude Plugin Pack Hub API",
        "docs": "/api/docs",
    }
