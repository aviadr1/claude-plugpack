"""
Health check tests.

These tests verify that the application is running and responding correctly.
"""

import pytest
from httpx import AsyncClient

from plugpack import __version__


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Test the health check endpoint returns 200."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["version"] == __version__


@pytest.mark.asyncio
async def test_api_health_check(client: AsyncClient) -> None:
    """Test the API health check endpoint returns 200."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["version"] == __version__


@pytest.mark.asyncio
async def test_api_root(client: AsyncClient) -> None:
    """Test the API root endpoint."""
    response = await client.get("/api/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


@pytest.mark.asyncio
async def test_homepage(client: AsyncClient) -> None:
    """Test the homepage returns 200."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "Claude Plugin Pack Hub" in response.text


@pytest.mark.asyncio
async def test_plugins_page(client: AsyncClient) -> None:
    """Test the plugins page returns 200."""
    response = await client.get("/plugins")
    assert response.status_code == 200
    assert "Browse Plugins" in response.text


@pytest.mark.asyncio
async def test_packs_page(client: AsyncClient) -> None:
    """Test the packs page returns 200."""
    response = await client.get("/packs")
    assert response.status_code == 200
    assert "Curated Plugin Packs" in response.text
