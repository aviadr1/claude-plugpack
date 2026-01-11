"""
Database seeding script.

Seeds the database with sample data for development.

Usage:
    python -m plugpack.scripts.seed
    # or
    make db-seed
"""

import asyncio

import structlog

from plugpack.database import get_session
from plugpack.models import Pack, Plugin
from plugpack.scraper.scraper import run_scraper

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)

logger = structlog.get_logger()


async def seed_from_scraper() -> None:
    """Seed database from scraped plugin data."""
    logger.info("Running scraper to fetch plugins...")

    plugins = await run_scraper()

    logger.info("Seeding database", plugin_count=len(plugins))

    # Use get_session() context manager which auto-commits on successful exit
    async with get_session() as session:
        # Create plugin objects for bulk insert
        plugin_objects = [
            Plugin(
                name=plugin_data["name"],
                slug=plugin_data["slug"],
                description=plugin_data.get("description", ""),
                version=plugin_data.get("version", "0.0.0"),
                source_url=plugin_data.get("source_url", ""),
                repository_url=plugin_data.get("repository_url", ""),
                homepage_url=plugin_data.get("homepage_url", ""),
                author_name=plugin_data.get("author_name", ""),
                author_url=plugin_data.get("author_url", ""),
                category=plugin_data.get("category", "other"),
                keywords=plugin_data.get("keywords", ""),
                github_stars=plugin_data.get("github_stars", 0),
                github_forks=plugin_data.get("github_forks", 0),
                open_issues=plugin_data.get("open_issues", 0),
                is_verified=plugin_data.get("is_verified", False),
                maintenance_status=plugin_data.get("maintenance_status", "unknown"),
            )
            for plugin_data in plugins
        ]

        # Bulk insert all plugins
        session.add_all(plugin_objects)
        logger.debug("Added plugins for bulk insert", count=len(plugin_objects))
        # Session will auto-commit when context manager exits

    logger.info("Database seeded successfully!")


async def seed_sample_packs() -> None:
    """Seed sample packs for demo purposes."""
    logger.info("Seeding sample packs...")

    sample_packs = [
        {
            "name": "Full-Stack SaaS Starter",
            "slug": "full-stack-saas-starter",
            "description": "Everything you need to go from idea to deployed MVP in a weekend.",
            "short_description": "Complete SaaS development toolkit",
            "curator_name": "Plugin Pack Hub",
            "tags": "saas,fullstack,nextjs,supabase,vercel",
            "difficulty": "beginner",
            "estimated_setup_minutes": 30,
            "target_audience": "Solo developers building MVPs",
            "is_published": True,
            "is_featured": True,
        },
        {
            "name": "DevOps Automation Suite",
            "slug": "devops-automation-suite",
            "description": "Automate your CI/CD, Docker, and Kubernetes workflows.",
            "short_description": "Complete DevOps automation toolkit",
            "curator_name": "Plugin Pack Hub",
            "tags": "devops,cicd,docker,kubernetes",
            "difficulty": "intermediate",
            "estimated_setup_minutes": 45,
            "target_audience": "DevOps engineers and teams",
            "is_published": True,
            "is_featured": True,
        },
        {
            "name": "Security & Compliance Pack",
            "slug": "security-compliance-pack",
            "description": "Security scanning, vulnerability detection, and compliance tools.",
            "short_description": "Security-first development toolkit",
            "curator_name": "Plugin Pack Hub",
            "tags": "security,audit,compliance,vulnerability",
            "difficulty": "intermediate",
            "estimated_setup_minutes": 30,
            "target_audience": "Security-conscious teams",
            "is_published": True,
            "is_featured": True,
        },
    ]

    # Use get_session() context manager which auto-commits on successful exit
    async with get_session() as session:
        # Create pack objects for bulk insert
        pack_objects = [Pack(**pack_data) for pack_data in sample_packs]

        # Bulk insert all packs
        session.add_all(pack_objects)
        logger.debug("Added packs for bulk insert", count=len(pack_objects))
        # Session will auto-commit when context manager exits

    logger.info("Sample packs seeded!")


async def main() -> None:
    """Run all seeding operations."""
    await seed_from_scraper()
    await seed_sample_packs()
    logger.info("All seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
