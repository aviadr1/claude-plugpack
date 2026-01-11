"""
CLI entry point for the Plugin Pack Hub.

Usage:
    plugpack serve     # Start the server
    plugpack scrape    # Run the scraper
    plugpack seed      # Seed the database
"""

import asyncio

import click
import structlog
import uvicorn

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)


@click.group()
def main() -> None:
    """Claude Plugin Pack Hub CLI."""
    pass


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(host: str, port: int, reload: bool) -> None:
    """Start the web server."""
    uvicorn.run(
        "plugpack.main:app",
        host=host,
        port=port,
        reload=reload,
    )


@main.command()
def scrape() -> None:
    """Run the plugin scraper."""
    from plugpack.scraper.run import main as scraper_main

    asyncio.run(scraper_main())


@main.command()
def seed() -> None:
    """Seed the database with sample data."""
    from plugpack.scripts.seed import main as seed_main

    asyncio.run(seed_main())


if __name__ == "__main__":
    main()
