"""
Plugin Scraper Implementation.

Fetches plugin data from various sources and enriches it with GitHub metadata.
"""

import re
from datetime import datetime
from typing import Any

import httpx
import structlog

from plugpack.config import settings
from plugpack.scraper.sources import PLUGIN_SOURCES, PluginSource, categorize_plugin

logger = structlog.get_logger()


class PluginScraper:
    """Scrapes plugin data from configured sources."""

    def __init__(self, github_token: str | None = None):
        self.github_token = github_token or settings.github_token
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Claude-Plugin-Pack-Hub/0.1.0",
                "Accept": "application/json",
            },
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.http_client.aclose()

    async def scrape_all(self) -> list[dict[str, Any]]:
        """Scrape all configured sources and return merged plugin list."""
        all_plugins: dict[str, dict[str, Any]] = {}

        for source in sorted(PLUGIN_SOURCES, key=lambda s: -s.priority):
            try:
                logger.info("Scraping source", source=source.name, url=source.url)
                plugins = await self.scrape_source(source)

                for plugin in plugins:
                    slug = plugin.get("slug", "")
                    if slug:
                        # Merge with existing, higher priority wins
                        if slug not in all_plugins:
                            all_plugins[slug] = plugin
                        else:
                            # Keep higher priority data, fill in blanks
                            for key, value in plugin.items():
                                if not all_plugins[slug].get(key):
                                    all_plugins[slug][key] = value

                logger.info("Scraped plugins", source=source.name, count=len(plugins))

            except Exception as e:
                logger.error("Failed to scrape source", source=source.name, error=str(e))

        return list(all_plugins.values())

    async def scrape_source(self, source: PluginSource) -> list[dict[str, Any]]:
        """Scrape a single source for plugins."""
        if source.source_type == "github_raw":
            return await self._scrape_github_raw(source)
        elif source.source_type == "github_api":
            return await self._scrape_github_api(source)
        else:
            raise ValueError(f"Unknown source type: {source.source_type}")

    async def _scrape_github_raw(self, source: PluginSource) -> list[dict[str, Any]]:
        """Scrape a raw JSON file from GitHub."""
        response = await self.http_client.get(source.url)
        response.raise_for_status()

        data = response.json()
        plugins = []

        # Handle different JSON structures
        if isinstance(data, list):
            raw_plugins = data
        elif isinstance(data, dict) and "plugins" in data:
            raw_plugins = data["plugins"]
        else:
            logger.warning("Unknown JSON structure", source=source.name)
            return []

        for raw in raw_plugins:
            plugin = await self._normalize_plugin(raw, source)
            if plugin:
                plugins.append(plugin)

        return plugins

    async def _scrape_github_api(self, source: PluginSource) -> list[dict[str, Any]]:
        """Scrape plugins using GitHub API."""
        # This would use the GitHub API to list plugins from source.url
        # For now, return empty - implement as needed
        logger.debug("GitHub API scraping not implemented", source=source.name)
        return []

    async def _normalize_plugin(
        self, raw: dict[str, Any], source: PluginSource
    ) -> dict[str, Any] | None:
        """Normalize a raw plugin entry to our schema."""
        try:
            name = raw.get("name", "")
            if not name:
                return None

            # Generate slug from name
            slug = self._generate_slug(name)

            # Extract description
            description = raw.get("description", "") or ""

            # Extract keywords
            keywords_raw = raw.get("keywords", [])
            if isinstance(keywords_raw, str):
                keywords = [k.strip() for k in keywords_raw.split(",")]
            else:
                keywords = keywords_raw or []

            # Auto-categorize
            category = raw.get("category", "") or categorize_plugin(name, description, keywords)

            # Build repository URL
            repo_url = ""
            if "repository" in raw:
                repo = raw["repository"]
                if isinstance(repo, str):
                    repo_url = repo
                elif isinstance(repo, dict):
                    repo_url = repo.get("url", "")

            # If source is from a GitHub raw file, try to infer repo from source path
            if not repo_url and "source" in raw:
                src = raw["source"]
                if src.startswith("./plugins/"):
                    # This is a relative path in jeremylongshore's repo
                    plugin_name = src.replace("./plugins/", "")
                    repo_url = f"https://github.com/jeremylongshore/claude-code-plugins-plus-skills/tree/main/plugins/{plugin_name}"

            # Author info
            author_raw = raw.get("author", {})
            if isinstance(author_raw, str):
                author_name = author_raw
                author_url = ""
            elif isinstance(author_raw, dict):
                author_name = author_raw.get("name", "")
                author_url = author_raw.get("url", "") or author_raw.get("homepage", "")
            else:
                author_name = ""
                author_url = ""

            return {
                "name": name,
                "slug": slug,
                "description": description[:1000] if description else "",
                "version": raw.get("version", "0.0.0"),
                "source_url": source.url,
                "repository_url": repo_url,
                "homepage_url": raw.get("homepage", "") or "",
                "author_name": author_name,
                "author_url": author_url,
                "category": category,
                "keywords": ",".join(keywords),
                "is_verified": source.is_official,
                "scraped_from": source.name,
                "scraped_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.warning("Failed to normalize plugin", raw=raw, error=str(e))
            return None

    def _generate_slug(self, name: str) -> str:
        """Generate a URL-safe slug from a plugin name."""
        # Convert to lowercase
        slug = name.lower()
        # Replace spaces and underscores with hyphens
        slug = re.sub(r"[\s_]+", "-", slug)
        # Remove non-alphanumeric characters (except hyphens)
        slug = re.sub(r"[^a-z0-9-]", "", slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r"-+", "-", slug)
        # Strip leading/trailing hyphens
        slug = slug.strip("-")
        return slug

    async def enrich_with_github(self, plugin: dict[str, Any]) -> dict[str, Any]:
        """Enrich a plugin with GitHub metadata."""
        repo_url = plugin.get("repository_url", "")
        if not repo_url or "github.com" not in repo_url:
            return plugin

        # Extract owner/repo from URL
        match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        if not match:
            return plugin

        owner, repo = match.groups()
        repo = repo.replace(".git", "").split("/")[0]  # Clean up

        try:
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self.github_token:
                headers["Authorization"] = f"Bearer {self.github_token}"

            response = await self.http_client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                plugin["github_stars"] = data.get("stargazers_count", 0)
                plugin["github_forks"] = data.get("forks_count", 0)
                plugin["open_issues"] = data.get("open_issues_count", 0)

                # Determine maintenance status from last push
                last_push = data.get("pushed_at", "")
                if last_push:
                    last_push_dt = datetime.fromisoformat(last_push.replace("Z", "+00:00"))
                    days_since_push = (datetime.now(last_push_dt.tzinfo) - last_push_dt).days

                    if days_since_push < 14:
                        plugin["maintenance_status"] = "active"
                    elif days_since_push < 90:
                        plugin["maintenance_status"] = "maintained"
                    elif days_since_push < 365:
                        plugin["maintenance_status"] = "slow"
                    else:
                        plugin["maintenance_status"] = "stale"

                logger.debug(
                    "Enriched plugin with GitHub data",
                    plugin=plugin["name"],
                    stars=plugin.get("github_stars"),
                )

        except Exception as e:
            logger.warning("Failed to enrich with GitHub", plugin=plugin["name"], error=str(e))

        return plugin


async def run_scraper() -> list[dict[str, Any]]:
    """Run the scraper and return all plugins."""
    scraper = PluginScraper()
    try:
        plugins = await scraper.scrape_all()

        # Enrich with GitHub data (rate limited)
        enriched = []
        for plugin in plugins[:50]:  # Limit to avoid rate limits
            enriched_plugin = await scraper.enrich_with_github(plugin)
            enriched.append(enriched_plugin)

        return enriched
    finally:
        await scraper.close()
