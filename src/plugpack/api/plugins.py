"""
Plugin API endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from plugpack.database import get_db
from plugpack.models import Plugin, PluginRead

router = APIRouter()


@router.get("/", response_model=list[PluginRead])
async def list_plugins(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = None,
    search: str | None = None,
    featured: bool | None = None,
    verified: bool | None = None,
) -> list[Plugin]:
    """List plugins with filtering and pagination."""
    query = select(Plugin)

    # Apply filters
    if category:
        query = query.where(Plugin.category == category)
    if featured is not None:
        query = query.where(Plugin.is_featured == featured)
    if verified is not None:
        query = query.where(Plugin.is_verified == verified)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Plugin.name.ilike(search_pattern))
            | (Plugin.description.ilike(search_pattern))
            | (Plugin.keywords.ilike(search_pattern))
        )

    # Order by featured first, then by stars
    query = query.order_by(Plugin.is_featured.desc(), Plugin.github_stars.desc())

    # Pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/count")
async def count_plugins(
    db: AsyncSession = Depends(get_db),
    category: str | None = None,
) -> dict[str, int]:
    """Get total plugin count."""
    query = select(func.count(Plugin.id))
    if category:
        query = query.where(Plugin.category == category)

    result = await db.execute(query)
    count = result.scalar() or 0
    return {"count": count}


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, str | int]]:
    """List all categories with counts."""
    query = select(Plugin.category, func.count(Plugin.id)).group_by(Plugin.category)
    result = await db.execute(query)
    categories = [{"name": row[0], "count": row[1]} for row in result.all()]
    return sorted(categories, key=lambda x: x["count"], reverse=True)


@router.get("/{plugin_id}", response_model=PluginRead)
async def get_plugin(
    plugin_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Plugin:
    """Get a plugin by ID."""
    result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
    plugin = result.scalar_one_or_none()
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin


@router.get("/slug/{slug}", response_model=PluginRead)
async def get_plugin_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> Plugin:
    """Get a plugin by slug."""
    result = await db.execute(select(Plugin).where(Plugin.slug == slug))
    plugin = result.scalar_one_or_none()
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin
