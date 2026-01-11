"""
CLI script to run the plugin scraper.

Usage:
    python -m plugpack.scraper.run
    # or
    make scrape
"""

import asyncio
import json
from pathlib import Path

import structlog

from plugpack.scraper.scraper import run_scraper

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)

logger = structlog.get_logger()


async def main() -> None:
    """Run the scraper and output results."""
    logger.info("Starting plugin scraper...")

    plugins = await run_scraper()

    logger.info("Scraping complete", total_plugins=len(plugins))

    # Output to stdout as JSON
    print("\n" + "=" * 60)
    print("SCRAPED PLUGINS")
    print("=" * 60)

    for plugin in plugins:
        print(f"\n{plugin['name']} ({plugin['category']})")
        print(f"  Slug: {plugin['slug']}")
        print(f"  Description: {plugin['description'][:100]}...")
        print(f"  Source: {plugin['scraped_from']}")
        if plugin.get("github_stars"):
            print(f"  Stars: {plugin['github_stars']}")

    # Also save to file for debugging
    output_path = Path("scraped_plugins.json")
    with output_path.open("w") as f:
        json.dump(plugins, f, indent=2, default=str)

    logger.info("Results saved to scraped_plugins.json")


if __name__ == "__main__":
    asyncio.run(main())
