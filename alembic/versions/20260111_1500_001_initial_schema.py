"""Initial schema with all tables.

Revision ID: 001
Revises:
Create Date: 2026-01-11 15:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("github_id", sa.Integer(), nullable=False),
        sa.Column("github_username", sa.String(100), nullable=False),
        sa.Column("github_avatar_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("display_name", sa.String(100), nullable=False, server_default=""),
        sa.Column("email", sa.String(200), nullable=False, server_default=""),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_curator", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_banned", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_id"),
    )
    op.create_index("ix_users_github_id", "users", ["github_id"])

    # Plugins table
    op.create_table(
        "plugins",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False, server_default=""),
        sa.Column("version", sa.String(50), nullable=False, server_default="0.0.0"),
        sa.Column("source_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("repository_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("homepage_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("author_name", sa.String(100), nullable=False, server_default=""),
        sa.Column("author_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("category", sa.String(50), nullable=False, server_default="other"),
        sa.Column("keywords", sa.Text(), nullable=False, server_default=""),
        sa.Column("github_stars", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("github_forks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("open_issues", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_deprecated", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("maintenance_status", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("requires_api_keys", sa.Text(), nullable=False, server_default=""),
        sa.Column("requires_prerequisites", sa.Text(), nullable=False, server_default=""),
        sa.Column("claude_plan_required", sa.String(20), nullable=False, server_default="free"),
        sa.Column("commands_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("agents_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hooks_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mcp_servers_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_scraped_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_plugins_name", "plugins", ["name"])
    op.create_index("ix_plugins_slug", "plugins", ["slug"])
    op.create_index("ix_plugins_category", "plugins", ["category"])

    # Packs table
    op.create_table(
        "packs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False, server_default=""),
        sa.Column("short_description", sa.String(200), nullable=False, server_default=""),
        sa.Column("curator_name", sa.String(100), nullable=False, server_default=""),
        sa.Column("curator_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("curator_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("tags", sa.Text(), nullable=False, server_default=""),
        sa.Column("difficulty", sa.String(20), nullable=False, server_default="beginner"),
        sa.Column("estimated_setup_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("target_audience", sa.String(200), nullable=False, server_default=""),
        sa.Column("video_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("blog_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("example_repo_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("install_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_packs_slug", "packs", ["slug"])

    # Pack-Plugin junction table
    op.create_table(
        "pack_plugins",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("pack_id", sa.Uuid(), nullable=False),
        sa.Column("plugin_id", sa.Uuid(), nullable=False),
        sa.Column("phase", sa.String(100), nullable=False, server_default=""),
        sa.Column("phase_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("plugin_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.String(500), nullable=False, server_default=""),
        sa.Column("commands_to_run", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["pack_id"], ["packs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugins.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_pack_plugins_pack_id", "pack_plugins", ["pack_id"])
    op.create_index("ix_pack_plugins_plugin_id", "pack_plugins", ["plugin_id"])

    # Reviews table
    op.create_table(
        "reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.String(5000), nullable=False, server_default=""),
        sa.Column("pro_tip", sa.String(500), nullable=False, server_default=""),
        sa.Column("gotcha", sa.String(500), nullable=False, server_default=""),
        sa.Column("example_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("frameworks_used", sa.Text(), nullable=False, server_default=""),
        sa.Column("team_size", sa.String(20), nullable=False, server_default="solo"),
        sa.Column("time_saved_hours", sa.Integer(), nullable=True),
        sa.Column("plugin_id", sa.Uuid(), nullable=True),
        sa.Column("pack_id", sa.Uuid(), nullable=True),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("user_github_username", sa.String(100), nullable=False, server_default=""),
        sa.Column("helpful_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reported_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["pack_id"], ["packs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_reviews_plugin_id", "reviews", ["plugin_id"])
    op.create_index("ix_reviews_pack_id", "reviews", ["pack_id"])
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_reviews_user_id", table_name="reviews")
    op.drop_index("ix_reviews_pack_id", table_name="reviews")
    op.drop_index("ix_reviews_plugin_id", table_name="reviews")
    op.drop_table("reviews")
    op.drop_index("ix_pack_plugins_plugin_id", table_name="pack_plugins")
    op.drop_index("ix_pack_plugins_pack_id", table_name="pack_plugins")
    op.drop_table("pack_plugins")
    op.drop_table("packs")
    op.drop_index("ix_plugins_category", table_name="plugins")
    op.drop_index("ix_plugins_slug", table_name="plugins")
    op.drop_index("ix_plugins_name", table_name="plugins")
    op.drop_table("plugins")
    op.drop_index("ix_users_github_id", table_name="users")
    op.drop_table("users")
