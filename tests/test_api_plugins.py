"""
Plugin API tests.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_plugins_empty(client: AsyncClient) -> None:
    """Test listing plugins when database is empty."""
    response = await client.get("/api/plugins/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_plugin_count_empty(client: AsyncClient) -> None:
    """Test plugin count when database is empty."""
    response = await client.get("/api/plugins/count")
    assert response.status_code == 200
    assert response.json() == {"count": 0}


@pytest.mark.asyncio
async def test_list_categories_empty(client: AsyncClient) -> None:
    """Test listing categories when database is empty."""
    response = await client.get("/api/plugins/categories")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_plugin_not_found(client: AsyncClient) -> None:
    """Test getting a non-existent plugin."""
    response = await client.get("/api/plugins/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_plugin_by_slug_not_found(client: AsyncClient) -> None:
    """Test getting a non-existent plugin by slug."""
    response = await client.get("/api/plugins/slug/nonexistent")
    assert response.status_code == 404
