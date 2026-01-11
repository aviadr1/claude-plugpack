"""
Search API endpoints.

Uses Meilisearch for fast, typo-tolerant search.
Falls back to database search if Meilisearch is unavailable.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from plugpack.config import settings
from plugpack.database import get_db
from plugpack.models import Pack, Plugin

router = APIRouter()


async def search_database(
    db: AsyncSession,
    query: str,
    limit: int = 20,
) -> dict:
    """Fallback database search when Meilisearch is unavailable."""
    search_pattern = f"%{query}%"

    # Search plugins
    plugin_query = (
        select(Plugin)
        .where(
            (Plugin.name.ilike(search_pattern))
            | (Plugin.description.ilike(search_pattern))
            | (Plugin.keywords.ilike(search_pattern))
        )
        .order_by(Plugin.github_stars.desc())
        .limit(limit)
    )
    plugin_result = await db.execute(plugin_query)
    plugins = list(plugin_result.scalars().all())

    # Search packs
    pack_query = (
        select(Pack)
        .where(
            (Pack.is_published == True)  # noqa: E712
            & (
                (Pack.name.ilike(search_pattern))
                | (Pack.description.ilike(search_pattern))
                | (Pack.tags.ilike(search_pattern))
            )
        )
        .order_by(Pack.install_count.desc())
        .limit(limit)
    )
    pack_result = await db.execute(pack_query)
    packs = list(pack_result.scalars().all())

    return {
        "query": query,
        "plugins": plugins,
        "packs": packs,
        "total_plugins": len(plugins),
        "total_packs": len(packs),
        "search_engine": "database",
    }


async def search_meilisearch(
    query: str,
    limit: int = 20,
) -> dict | None:
    """Search using Meilisearch."""
    try:
        from meilisearch import Client

        client = Client(settings.meilisearch_url, settings.meilisearch_api_key)

        # Multi-index search
        results = client.multi_search(
            [
                {
                    "indexUid": "plugins",
                    "q": query,
                    "limit": limit,
                },
                {
                    "indexUid": "packs",
                    "q": query,
                    "limit": limit,
                },
            ]
        )

        plugins = results["results"][0]["hits"] if len(results["results"]) > 0 else []
        packs = results["results"][1]["hits"] if len(results["results"]) > 1 else []

        return {
            "query": query,
            "plugins": plugins,
            "packs": packs,
            "total_plugins": len(plugins),
            "total_packs": len(packs),
            "search_engine": "meilisearch",
        }
    except Exception:
        # Meilisearch unavailable, return None to fall back to database
        return None


@router.get("/")
async def search(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Search plugins and packs.

    Tries Meilisearch first, falls back to database search.
    """
    # Try Meilisearch first
    meilisearch_results = await search_meilisearch(q, limit)
    if meilisearch_results:
        return meilisearch_results

    # Fallback to database search
    return await search_database(db, q, limit)


@router.get("/suggest")
async def suggest(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    """Get search suggestions (autocomplete)."""
    search_pattern = f"{q}%"

    # Get plugin name suggestions
    query = (
        select(Plugin.name)
        .where(Plugin.name.ilike(search_pattern))
        .order_by(Plugin.github_stars.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    suggestions = [row[0] for row in result.all()]

    return suggestions
