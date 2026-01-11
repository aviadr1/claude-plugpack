"""
Pack API endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from plugpack.database import get_db
from plugpack.models import Pack, PackPlugin, PluginRead

router = APIRouter()


# =============================================================================
# Response Models
# =============================================================================


class PackPluginResponse(BaseModel):
    """Response model for a plugin within a pack."""

    plugin: PluginRead
    phase: str
    description: str
    commands_to_run: str

    model_config = {"from_attributes": True}


class PackDetailResponse(BaseModel):
    """Response model for pack detail with plugins."""

    pack: Pack
    plugins: list[PackPluginResponse]

    model_config = {"from_attributes": True}


# =============================================================================
# Helper Functions
# =============================================================================


def format_pack_plugins(pack: Pack) -> list[PackPluginResponse]:
    """Format pack plugins for response."""
    return [
        PackPluginResponse(
            plugin=pp.plugin,  # type: ignore[arg-type]
            phase=pp.phase,
            description=pp.description,
            commands_to_run=pp.commands_to_run,
        )
        for pp in sorted(pack.pack_plugins, key=lambda x: (x.phase_order, x.plugin_order))
    ]


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/")
async def list_packs(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    featured: bool | None = None,
    difficulty: str | None = None,
) -> list[Pack]:
    """List packs with filtering and pagination."""
    query = select(Pack).where(col(Pack.is_published) == True)  # noqa: E712

    # Apply filters
    if featured is not None:
        query = query.where(col(Pack.is_featured) == featured)
    if difficulty:
        query = query.where(col(Pack.difficulty) == difficulty)

    # Order by featured first, then by install count
    query = query.order_by(col(Pack.is_featured).desc(), col(Pack.install_count).desc())

    # Pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/count")
async def count_packs(
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """Get total pack count."""
    query = select(func.count(col(Pack.id))).where(col(Pack.is_published) == True)  # noqa: E712
    result = await db.execute(query)
    count = result.scalar() or 0
    return {"count": count}


@router.get("/{pack_id}")
async def get_pack(
    pack_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PackDetailResponse:
    """Get a pack by ID with its plugins."""
    query = (
        select(Pack)
        .where(col(Pack.id) == pack_id)
        .options(
            selectinload(Pack.pack_plugins).selectinload(PackPlugin.plugin)  # type: ignore[arg-type]
        )
    )
    result = await db.execute(query)
    pack = result.scalar_one_or_none()
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    return PackDetailResponse(
        pack=pack,
        plugins=format_pack_plugins(pack),
    )


@router.get("/slug/{slug}")
async def get_pack_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> PackDetailResponse:
    """Get a pack by slug with its plugins."""
    query = (
        select(Pack)
        .where(col(Pack.slug) == slug)
        .options(
            selectinload(Pack.pack_plugins).selectinload(PackPlugin.plugin)  # type: ignore[arg-type]
        )
    )
    result = await db.execute(query)
    pack = result.scalar_one_or_none()
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    return PackDetailResponse(
        pack=pack,
        plugins=format_pack_plugins(pack),
    )
