"""
Pytest configuration and fixtures.

This module provides reusable fixtures for testing the application.
Database-dependent tests use an in-memory SQLite database for speed.
"""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

# Use SQLite for testing (faster, no Docker needed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio as the async backend."""
    return "asyncio"


@pytest.fixture
async def test_engine():
    """Create a test database engine with SQLite."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )

    # Import models to register them with SQLModel metadata
    from plugpack.models import Pack, PackPlugin, Plugin, Review, User  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing the API with test database."""
    from plugpack.database import get_db
    from plugpack.main import app

    # Create a session factory for the test database
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Override the database dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_plugin_data() -> dict[str, Any]:
    """Sample plugin data for testing."""
    return {
        "name": "test-plugin",
        "slug": "test-plugin",
        "description": "A test plugin for testing purposes",
        "source_url": "https://github.com/example/test-plugin",
        "repository_url": "https://github.com/example/test-plugin",
        "author_name": "Test Author",
        "category": "testing",
        "keywords": "test,example,demo",
        "version": "1.0.0",
    }


@pytest.fixture
def sample_pack_data() -> dict[str, Any]:
    """Sample pack data for testing."""
    return {
        "name": "Test Pack",
        "slug": "test-pack",
        "description": "A test pack for testing purposes",
        "short_description": "Test pack",
        "curator_name": "Test Curator",
        "tags": "test,example",
        "difficulty": "beginner",
        "estimated_setup_minutes": 15,
        "is_published": True,
    }
