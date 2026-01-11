"""
Plugin data sources configuration.

This module defines the sources we scrape for plugin data.
Learning from competitors:
- Anthropic official: https://github.com/anthropics/claude-code
- jeremylongshore: https://github.com/jeremylongshore/claude-code-plugins-plus-skills
- claudecodeplugin.com data
"""

from dataclasses import dataclass


@dataclass
class PluginSource:
    """A source of plugin data."""

    name: str
    url: str
    source_type: str  # "github_raw", "github_api", "http_json"
    is_official: bool = False
    priority: int = 0  # Higher = more important


# Known plugin sources to scrape
# Based on PRD research of existing aggregators
PLUGIN_SOURCES = [
    # Anthropic's official marketplace.json
    PluginSource(
        name="Anthropic Official",
        url="https://raw.githubusercontent.com/anthropics/claude-code/main/.claude-plugin/marketplace.json",
        source_type="github_raw",
        is_official=True,
        priority=100,
    ),
    # Jeremy Longshore's extended marketplace
    PluginSource(
        name="Claude Code Plugins Plus Skills",
        url="https://raw.githubusercontent.com/jeremylongshore/claude-code-plugins-plus-skills/main/marketplace.extended.json",
        source_type="github_raw",
        is_official=False,
        priority=80,
    ),
    # Additional sources can be added here
]

# Categories based on jeremylongshore's classification
PLUGIN_CATEGORIES = [
    "devops",
    "testing",
    "frontend",
    "backend",
    "security",
    "ai",
    "database",
    "documentation",
    "git",
    "deployment",
    "monitoring",
    "utilities",
    "mobile",
    "cloud",
    "other",
]

# Mapping of keywords to categories (for auto-categorization)
KEYWORD_TO_CATEGORY = {
    # DevOps
    "docker": "devops",
    "kubernetes": "devops",
    "k8s": "devops",
    "ci": "devops",
    "cd": "devops",
    "pipeline": "devops",
    "terraform": "devops",
    "ansible": "devops",
    "helm": "devops",
    # Testing
    "test": "testing",
    "testing": "testing",
    "jest": "testing",
    "pytest": "testing",
    "e2e": "testing",
    "unit": "testing",
    "coverage": "testing",
    # Frontend
    "react": "frontend",
    "vue": "frontend",
    "angular": "frontend",
    "nextjs": "frontend",
    "next": "frontend",
    "tailwind": "frontend",
    "css": "frontend",
    "ui": "frontend",
    "component": "frontend",
    # Backend
    "api": "backend",
    "rest": "backend",
    "graphql": "backend",
    "fastapi": "backend",
    "django": "backend",
    "flask": "backend",
    "express": "backend",
    # Security
    "security": "security",
    "audit": "security",
    "vulnerability": "security",
    "auth": "security",
    "oauth": "security",
    # AI/ML
    "ai": "ai",
    "ml": "ai",
    "machine-learning": "ai",
    "llm": "ai",
    "agent": "ai",
    "mcp": "ai",
    # Database
    "database": "database",
    "sql": "database",
    "postgres": "database",
    "mysql": "database",
    "mongodb": "database",
    "redis": "database",
    "migration": "database",
    # Git
    "git": "git",
    "github": "git",
    "gitlab": "git",
    "commit": "git",
    "pr": "git",
    "pull-request": "git",
    # Documentation
    "doc": "documentation",
    "documentation": "documentation",
    "readme": "documentation",
    "markdown": "documentation",
    # Deployment
    "deploy": "deployment",
    "deployment": "deployment",
    "vercel": "deployment",
    "netlify": "deployment",
    "aws": "deployment",
    "gcp": "deployment",
    "azure": "deployment",
    # Mobile
    "mobile": "mobile",
    "ios": "mobile",
    "android": "mobile",
    "react-native": "mobile",
    "flutter": "mobile",
    # Cloud
    "cloud": "cloud",
    "serverless": "cloud",
    "lambda": "cloud",
    "functions": "cloud",
}


def categorize_plugin(name: str, description: str, keywords: list[str]) -> str:
    """
    Auto-categorize a plugin based on its name, description, and keywords.

    Returns the most likely category.
    """
    # Combine all text for matching
    text = f"{name} {description} {' '.join(keywords)}".lower()

    # Count matches per category
    category_scores: dict[str, int] = {}

    for keyword, category in KEYWORD_TO_CATEGORY.items():
        if keyword in text:
            category_scores[category] = category_scores.get(category, 0) + 1

    # Return category with highest score, or "other" if no matches
    if category_scores:
        return max(category_scores.items(), key=lambda x: x[1])[0]

    return "other"
