"""
Pack API endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from plugpack.database import get_db
from plugpack.models import Pack, PackPlugin

router = APIRouter()


@router.get("/")
async def list_packs(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    featured: bool | None = None,
    difficulty: str | None = None,
) -> list[Pack]:
    """List packs with filtering and pagination."""
    query = select(Pack).where(Pack.is_published == True)  # noqa: E712

    # Apply filters
    if featured is not None:
        query = query.where(Pack.is_featured == featured)
    if difficulty:
        query = query.where(Pack.difficulty == difficulty)

    # Order by featured first, then by install count
    query = query.order_by(Pack.is_featured.desc(), Pack.install_count.desc())

    # Pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/count")
async def count_packs(
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """Get total pack count."""
    query = select(func.count(Pack.id)).where(Pack.is_published == True)  # noqa: E712
    result = await db.execute(query)
    count = result.scalar() or 0
    return {"count": count}


@router.get("/{pack_id}")
async def get_pack(
    pack_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a pack by ID with its plugins."""
    query = (
        select(Pack)
        .where(Pack.id == pack_id)
        .options(selectinload(Pack.pack_plugins).selectinload(PackPlugin.plugin))
    )
    result = await db.execute(query)
    pack = result.scalar_one_or_none()
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    # Format response with plugins
    plugins = []
    for pp in sorted(pack.pack_plugins, key=lambda x: (x.phase_order, x.plugin_order)):
        plugins.append(
            {
                "plugin": pp.plugin,
                "phase": pp.phase,
                "description": pp.description,
                "commands_to_run": pp.commands_to_run,
            }
        )

    return {
        "pack": pack,
        "plugins": plugins,
    }


@router.get("/slug/{slug}")
async def get_pack_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a pack by slug with its plugins."""
    query = (
        select(Pack)
        .where(Pack.slug == slug)
        .options(selectinload(Pack.pack_plugins).selectinload(PackPlugin.plugin))
    )
    result = await db.execute(query)
    pack = result.scalar_one_or_none()
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    # Format response with plugins
    plugins = []
    for pp in sorted(pack.pack_plugins, key=lambda x: (x.phase_order, x.plugin_order)):
        plugins.append(
            {
                "plugin": pp.plugin,
                "phase": pp.phase,
                "description": pp.description,
                "commands_to_run": pp.commands_to_run,
            }
        )

    return {
        "pack": pack,
        "plugins": plugins,
    }
