"""
Tests for the plugin scraper module.
"""

import pytest

from plugpack.scraper.scraper import PluginScraper
from plugpack.scraper.sources import categorize_plugin


class TestCategorizePlugin:
    """Tests for plugin categorization logic."""

    def test_categorize_devops_by_name(self):
        """Should categorize Docker plugins as devops."""
        result = categorize_plugin("docker-deploy", "Deploy containers", [])
        assert result == "devops"

    def test_categorize_devops_by_keywords(self):
        """Should categorize by CI/CD keywords."""
        result = categorize_plugin("my-plugin", "A plugin", ["ci", "cd", "pipeline"])
        assert result == "devops"

    def test_categorize_testing_by_name(self):
        """Should categorize test-related plugins as testing."""
        result = categorize_plugin("jest-runner", "Run Jest tests", [])
        assert result == "testing"

    def test_categorize_testing_by_description(self):
        """Should categorize by testing in description."""
        result = categorize_plugin("my-plugin", "Helps with unit testing", [])
        assert result == "testing"

    def test_categorize_frontend_by_name(self):
        """Should categorize React plugins as frontend."""
        result = categorize_plugin("react-helper", "React utilities", [])
        assert result == "frontend"

    def test_categorize_database_by_keywords(self):
        """Should categorize by database keywords."""
        result = categorize_plugin("db-tool", "Database helper", ["postgres", "sql"])
        assert result == "database"

    def test_categorize_security_by_name(self):
        """Should categorize security plugins."""
        result = categorize_plugin("security-scanner", "Scan for vulnerabilities", [])
        assert result == "security"

    def test_categorize_default_other(self):
        """Should default to 'other' for unknown plugins."""
        result = categorize_plugin("unknown-plugin", "Does something", [])
        assert result == "other"

    def test_categorize_ai_by_keywords(self):
        """Should categorize AI/ML plugins."""
        result = categorize_plugin("my-plugin", "Machine learning helper", ["ml", "ai"])
        assert result == "ai"


class TestPluginScraper:
    """Tests for PluginScraper class."""

    def test_generate_slug_simple(self):
        """Should generate simple slugs from names."""
        scraper = PluginScraper()
        assert scraper._generate_slug("My Plugin") == "my-plugin"

    def test_generate_slug_with_special_chars(self):
        """Should remove special characters from slugs."""
        scraper = PluginScraper()
        assert scraper._generate_slug("My@Plugin!v2") == "mypluginv2"

    def test_generate_slug_with_underscores(self):
        """Should convert underscores to hyphens."""
        scraper = PluginScraper()
        assert scraper._generate_slug("my_awesome_plugin") == "my-awesome-plugin"

    def test_generate_slug_multiple_hyphens(self):
        """Should collapse multiple hyphens."""
        scraper = PluginScraper()
        assert scraper._generate_slug("my---plugin") == "my-plugin"

    def test_generate_slug_leading_trailing_hyphens(self):
        """Should strip leading/trailing hyphens."""
        scraper = PluginScraper()
        assert scraper._generate_slug("-my-plugin-") == "my-plugin"

    @pytest.mark.asyncio
    async def test_normalize_plugin_minimal(self):
        """Should normalize plugin with minimal data."""
        from plugpack.scraper.sources import PluginSource

        scraper = PluginScraper()
        source = PluginSource(
            name="test",
            url="https://example.com",
            source_type="github_raw",
            priority=1,
            is_official=True,
        )

        raw = {"name": "Test Plugin"}
        result = await scraper._normalize_plugin(raw, source)

        assert result is not None
        assert result["name"] == "Test Plugin"
        assert result["slug"] == "test-plugin"
        assert result["is_verified"] is True
        assert result["scraped_from"] == "test"

    @pytest.mark.asyncio
    async def test_normalize_plugin_full_data(self):
        """Should normalize plugin with full data."""
        from plugpack.scraper.sources import PluginSource

        scraper = PluginScraper()
        source = PluginSource(
            name="test",
            url="https://example.com",
            source_type="github_raw",
            priority=1,
            is_official=False,
        )

        raw = {
            "name": "Full Plugin",
            "description": "A complete plugin",
            "version": "1.2.3",
            "homepage": "https://example.com",
            "repository": "https://github.com/test/plugin",
            "author": {"name": "Test Author", "url": "https://author.com"},
            "keywords": ["test", "plugin"],
        }
        result = await scraper._normalize_plugin(raw, source)

        assert result is not None
        assert result["name"] == "Full Plugin"
        assert result["description"] == "A complete plugin"
        assert result["version"] == "1.2.3"
        assert result["repository_url"] == "https://github.com/test/plugin"
        assert result["author_name"] == "Test Author"
        assert result["author_url"] == "https://author.com"
        assert "test" in result["keywords"]

    @pytest.mark.asyncio
    async def test_normalize_plugin_missing_name(self):
        """Should return None for plugins without name."""
        from plugpack.scraper.sources import PluginSource

        scraper = PluginScraper()
        source = PluginSource(
            name="test",
            url="https://example.com",
            source_type="github_raw",
            priority=1,
            is_official=False,
        )

        raw = {"description": "No name plugin"}
        result = await scraper._normalize_plugin(raw, source)

        assert result is None

    @pytest.mark.asyncio
    async def test_normalize_plugin_string_author(self):
        """Should handle string author field."""
        from plugpack.scraper.sources import PluginSource

        scraper = PluginScraper()
        source = PluginSource(
            name="test",
            url="https://example.com",
            source_type="github_raw",
            priority=1,
            is_official=False,
        )

        raw = {"name": "Test", "author": "John Doe"}
        result = await scraper._normalize_plugin(raw, source)

        assert result is not None
        assert result["author_name"] == "John Doe"
        assert result["author_url"] == ""

    @pytest.mark.asyncio
    async def test_normalize_plugin_string_repository(self):
        """Should handle string repository field."""
        from plugpack.scraper.sources import PluginSource

        scraper = PluginScraper()
        source = PluginSource(
            name="test",
            url="https://example.com",
            source_type="github_raw",
            priority=1,
            is_official=False,
        )

        raw = {"name": "Test", "repository": "https://github.com/test/repo"}
        result = await scraper._normalize_plugin(raw, source)

        assert result is not None
        assert result["repository_url"] == "https://github.com/test/repo"

    @pytest.mark.asyncio
    async def test_normalize_plugin_truncates_description(self):
        """Should truncate long descriptions."""
        from plugpack.scraper.sources import PluginSource

        scraper = PluginScraper()
        source = PluginSource(
            name="test",
            url="https://example.com",
            source_type="github_raw",
            priority=1,
            is_official=False,
        )

        raw = {"name": "Test", "description": "x" * 2000}
        result = await scraper._normalize_plugin(raw, source)

        assert result is not None
        assert len(result["description"]) == 1000
