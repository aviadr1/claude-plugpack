"""
Database configuration and session management.

Uses SQLModel (SQLAlchemy + Pydantic) for async database operations.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from plugpack.config import settings

# Determine if using SQLite (doesn't support connection pooling)
_is_sqlite = settings.database_url.startswith("sqlite")

# Engine configuration differs for SQLite vs PostgreSQL
_engine_kwargs: dict[str, Any] = {
    "echo": settings.app_debug,
    "future": True,
}

if _is_sqlite:
    # SQLite: use StaticPool for single connection, check_same_thread=False for async
    from sqlalchemy.pool import StaticPool

    _engine_kwargs["poolclass"] = StaticPool
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL: use connection pooling
    _engine_kwargs["pool_pre_ping"] = True
    _engine_kwargs["pool_size"] = 5
    _engine_kwargs["max_overflow"] = 10

# Create async engine
engine = create_async_engine(settings.database_url, **_engine_kwargs)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables.

    Note: In production, use Alembic migrations instead.
    This is useful for development and testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.

    Usage:
        async with get_session() as session:
            result = await session.execute(select(Plugin))
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes.

    Usage:
        @app.get("/plugins")
        async def list_plugins(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
