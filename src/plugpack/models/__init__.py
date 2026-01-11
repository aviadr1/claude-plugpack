"""
Database models using SQLModel.

SQLModel combines SQLAlchemy and Pydantic, giving us:
- Database ORM capabilities
- Pydantic validation
- Automatic OpenAPI schema generation
"""

from datetime import UTC, datetime
from typing import Annotated, Optional
from uuid import UUID, uuid4

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

# Type for validated URLs that get stored as strings
UrlStr = Annotated[str, Field(max_length=500)]


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(UTC)


# =============================================================================
# Base Models
# =============================================================================


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


# =============================================================================
# Plugin Models
# =============================================================================


class PluginBase(SQLModel):
    """Base fields for Plugin."""

    name: str = Field(index=True, max_length=100)
    slug: str = Field(unique=True, index=True, max_length=100)
    description: str = Field(default="", max_length=1000)
    version: str = Field(default="0.0.0", max_length=50)

    # Source info
    source_url: str = Field(default="", max_length=500)
    repository_url: str = Field(default="", max_length=500)
    homepage_url: str = Field(default="", max_length=500)

    # Author
    author_name: str = Field(default="", max_length=100)
    author_url: str = Field(default="", max_length=500)

    # Metadata
    category: str = Field(default="other", max_length=50, index=True)
    keywords: str = Field(default="")  # Comma-separated

    # Statistics from GitHub
    github_stars: int = Field(default=0)
    github_forks: int = Field(default=0)
    open_issues: int = Field(default=0)

    # Quality signals
    is_verified: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    is_deprecated: bool = Field(default=False)
    maintenance_status: str = Field(default="unknown", max_length=20)

    # Detected requirements
    requires_api_keys: str = Field(default="")  # Comma-separated
    requires_prerequisites: str = Field(default="")  # Comma-separated
    claude_plan_required: str = Field(default="free", max_length=20)

    # Components count
    commands_count: int = Field(default=0)
    agents_count: int = Field(default=0)
    hooks_count: int = Field(default=0)
    mcp_servers_count: int = Field(default=0)


class Plugin(PluginBase, TimestampMixin, table=True):
    """Plugin database model."""

    # SQLModel requires __tablename__ as string but stubs declare it as declared_attr
    # See: https://github.com/fastapi/sqlmodel/issues/98
    __tablename__ = "plugins"  # pyright: ignore[reportAssignmentType, reportIncompatibleVariableOverride]

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Relationships
    reviews: list["Review"] = Relationship(back_populates="plugin")
    pack_plugins: list["PackPlugin"] = Relationship(back_populates="plugin")

    # Last scraped
    last_scraped_at: datetime | None = Field(default=None)


class PluginRead(PluginBase):
    """Plugin response model."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    last_scraped_at: datetime | None


class PluginCreate(SQLModel):
    """Plugin creation model with URL validation."""

    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=1000)
    source_url: str = Field(max_length=500)
    repository_url: str = Field(default="", max_length=500)

    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validate slug format."""
        import re

        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        return v

    @field_validator("source_url", "repository_url", mode="before")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format if provided."""
        if not v:
            return v
        # Basic URL validation - must start with http:// or https://
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


# =============================================================================
# Pack Models
# =============================================================================


class PackBase(SQLModel):
    """Base fields for Pack."""

    name: str = Field(max_length=100)
    slug: str = Field(unique=True, index=True, max_length=100)
    description: str = Field(default="", max_length=2000)
    short_description: str = Field(default="", max_length=200)

    # Curator info
    curator_name: str = Field(default="", max_length=100)
    curator_url: str = Field(default="", max_length=500)
    curator_verified: bool = Field(default=False)

    # Metadata
    tags: str = Field(default="")  # Comma-separated
    difficulty: str = Field(default="beginner", max_length=20)
    estimated_setup_minutes: int = Field(default=30)
    target_audience: str = Field(default="", max_length=200)

    # Resources
    video_url: str = Field(default="", max_length=500)
    blog_url: str = Field(default="", max_length=500)
    example_repo_url: str = Field(default="", max_length=500)

    # Stats
    install_count: int = Field(default=0)
    is_featured: bool = Field(default=False)
    is_published: bool = Field(default=False)


class Pack(PackBase, TimestampMixin, table=True):
    """Pack database model."""

    # SQLModel requires __tablename__ as string but stubs declare it as declared_attr
    # See: https://github.com/fastapi/sqlmodel/issues/98
    __tablename__ = "packs"  # pyright: ignore[reportAssignmentType, reportIncompatibleVariableOverride]

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Relationships
    pack_plugins: list["PackPlugin"] = Relationship(back_populates="pack")
    reviews: list["Review"] = Relationship(back_populates="pack")


class PackPlugin(TimestampMixin, table=True):
    """Many-to-many relationship between Packs and Plugins."""

    # SQLModel requires __tablename__ as string but stubs declare it as declared_attr
    # See: https://github.com/fastapi/sqlmodel/issues/98
    __tablename__ = "pack_plugins"  # pyright: ignore[reportAssignmentType, reportIncompatibleVariableOverride]

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pack_id: UUID = Field(foreign_key="packs.id")
    plugin_id: UUID = Field(foreign_key="plugins.id")

    # Ordering and phases
    phase: str = Field(default="", max_length=100)
    phase_order: int = Field(default=0)
    plugin_order: int = Field(default=0)

    # Notes
    description: str = Field(default="", max_length=500)
    commands_to_run: str = Field(default="")  # Comma-separated

    # Relationships
    pack: Pack = Relationship(back_populates="pack_plugins")
    plugin: Plugin = Relationship(back_populates="pack_plugins")


# =============================================================================
# Review Models
# =============================================================================


class ReviewBase(SQLModel):
    """Base fields for Review."""

    rating: int = Field(ge=1, le=5)
    title: str = Field(max_length=200)
    body: str = Field(default="", max_length=5000)

    # Optional fields
    pro_tip: str = Field(default="", max_length=500)
    gotcha: str = Field(default="", max_length=500)
    example_url: str = Field(default="", max_length=500)

    # Usage context
    frameworks_used: str = Field(default="")  # Comma-separated
    team_size: str = Field(default="solo", max_length=20)
    time_saved_hours: int | None = Field(default=None)


class Review(ReviewBase, TimestampMixin, table=True):
    """Review database model."""

    # SQLModel requires __tablename__ as string but stubs declare it as declared_attr
    # See: https://github.com/fastapi/sqlmodel/issues/98
    __tablename__ = "reviews"  # pyright: ignore[reportAssignmentType, reportIncompatibleVariableOverride]

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign keys (one must be set)
    plugin_id: UUID | None = Field(default=None, foreign_key="plugins.id")
    pack_id: UUID | None = Field(default=None, foreign_key="packs.id")

    # User info
    user_id: UUID | None = Field(default=None, foreign_key="users.id")
    user_github_username: str = Field(default="", max_length=100)

    # Moderation
    helpful_count: int = Field(default=0)
    reported_count: int = Field(default=0)
    is_approved: bool = Field(default=True)
    is_featured: bool = Field(default=False)

    # Relationships (use Optional for SQLAlchemy compatibility)
    plugin: Optional[Plugin] = Relationship(back_populates="reviews")  # noqa: UP045
    pack: Optional[Pack] = Relationship(back_populates="reviews")  # noqa: UP045
    user: Optional["User"] = Relationship(back_populates="reviews")


# =============================================================================
# User Models
# =============================================================================


class UserBase(SQLModel):
    """Base fields for User."""

    github_id: int = Field(unique=True, index=True)
    github_username: str = Field(max_length=100)
    github_avatar_url: str = Field(default="", max_length=500)
    display_name: str = Field(default="", max_length=100)
    email: str = Field(default="", max_length=200)

    # Permissions
    is_admin: bool = Field(default=False)
    is_curator: bool = Field(default=False)
    is_banned: bool = Field(default=False)


class User(UserBase, TimestampMixin, table=True):
    """User database model."""

    # SQLModel requires __tablename__ as string but stubs declare it as declared_attr
    # See: https://github.com/fastapi/sqlmodel/issues/98
    __tablename__ = "users"  # pyright: ignore[reportAssignmentType, reportIncompatibleVariableOverride]

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Relationships
    reviews: list[Review] = Relationship(back_populates="user")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Pack",
    "PackPlugin",
    "Plugin",
    "PluginCreate",
    "PluginRead",
    "Review",
    "User",
]
