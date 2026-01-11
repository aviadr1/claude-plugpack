"""Utility functions for static site generation."""

from datetime import UTC, datetime
from typing import Any


def format_date(date_str: str | None) -> str:
    """Format a date string for display."""
    if not date_str:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except (ValueError, AttributeError):
        return "Unknown"


def time_ago(date_str: str | None) -> str:
    """Convert a date to a human-readable 'time ago' format."""
    if not date_str:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        # Make both timezone-aware for comparison
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        now = datetime.now(UTC)
        diff = now - dt

        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            return "Just now"
    except (ValueError, AttributeError):
        return "Unknown"


def get_maintenance_badge(status: str) -> dict[str, str]:
    """Get badge styling for maintenance status."""
    badges = {
        "active": {"text": "Active", "class": "bg-green-100 text-green-800", "emoji": ""},
        "maintained": {"text": "Maintained", "class": "bg-blue-100 text-blue-800", "emoji": ""},
        "slow": {"text": "Slow Updates", "class": "bg-yellow-100 text-yellow-800", "emoji": ""},
        "stale": {"text": "Stale", "class": "bg-red-100 text-red-800", "emoji": ""},
    }
    return badges.get(
        status, {"text": "Unknown", "class": "bg-gray-100 text-gray-800", "emoji": ""}
    )


def get_category_info(category: str) -> dict[str, str]:
    """Get category display info with icon."""
    categories = {
        "development": {"icon": "code", "color": "blue"},
        "productivity": {"icon": "zap", "color": "yellow"},
        "security": {"icon": "shield", "color": "red"},
        "testing": {"icon": "check-circle", "color": "green"},
        "devops": {"icon": "server", "color": "purple"},
        "learning": {"icon": "book-open", "color": "indigo"},
        "frontend": {"icon": "layout", "color": "pink"},
        "backend": {"icon": "database", "color": "gray"},
        "ai": {"icon": "cpu", "color": "violet"},
        "git": {"icon": "git-branch", "color": "orange"},
        "documentation": {"icon": "file-text", "color": "teal"},
        "utilities": {"icon": "tool", "color": "slate"},
        "cloud": {"icon": "cloud", "color": "sky"},
        "mobile": {"icon": "smartphone", "color": "rose"},
        "monitoring": {"icon": "activity", "color": "emerald"},
        "database": {"icon": "database", "color": "amber"},
        "deployment": {"icon": "upload-cloud", "color": "cyan"},
    }
    return categories.get(category, {"icon": "box", "color": "gray"})


def format_number(n: int | None) -> str:
    """Format a number with K/M suffixes."""
    if n is None:
        return "0"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def slugify(text: str) -> str:
    """Create a URL-safe slug from text."""
    import re

    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def group_by_category(plugins: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group plugins by category."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for plugin in plugins:
        category = plugin.get("category", "other")
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(plugin)
    return grouped


def sort_plugins(plugins: list[dict[str, Any]], sort_by: str = "stars") -> list[dict[str, Any]]:
    """Sort plugins by the given criteria."""
    if sort_by == "stars":
        return sorted(plugins, key=lambda p: p.get("github_stars", 0) or 0, reverse=True)
    elif sort_by == "name":
        return sorted(plugins, key=lambda p: p.get("name", "").lower())
    elif sort_by == "recent":
        return sorted(plugins, key=lambda p: p.get("scraped_at", ""), reverse=True)
    return plugins
