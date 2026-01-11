"""
Search API tests.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_empty_query(client: AsyncClient) -> None:
    """Test search with empty query returns error."""
    response = await client.get("/api/search/?q=")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_search_no_results(client: AsyncClient) -> None:
    """Test search with no matching results."""
    response = await client.get("/api/search/?q=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert "plugins" in data
    assert "packs" in data
    assert data["total_plugins"] == 0
    assert data["total_packs"] == 0


@pytest.mark.asyncio
async def test_search_suggest_empty(client: AsyncClient) -> None:
    """Test search suggestions with no matching results."""
    response = await client.get("/api/search/suggest?q=xyz")
    assert response.status_code == 200
    assert response.json() == []
