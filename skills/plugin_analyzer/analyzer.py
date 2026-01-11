#!/usr/bin/env python3
"""
Plugin Analyzer - Analyze Claude Code plugins before installation.

This module provides comprehensive plugin analysis including:
- Metadata extraction (name, version, author, description)
- Component counting (commands, agents, hooks, MCP servers)
- Dependency detection (Python, Node, API keys)
- Quality assessment (GitHub stats, maintenance status)

Usage:
    python -m skills.plugin-analyzer.analyzer https://github.com/user/plugin
    python -m skills.plugin-analyzer.analyzer /path/to/plugin
"""

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx


@dataclass
class PluginComponents:
    """Count of plugin components."""

    commands: int = 0
    agents: int = 0
    hooks: int = 0
    mcp_servers: int = 0

    def to_dict(self) -> dict:
        return {
            "commands": self.commands,
            "agents": self.agents,
            "hooks": self.hooks,
            "mcp_servers": self.mcp_servers,
        }


@dataclass
class PluginRequirements:
    """Plugin requirements and dependencies."""

    prerequisites: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    api_keys: list[str] = field(default_factory=list)
    claude_plan: str = "free"

    def to_dict(self) -> dict:
        return {
            "prerequisites": self.prerequisites,
            "dependencies": self.dependencies,
            "api_keys": self.api_keys,
            "claude_plan": self.claude_plan,
        }


@dataclass
class PluginQuality:
    """Quality metrics from GitHub."""

    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    last_commit: str = ""
    maintenance_status: str = "unknown"
    has_tests: bool = False
    has_ci: bool = False

    def to_dict(self) -> dict:
        return {
            "stars": self.stars,
            "forks": self.forks,
            "open_issues": self.open_issues,
            "last_commit": self.last_commit,
            "maintenance_status": self.maintenance_status,
            "has_tests": self.has_tests,
            "has_ci": self.has_ci,
        }


@dataclass
class PluginAnalysis:
    """Complete plugin analysis result."""

    name: str
    version: str = "unknown"
    description: str = ""
    author: str = ""
    author_url: str = ""
    repository_url: str = ""
    components: PluginComponents = field(default_factory=PluginComponents)
    requirements: PluginRequirements = field(default_factory=PluginRequirements)
    quality: PluginQuality = field(default_factory=PluginQuality)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "author_url": self.author_url,
            "repository_url": self.repository_url,
            "components": self.components.to_dict(),
            "requirements": self.requirements.to_dict(),
            "quality": self.quality.to_dict(),
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


def count_files(directory: Path, pattern: str = "*.md") -> int:
    """Count files in a directory matching the pattern."""
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


def find_files(directory: Path, pattern: str) -> list[Path]:
    """Find files in a directory matching the pattern."""
    if not directory.exists():
        return []
    return list(directory.glob(pattern))


def clone_plugin(repo_url: str) -> Path:
    """Clone a GitHub repository to a temporary directory."""
    tmpdir = tempfile.mkdtemp(prefix="plugin-analyzer-")

    # Handle tree URLs (e.g., .../tree/main/plugins/name)
    if "/tree/" in repo_url:
        parts = repo_url.split("/tree/")
        base_url = parts[0]
        path_parts = parts[1].split("/", 1)
        branch = path_parts[0]
        subpath = path_parts[1] if len(path_parts) > 1 else ""

        # Clone the whole repo
        subprocess.run(
            ["git", "clone", "--depth", "1", "-b", branch, base_url, tmpdir],
            capture_output=True,
            check=True,
        )

        # Return the subpath
        if subpath:
            return Path(tmpdir) / subpath
        return Path(tmpdir)

    # Simple clone
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, tmpdir],
        capture_output=True,
        check=True,
    )
    return Path(tmpdir)


def parse_plugin_json(plugin_path: Path) -> dict[str, Any]:
    """Parse plugin.json file."""
    plugin_json = plugin_path / "plugin.json"
    if not plugin_json.exists():
        return {}

    with plugin_json.open() as f:
        return json.load(f)


def detect_components(plugin_path: Path) -> PluginComponents:
    """Detect plugin components (commands, agents, hooks, MCP)."""
    components = PluginComponents()

    # Count commands (*.md in commands/)
    commands_dir = plugin_path / "commands"
    if commands_dir.exists():
        components.commands = count_files(commands_dir, "*.md")

    # Count agents (*.md in agents/)
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        components.agents = count_files(agents_dir, "*.md")

    # Count hooks (*.md or *.py in hooks/)
    hooks_dir = plugin_path / "hooks"
    if hooks_dir.exists():
        components.hooks = count_files(hooks_dir, "*.md") + count_files(hooks_dir, "*.py")

    # Check for MCP servers
    mcp_json = plugin_path / ".mcp.json"
    if mcp_json.exists():
        with mcp_json.open() as f:
            mcp_config = json.load(f)
            components.mcp_servers = len(mcp_config)

    return components


def detect_requirements(plugin_path: Path, components: PluginComponents) -> PluginRequirements:
    """Detect plugin requirements and dependencies."""
    requirements = PluginRequirements()

    # Check for Python requirements
    requirements_txt = plugin_path / "requirements.txt"
    if requirements_txt.exists():
        requirements.prerequisites.append("Python 3.8+")
        deps = requirements_txt.read_text().strip().split("\n")
        requirements.dependencies.extend([d.strip() for d in deps if d.strip()])

    # Check for Node dependencies
    package_json = plugin_path / "package.json"
    if package_json.exists():
        requirements.prerequisites.append("Node.js 18+")
        with package_json.open() as f:
            pkg = json.load(f)
            requirements.dependencies.extend(pkg.get("dependencies", {}).keys())

    # Check for API keys in MCP servers
    mcp_json = plugin_path / ".mcp.json"
    if mcp_json.exists():
        with mcp_json.open() as f:
            mcp_config = json.load(f)
        for server_config in mcp_config.values():
            if isinstance(server_config, dict) and "env" in server_config:
                for key in server_config["env"]:
                    if "KEY" in key.upper() or "TOKEN" in key.upper() or "SECRET" in key.upper():
                        requirements.api_keys.append(key)

    # Scan files for API key patterns
    api_key_patterns = [
        r"OPENAI[_-]?API[_-]?KEY",
        r"ANTHROPIC[_-]?API[_-]?KEY",
        r"GITHUB[_-]?TOKEN",
        r"AWS[_-]?ACCESS[_-]?KEY",
        r"GOOGLE[_-]?API[_-]?KEY",
    ]

    for file in find_files(plugin_path, "**/*"):
        if file.is_file() and file.suffix in (".md", ".json", ".py", ".js", ".ts"):
            try:
                content = file.read_text()
                for pattern in api_key_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match and match.group() not in requirements.api_keys:
                            requirements.api_keys.append(match.group())
            except UnicodeDecodeError:
                pass

    # Estimate Claude plan based on agent count
    if components.agents > 5:
        requirements.claude_plan = "max"
        requirements.prerequisites.append("Claude Max plan (6+ agents)")
    elif components.agents > 2:
        requirements.claude_plan = "pro"
        requirements.prerequisites.append("Claude Pro plan (3+ agents)")

    return requirements


def check_github_quality(repo_url: str) -> PluginQuality:
    """Check GitHub repository quality metrics."""
    quality = PluginQuality()

    # Extract owner/repo from URL
    # Handle various URL formats
    if "/tree/" in repo_url:
        repo_url = repo_url.split("/tree/")[0]

    match = re.search(r"github\.com[/:]([^/]+)/([^/.]+)", repo_url)
    if not match:
        return quality

    owner, repo = match.groups()
    repo = repo.rstrip(".git")

    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = httpx.get(api_url, timeout=10)

        if response.status_code != 200:
            return quality

        data = response.json()

        quality.stars = data.get("stargazers_count", 0)
        quality.forks = data.get("forks_count", 0)
        quality.open_issues = data.get("open_issues_count", 0)
        quality.last_commit = data.get("pushed_at", "")

        # Calculate maintenance status
        if quality.last_commit:
            last = datetime.fromisoformat(quality.last_commit.replace("Z", "+00:00"))
            days_since = (datetime.now(UTC) - last).days

            if days_since < 14:
                quality.maintenance_status = "active"
            elif days_since < 60:
                quality.maintenance_status = "maintained"
            elif days_since < 180:
                quality.maintenance_status = "slow"
            else:
                quality.maintenance_status = "stale"

    except Exception:
        pass

    return quality


def check_testing(plugin_path: Path) -> tuple[bool, bool]:
    """Check for tests and CI configuration."""
    has_tests = False
    has_ci = False

    # Check for tests
    test_patterns = ["test_*.py", "*_test.py", "tests/", "test/", "*.test.js", "*.spec.js"]
    for pattern in test_patterns:
        if find_files(plugin_path, pattern):
            has_tests = True
            break

    # Check for CI
    ci_files = [
        ".github/workflows",
        ".circleci",
        ".travis.yml",
        "Jenkinsfile",
        "azure-pipelines.yml",
    ]
    for ci in ci_files:
        if (plugin_path / ci).exists():
            has_ci = True
            break

    return has_tests, has_ci


def generate_recommendations(analysis: PluginAnalysis) -> list[str]:
    """Generate recommendations based on analysis."""
    recommendations = []

    # Documentation
    if not analysis.description:
        recommendations.append("Add a description to plugin.json")

    # Testing
    if not analysis.quality.has_tests:
        recommendations.append("Add test coverage for commands and agents")

    if not analysis.quality.has_ci:
        recommendations.append("Set up CI/CD (GitHub Actions recommended)")

    # Maintenance
    if analysis.quality.maintenance_status == "stale":
        recommendations.append("Repository hasn't been updated in 6+ months")

    # Heavy usage warning
    if analysis.components.agents > 3:
        recommendations.append(
            f"Heavy agent usage ({analysis.components.agents} agents) - monitor context consumption"
        )

    return recommendations


def analyze_plugin(plugin_url_or_path: str) -> PluginAnalysis:
    """Analyze a Claude Code plugin and return comprehensive metadata."""

    # 1. Get plugin location
    if plugin_url_or_path.startswith("http"):
        plugin_path = clone_plugin(plugin_url_or_path)
        repo_url = plugin_url_or_path
    else:
        plugin_path = Path(plugin_url_or_path)
        repo_url = ""

    # 2. Parse plugin.json
    plugin_json = parse_plugin_json(plugin_path)

    # 3. Create analysis object
    analysis = PluginAnalysis(
        name=plugin_json.get("name", plugin_path.name),
        version=plugin_json.get("version", "unknown"),
        description=plugin_json.get("description", ""),
        repository_url=repo_url,
    )

    # Extract author
    author = plugin_json.get("author", {})
    if isinstance(author, dict):
        analysis.author = author.get("name", "")
        analysis.author_url = author.get("url", "")
    elif isinstance(author, str):
        analysis.author = author

    # 4. Analyze structure
    analysis.components = detect_components(plugin_path)

    # 5. Detect dependencies
    analysis.requirements = detect_requirements(plugin_path, analysis.components)

    # 6. Check quality (if GitHub repo)
    if repo_url:
        analysis.quality = check_github_quality(repo_url)

    # 7. Check for tests and CI
    has_tests, has_ci = check_testing(plugin_path)
    analysis.quality.has_tests = has_tests
    analysis.quality.has_ci = has_ci

    # 8. Generate recommendations
    analysis.recommendations = generate_recommendations(analysis)

    return analysis


def format_as_text(analysis: PluginAnalysis) -> str:
    """Format analysis as human-readable text."""
    lines = []

    # Header
    lines.append(f"Plugin: {analysis.name}")
    lines.append(f"Version: {analysis.version}")
    if analysis.author:
        lines.append(f"Author: {analysis.author}")
    lines.append("")

    # Components
    lines.append("Components:")
    lines.append(f"  - {analysis.components.commands} command(s)")
    lines.append(f"  - {analysis.components.agents} agent(s)")
    lines.append(f"  - {analysis.components.hooks} hook(s)")
    lines.append(f"  - {analysis.components.mcp_servers} MCP server(s)")
    lines.append("")

    # Requirements
    lines.append("Requirements:")
    if analysis.requirements.prerequisites:
        for prereq in analysis.requirements.prerequisites:
            lines.append(f"  - {prereq}")
    else:
        lines.append("  - None")

    if analysis.requirements.api_keys:
        lines.append("")
        lines.append("API Keys Required:")
        for key in analysis.requirements.api_keys:
            lines.append(f"  - {key}")
    lines.append("")

    # Dependencies
    if analysis.requirements.dependencies:
        lines.append("Dependencies:")
        for dep in analysis.requirements.dependencies[:10]:  # Limit to 10
            lines.append(f"  - {dep}")
        if len(analysis.requirements.dependencies) > 10:
            lines.append(f"  - ... and {len(analysis.requirements.dependencies) - 10} more")
        lines.append("")

    # Quality
    lines.append("Quality:")
    if analysis.quality.maintenance_status != "unknown":
        status_emoji = {
            "active": "[Active]",
            "maintained": "[Maintained]",
            "slow": "[Slow Updates]",
            "stale": "[Stale]",
        }
        lines.append(
            f"  - {status_emoji.get(analysis.quality.maintenance_status, '')} {analysis.quality.maintenance_status.title()}"
        )
    if analysis.quality.stars:
        lines.append(f"  - {analysis.quality.stars} GitHub stars")
    if analysis.quality.open_issues:
        lines.append(f"  - {analysis.quality.open_issues} open issues")
    lines.append(f"  - Tests: {'Yes' if analysis.quality.has_tests else 'No'}")
    lines.append(f"  - CI: {'Yes' if analysis.quality.has_ci else 'No'}")
    lines.append("")

    # Recommendations
    if analysis.recommendations:
        lines.append("Recommendations:")
        for rec in analysis.recommendations:
            lines.append(f"  - {rec}")

    return "\n".join(lines)


def main():
    """Main entry point for CLI usage."""
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python -m skills.plugin-analyzer.analyzer <plugin-url-or-path> [--format json]"
        )
        sys.exit(1)

    plugin_url = sys.argv[1]
    output_format = "text"

    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    try:
        analysis = analyze_plugin(plugin_url)

        if output_format == "json":
            print(json.dumps(analysis.to_dict(), indent=2))
        else:
            print(format_as_text(analysis))
    except Exception as e:
        print(f"Error analyzing plugin: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
